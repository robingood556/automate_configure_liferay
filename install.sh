#!/bin/bash

sudo yum install -y python3
sudo yum install -y python3-pip
sudo pip3 install --upgrade pip
sudo pip3 install -r requirements.txt
python3 demo.py $@
