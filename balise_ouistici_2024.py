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

CONFIG_FILE = 'config.yml'

with open(CONFIG_FILE) as c:
    configYAML = yaml.load(c, Loader=yaml.SafeLoader)

config = configparser.ConfigParser()
config.read('config.ini')

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
    timeslots = configYAML['TIME_SLOTS']
    for ts in timeslots:
        if day.lower() in ts and ts[day.lower()]:
            start = datetime.strptime(ts['time_start'], "%H:%M")
            end = datetime.strptime(ts['time_start'], "%H:%M")
            if start < time and time < end:
                id_annonce = ts['id_annonce']
    # get annonce and filename
    annonces = configYAML['ANNONCES']
    result = next((item for item in annonces if item["id_annonce"] == id_annonce), None)
    if result is not None and "filename" in result:
        filename = result["filename"]
    return filename


'''
if SWITCH:
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    button = int(config.get('DEFAULT', 'switch_pin')) # 4
    GPIO.setup(button, GPIO.IN, GPIO.PUD_UP)

from bb_autovolume import setDefaultVolume
if AUTOVOLUME:
    from bb_autovolume import autovolume_thread_function

sound2_index = 0
sounds2 = [SOUNDPATH_2_0, SOUNDPATH_2_1]

def set_sound(button):
    global sound2_index
    button_state = GPIO.input(button)
    if button_state == GPIO.HIGH:
        sleep(0.5)
        if GPIO.input(button) == GPIO.HIGH:
            sound2_index = 0
    else:
        sleep(0.5)
        if GPIO.input(button) == GPIO.LOW:
            sound2_index = 1
'''


def play_thread_function():
    mixer.init()
    while True:
        q.get()
        mixer.music.load(sound_to_play())
        setDefaultVolume()
        '''
        if AUTOVOLUME:
            autovolume_q.put('start')
        '''
        #sleep(PREDELAY_1)
        mixer.music.play()
        while mixer.music.get_busy():
            sleep(0.2)
        '''
        if AUTOVOLUME:
            autovolume_q.put('stop')
        '''
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
sdr.sdr.gain = 5
sdr.startDetection(callback=detect, simple_detect=True)

q.join()

'''
if AUTOVOLUME:
    autovolume_q.join()
'''

