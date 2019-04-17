# Simple bash script to recreate env for this repository
# Activate env by typing
#
# source ./v-env/bin/activate
#
rm -rf ./v-env
virtualenv -p python3 v-env
. ./v-env/bin/activate

pip install --upgrade pip
pip install --compile \
jupyter==1.0.0 \
selenium==3.141.0 \
mss==4.0.2 \
numpy==1.16.2 \
image==1.5.27 \
sklearn==0.0 \
keras==2.2.4 \
tensorflow==1.13.1 \
pyvirtualdisplay==0.2.1

cp ./special_files/tensorflow_backend.py ./v-env/lib/python3.6/site-packages/keras/backend
cp ./special_files/training_arrays.py ./v-env/lib/python3.6/site-packages/keras/engine
cp ./special_files/training_utils.py ./v-env/lib/python3.6/site-packages/keras/engine
