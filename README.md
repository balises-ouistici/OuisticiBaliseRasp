# OuisticiBaliseRasp

## How to install OuisticiBaliseRasp

1. Install Raspberry Pi OS

You can find docs at https://www.raspberrypi.com/software/
Prefer a Pi OS Lite for fast boot.
Prefer a 2024+ version so installed Python will be version 3.11.

2. Download ouistici for rpi

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
sudo apt install rtl-sdr
sudo apt install librtlsdr-dev
```

Install rtl_433
```
apt-get install rtl-433
```
Or build, see : https://github.com/merbanan/rtl_433/blob/master/docs/BUILDING.md.

Install some tools for pygame
```
sudo apt-get install libopenblas-dev
sudo apt install libsdl2-dev
sudo apt install libsdl2-mixer-dev
```

Install Pip tool for Python
```
sudo apt install python3-pip
```

Create a virtual environnement and install Python libraries.
```
cd OuisticiBaliseRasp
python -m venv ouistici
ouistici/bin/pip install -r requirements.txt
make install
```

Refer to this doc to use the IQaudio Zero module : [module IQaudio](https://balises-ouistici.github.io/recettes/iqaudio_zero/)

Refer to this doc to get the IQaudio Zero module button to shut-down the Raspberry Pi : [bouton d'arrêt](https://balises-ouistici.github.io/recettes/configuration/#bouton-darret-halt)

4. Start

5. Use services


## Trouble shooting

Please fix the device permissions, e.g. by installing the udev rules file rtl-sdr.rules
Failed to open rtlsdr device #0.

d /etc/udev/rules.d/
samuel@raspberrypi:/etc/udev/rules.d $ sudo wget https://raw.githubusercontent.com/osmocom/rtl-sdr/refs/heads/master/rtl-sdr.rules


pygame.error: ALSA: Couldn't open audio device: Unknown error 524
alsaaudio.ALSAAudioError: Unable to find mixer control DAC,0 [default]

Try reboot


