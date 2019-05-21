#!/bin/bash
# Simple script to create/update Lambda function for this project

set -e
SCRIPTPATH="$( cd "$(dirname "$0")" ; pwd -P )"
cd $SCRIPTPATH
. ./env.env

# Variables
VENV_FILE=./v-env/bin/activate
PORT_FILE=./port.txt
VENV_DIR=./v-env/
ENV_SCRIPT=./create_v_env.sh

MAIN_FILE=dino_neural_network
JUPYTER_FILE=$MAIN_FILE.ipynb
PYTHON_FILE=$MAIN_FILE.py

msg="Call script > bash $0 remote|local no_env|env jupyter|script screen|no_screen"


# Check 3 arg
if [[ $3 != "jupyter" ]] && [[ $3 != "script" ]]; then
    echo $msg
    exit -1
fi

# Check if screen (display) is necessary
if [[ $4 = "screen" ]]; then
    screen=true
elif [[ $4 = "no_screen" ]]; then
    screen=false
else
    echo $msg
    exit -1
fi

# Remove old env if necessary
if [[ $2 = "env" ]]; then
    rm -rf $VENV_DIR
elif [[ $2 = "no_env" ]]; then
    true
else
    echo $msg
    exit -1
fi

# Activate env (create if required)
if [ -f "$VENV_FILE" ]; then
    source $VENV_FILE
else
    bash $ENV_SCRIPT
    source $VENV_FILE
fi

# Get available socket and save to file
python3.6 -c "import socket;
tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
tcp.bind(('localhost', 0));
_, port_1 = tcp.getsockname();
tcp.close();
tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
tcp.bind(('localhost', 0));
_, port_2 = tcp.getsockname();
tcp.close();
print(port_1,port_2,end='');" > $PORT_FILE


# Check where run dino
if [[ $1 = "local" ]]; then
    local_run=true
    IFS=\  read jupyter_port debugger_port <<< $(<$PORT_FILE)
    if [[ $3 = "jupyter" ]]; then
        tmux new -d -s dino_$jupyter_port
        tmux send -t dino_$jupyter_port . Space deactivate ENTER
        tmux send -t dino_$jupyter_port . Space $VENV_FILE ENTER
        tmux send -t dino_$jupyter_port \
            screen=$screen Space \
            jupyter_port=$jupyter_port Space \
            debugger_port=$debugger_port Space \
            jupyter Space \
            notebook Space \
            --port Space \
            $jupyter_port Space \
            $JUPYTER_FILE ENTER
    elif [[ $3 = "script" ]]; then
        jupyter nbconvert --to script $JUPYTER_FILE
        tmux new -d -s dino_$jupyter_port
        tmux send -t dino_$jupyter_port . Space deactivate ENTER
        tmux send -t dino_$jupyter_port . Space $VENV_FILE ENTER
        tmux send -t dino_$jupyter_port \
            screen=$screen Space \
            jupyter_port=$jupyter_port Space \
            debugger_port=$debugger_port Space \
            python3.6 Space \
            $PYTHON_FILE ENTER
    else
        echo $msg
        exit -1
    fi
elif [[ $1 = "remote" ]]; then
    local_run=false
    rsync -v -v -azh --progress --cvs-exclude --exclude 'v-env*' --exclude '.git*' --exclude '.ipynb_checkpoints*' ./ $server_username@$server_ip:$server_path

    ssh $server_username@$server_ip "cd $server_path && bash $0 local $2 $3 $4"
    IFS=\  read r_jupyter_port r_debugger_port <<< $(scp $server_username@$server_ip:$server_path/$PORT_FILE /dev/stdout)
    if [[ $3 = "jupyter" ]]; then
        ssh -N -f -L localhost:$r_jupyter_port:localhost:$r_jupyter_port $server_username@$server_ip
    fi
    ssh -N -f -L localhost:$r_debugger_port:localhost:$r_debugger_port $server_username@$server_ip
    sleep 3
    open http://localhost:$r_jupyter_port
    open http://localhost:$r_debugger_port
else
    echo $msg
    exit -1
fi