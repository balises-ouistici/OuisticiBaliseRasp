# OuisticiBaliseRasp

A Ouistici audio beacon to use on Raspberry Pi

Main website : [balises-ouistici.org](https://balises-ouistici.org/)

Documentation : [balises-ouistici.github.io](https://balises-ouistici.github.io/)

## How to install OuisticiBaliseRasp

1. Install Raspberry Pi OS

You can find docs at https://www.raspberrypi.com/software/
Prefer a Pi OS Lite for fast boot.
Prefer a 2024+ version so installed Python will be version 3.11.

Refer to this doc to enable autoconnection to Wifi : [Connection automatique à un routeur Wifi](https://balises-ouistici.github.io/recettes/configuration/#connection-automatique-a-un-routeur-wifi)


2. Download OuisticiBaliseRasp

Install Git tool.
```
sudo apt install git
```

Dowload this repository :
```

```

3. Install dependencies

Install Rtl-Sdr tools
```
sudo apt update
sudo apt install rtl-sdr
sudo apt install librtlsdr-dev
```

Install rtl_433
```
sudo apt install rtl-433
```
Or build, see : https://github.com/merbanan/rtl_433/blob/master/docs/BUILDING.md.

Install some tools
```
# tools for Pygame
sudo apt install libopenblas-dev
sudo apt install libsdl2-dev
sudo apt install libsdl2-mixer-dev

# tools for Pyaudio
sudo apt install portaudio19-dev

# Pip for Python
sudo apt install python3-pip
```

Create a virtual environnement and install Python libraries.
```
cd OuisticiBaliseRasp
python -m venv ouistici
ouistici/bin/pip install -r requirements.txt
#make install
```

Refer to this doc to use the IQaudio Zero module : [module IQaudio](https://balises-ouistici.github.io/recettes/iqaudio_zero/)

Refer to this doc to get the IQaudio Zero module button to shut-down the Raspberry Pi : [bouton d'arrêt](https://balises-ouistici.github.io/recettes/configuration/#bouton-darret-halt)

4. Quick start 

```
# start rtl_433
rtl_433 -R 0 -c rtl_433_ouistici.conf -F http

# activate Python environnement
source ouistici/bin/activate

# start serverconfig.py
python serverconfig.py

# start balise_ouistici_2025.py
python balise_ouistici_2025.py
```

5. Use services

Copy services in `systemd` :
```
sudo cp scripts/* /lib/systemd/system/
```

Start services
```
sudo systemctl start ouistici_rtl_433.service
sudo systemctl start ouistici_server.service
sudo systemctl start ouistici.service
```

§§Enable services to ensure start at boot.


## Trouble shooting

Please fix the device permissions, e.g. by installing the udev rules file rtl-sdr.rules
Failed to open rtlsdr device #0.

d /etc/udev/rules.d/
samuel@raspberrypi:/etc/udev/rules.d $ sudo wget https://raw.githubusercontent.com/osmocom/rtl-sdr/refs/heads/master/rtl-sdr.rules


pygame.error: ALSA: Couldn't open audio device: Unknown error 524
alsaaudio.ALSAAudioError: Unable to find mixer control DAC,0 [default]

Try reboot


