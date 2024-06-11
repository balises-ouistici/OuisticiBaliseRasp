# Balise
# using rtlsdr-nfs32002 lib
# pip install rtlsdr-nfs32002
#import sys
#sys.path.append('/home/pi/balises/rtlsdr')
from rtlsdr_nfs32002.protocol import *
from pygame import mixer
from threading import Thread
import queue
from time import sleep
import configparser
import yaml
from datetime import datetime
import os
import alsaaudio


CONFIG_FILE = 'config.yml'
SOUNDS_FOLDER = '/home/pi/uploads/audio/'

RTLSDR_GAIN = 1.2

with open(CONFIG_FILE) as c:
    configYAML = yaml.load(c, Loader=yaml.SafeLoader)

config = configparser.ConfigParser()
config.read('config.ini')
VOLUME = config['INFOS']['volume']


'''
AUTOVOLUME = configYAML['DEFAULT']['autovolume']
ANOTHER_MESSAGE = config.get('DEFAULT', 'second_message') == 'true'
SWITCH = config.get('DEFAULT', 'second_message_switch') == 'true'
'''

def sound_to_play():
    # get time
    now = datetime.now()
    day = now.strftime('%A')
    time = now.time()
    # default annonce to play
    id_annonce = configYAML['INFOS']['default_message']
    # check annonce to play from timeslots
    if configYAML['INFOS']['timeslots']:
        timeslots = configYAML['TIME_SLOTS']
        for ts in timeslots:
            if day.lower() in ts and ts[day.lower()]:
                start = datetime.strptime(ts['time_start'], "%H:%M").time()
                end = datetime.strptime(ts['time_start'], "%H:%M").time()
                if start < time and time < end:
                    id_annonce = ts['id_annonce']
    # get annonce and filename
    filename = None
    annonces = configYAML['ANNONCES']
    result = next((item for item in annonces if item["id_annonce"] == id_annonce), None)
    if result is not None and "filename" in result:
        filename = result["filename"]
        filename = os.path.join(SOUNDS_FOLDER, filename)

    print(filename)
    return filename


def play_thread_function():
    mixer.init()
    m = alsaaudio.Mixer('DAC')
    while True:
        q.get()
        soundfile = sound_to_play()
        if soundfile is not None:
            mixer.music.load(soundfile)
            '''
            setDefaultVolume()
            if AUTOVOLUME:
                autovolume_q.put('start')
                sleep(0.5)
                autovolume_q.put('stop')
            '''
            m.getvolume()
            m.setvolume(volume)

            mixer.music.play()
 #           vlc_command = f"vlc --play-and-exit {audio_file_path}"
#            os.system(vlc_command)
            while mixer.music.get_busy():
                sleep(0.2)
        q.task_done()
        with q.mutex:
            q.queue.clear()

def detect():
    print("Ouistici !")
    q.put("Ouistici !")

q = queue.Queue()

play_thread = Thread(target=play_thread_function)
play_thread.start()

'''
if AUTOVOLUME:
    autovolume_q = queue.Queue()
    autovolume_thread = Thread(target=autovolume_thread_function,args=(autovolume_q,))
    autovolume_thread.start()

if SWITCH: 
    GPIO.add_event_detect(button, GPIO.BOTH, callback=set_sound)
'''


sdr = RtlSdr_NFS32002()
sdr.sdr.gain = RTLSDR_GAIN
sdr.startDetection(callback=detect, simple_detect=True)

q.join()

'''
if AUTOVOLUME:
    autovolume_q.join()
'''

