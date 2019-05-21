# Welcome to simple chrome dino TRex Machine Learning approach

To run code in this repo please follow this steps:
1. Obtain `python` in version 3+ (code tested on **3.6**)
1. Obtain `tmux` to detach sessions
2. Clone this repo: `git clone ssh://git@bitbucket.pearson.com/~matekrus/dino_ml.git`
3. Go to repo: `cd dino_ml`
4. Run code with `bash run_dino.sh remote|local no_env|env jupyter|script screen|no_screen`
    - `remote` run program on remote machine from config (file `env.env`)
        - you should obtain here also special `token` for jupyter site
        - log to remote machine type `jupyter notebook list` and choose proper `token`
        - second tab/window in browser reload when you run `main()` in jupyter or wait when python script run itself
    - `local` run program on local machine
    - `no_env` do not recreate virtual environment if exists
    - `env` always recreate virtual environment
    - `jupyter` run program in jupyter notebook
    - `script` run program as python script created from jupyter notebook
    - `screen` create virtual screen/display (for example when machine have no monitor)
    - `no_screen` do not create virtual screen/display
5. File `env.env` must be copied from file `env.env.example` and fill with data
6. In most case you will be used these:
    - `bash run_dino.sh local no_env jupyter no_screen`
    - `bash run_dino.sh remote no_env jupyter screen`
    - `bash run_dino.sh remote no_env script screen`
7. Program run in `tmux` sessions so **remember to kill sessions** when end work!
8. If you run remotely remember that bash script create `ssh connection` like these:
    - `ssh -N -f -L localhost:XXXX:localhost:XXXX server_username@server_ip` so please kill this connection when end work

## Run on remote server
1. Kill `ssh connection` after work with remote server
    - kill open port locally `sudo lsof -nPi -sTCP:LISTEN | grep -E '(PID|XXXX)'` remember `PID` and do `kill <PID>`
2. Kill `tmux sessions` after work
    - type `tmux ls` and kill all session with `dino_xxxxx`
    - `tmux a -t dino_xxxxx`
    - you can kill all sessions with `tmux kill-server`


## Some issues
1. If something not work
    - issue with `Xvfb`
        - on **CentOS** run `sudo yum search xvfb` and then install proper package
        - `sudo yum install python-xvfbwrapper.noarch`
    - issue with `chromedriver`
        - check name of `chromedriver` in code (Linux or MAC)
    - issue with `chrome`
        - you must install chrome on your machine
        - see tutorials in web
2. If you want see chrome by debug port run another port forwarding on local machine
    - `ssh -N -f -L localhost:9222:localhost:9222 user@remote_ip`
    - Remember to kill open port!


