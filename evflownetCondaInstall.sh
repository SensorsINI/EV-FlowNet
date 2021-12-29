#!/bin/zsh

echo 'Creating environment'
echo yes | conda create --name evflownet tensorflow=1.10.0 python=2.7.17
echo 'Activating evflownet'
source ~/miniconda3/etc/profile.d/conda.sh
echo $PATH
conda activate evflownet
echo yes | conda install -c conda-forge ipython ipykernel
echo yes | conda install jupyter 
pip install --force-reinstall --upgrade wcwidth
pip install --upgrade pip
python -m ipykernel install --user --name evflownet --display-name evflownet
pip install opencv-python==3.4.1.15
# echo yes | conda install -c conda-forge opencv
echo yes | conda install -c conda-forge numpy
echo yes | conda install -c conda-forge ros-rospy pycryptodome pycryptodomex python-gnupg
