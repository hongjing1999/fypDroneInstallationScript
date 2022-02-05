#!/bin/bash

apt-get update && apt-get upgrade
apt-get install gcc libpq-dev python2.7-dev python2 python3-dev python3 virtualenv python3-venv python3-wheel python3-pip python-lxml -y
curl https://bootstrap.pypa.io/pip/2.7/get-pip.py --output get-pip.py
sudo python2 get-pip.py
pip install --upgrade pip

mkdir -p /bin/fyp_drone

virtualenv --python=python2 /bin/fyp_drone/venv
. /bin/fyp_drone/venv/bin/activate
pip install -r requirements.txt

python3 -m venv /bin/fyp_drone/venv3
. /bin/fyp_drone/venv3/bin/activate
pip3 install -r requirements3.txt

cp check4G.sh /bin/fyp_drone/
cp start_camera.sh /bin/fyp_drone/
cp start_drone.sh /bin/fyp_drone/
cp server.sh /bin/fyp_drone/
cp rpi_camera.py /bin/fyp_drone/
cp server.py /bin/fyp_drone/

chmod 777 /bin/fyp_drone/start_camera.sh
chmod 777 /bin/fyp_drone/start_drone.sh
chmod 777 /bin/fyp_drone/server.sh
chmod 777 /bin/fyp_drone/check4G.sh

touch /etc/rc.local.TMP
chmod 777 /etc/rc.local.TMP
python write_rclocal.py

echo "Installed Successfully"
exit 0
