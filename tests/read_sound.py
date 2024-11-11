from pygame import mixer
import alsaaudio
import yaml
# import configparser

# config = configparser.ConfigParser()
# config.read('config.ini')
# DEFAULT_VOLUME = int(config['DEFAULT']['default_volume'])

def unmap_volume(mapped_volume):
    volume = int((mapped_volume-60)/40*100)
    volume = max(min(volume, 100), 0)
    return volume

CONFIG_FILE = 'config.yml'

with open(CONFIG_FILE) as c:
    config = yaml.load(c, Loader=yaml.SafeLoader)
volume = int(config['INFOS']['volume'])
volume = unmap_volume(volume)



mixer.init()
audiopath = "/home/pi/uploads/audio/1.wav"
mixer.music.load(audiopath)



def setVolumeDefault():
    m = alsaaudio.Mixer('DAC')
    m.getvolume()
    m.setvolume(volume)

def play():
    print("start")
    mixer.music.play()
    while mixer.music.get_busy() == True:
        continue
    print("end")

setVolumeDefault()
play()
