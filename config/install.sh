#!/bin/bash

sudo apt install -y git
git clone https://github.com/balises-ouistici/OuisticiBaliseRasp
cd OuisticiBaliseRasp
git checkout Rpi-jeremy
sudo make install.rpi
