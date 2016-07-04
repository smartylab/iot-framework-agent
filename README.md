# Installation #
## Environment ##
* OS: Ubuntu 16.04
* Platform: Python 3.5

## Linux Dependencies ##

### Bluetooth ###
* sudo apt install python-dev bluetooth libbluetooth-dev

### PyGame ###
* sudo apt-get install mercurial python3-dev python3-numpy libav-tools \
    libsdl-image1.2-dev libsdl-mixer1.2-dev libsdl-ttf2.0-dev libsmpeg-dev \
    libsdl1.2-dev  libportmidi-dev libswscale-dev libavformat-dev libavcodec-dev
 
* hg clone https://bitbucket.org/pygame/pygame
 
* cd pygame
* python3 setup.py build
* sudo python3 setup.py install

## Python Dependencies ##
* sudo pip install pyserial netifaces oauth2 pybluez requests flask