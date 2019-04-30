# Welcome to simple chrome dino TRex Machine Learning approach

To run code in this repo please follow this steps:
1. Obtain `python` in version 3+ (code tested on **3.6**)
2. Install **virtualenv**: `pip install virtualenv`
2. Clone this repo: `git clone ssh://git@bitbucket.pearson.com/~matekrus/dino_ml.git`
3. Go to repo: `cd dino_ml`
4. Create virtual environment for code: `bash ./create_v_env.sh`
5. Run **jupyter notebook**: `bash ./run_dino`
6. Choose proper notebook with version of dino
    - dino_neural_network.ipynb

## Run on remote server
1. Copy repo to remote server and create virtual environment there
2. Activate v-env
3. Run jupyter `jupyter notebook --no-browser --port=8889`
4. Local on your machine run port forwarding: `ssh -N -f -L localhost:8889:localhost:8889 user@remote_ip`
    - after work kill jupyter notebook on server
    - kill open port locally `sudo lsof -nPi -sTCP:LISTEN | grep -E '(PID|8889)'` remember `PID` and do `kill <PID>`
5. If something not work
    - issue with `Xvfb`
        - on **CentOS** run `sudo yum search xvfb` and then install proper package
        - `sudo yum install python-xvfbwrapper.noarch`
    - issue with `chromedriver`
        - check name of `chromedriver` in code (Linux or MAC)
    - issue with `chrome`
        - you must install chrome on your machine
        - see tutorials in web
6. If you want see chrome by debug port run another port forwarding on local machine
    - `ssh -N -f -L localhost:9222:localhost:9222 user@remote_ip`
    - Remember to kill open port!

### Useful commands
`rsync -azh --del --progress --cvs-exclude ./ user@remote_ip:~/dino`

