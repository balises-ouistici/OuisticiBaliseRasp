#
# Balises Ouistici
# https://balises-ouistici.org
# Licence GPLv3
#

from mpc import *
from threading import Thread, Lock
import queue
from time import sleep, time
import yaml
from datetime import datetime
import os
from utils import get_local_ip
import requests
import json
import uuid

# generate uuid if none exists in uuid.conf
def generate_uuid():
    try:
        with open("uuid.conf", "r") as f:
            return f.read()
    except FileNotFoundError:
        new_uuid = str(uuid.uuid4())
        with open("uuid.conf", "w") as f:
            f.write(new_uuid)
        return new_uuid

# Variables configuration
CONFIG_FILE = 'config.yml'
with open(CONFIG_FILE) as c:
    configYAML = yaml.load(c, Loader=yaml.SafeLoader)
HTTP_HOST = "127.0.0.1"
HTTP_PORT_RTL433 = 8433
HTTP_PORT_SERVER = 5000
SOUNDS_FOLDER = configYAML['OPTIONS']['sounds_folder']
IP_SOUNDS_FOLDER = configYAML['OPTIONS']['ip_sounds_folder']
VOLUME = configYAML['INFOS']['volume']
AUTOVOLUME = configYAML['DEFAULT']['autovolume']
CALL_BUTTON_ENABLED = True
CALL_BUTTON = 4
NAV_BUTTON_ENABLED = False
NAV_BUTTON = 17

# Initialize MPD client
mpc_init()

def stream_events(http_host, http_port):
    url = f'http://{http_host}:{http_port}/events'
    headers = {'Accept': 'application/json'}
    # You will receive JSON events, one per line terminated with CRLF.
    # On Events and Stream endpoints a keep-alive of CRLF will be send every 60 seconds.
    response = requests.get(url, headers=headers, timeout=70, stream=True)
    print(f'Connected to {url}')
    for chunk in response.iter_content(chunk_size=None):
        yield chunk

def handle_event(line):
    try:
        # Decode the message as JSON
        data = json.loads(line)
        # print(data)
        if "model" in data and data["model"] == "ouistici":
            print("ouistici remote")
            detect()
        if "test_sound" in data and data["test_sound"] == True:
            print("ouistici test sound")
            detect()
    except KeyError:
        # Ignore unknown message data and continue
        pass
    except ValueError as e:
        # Warn on decoding errors
        print(f'Event format not recognized: {e}')

def rtl_433_listen_thread_function():
    """Listen to all messages in a loop forever."""
    while True:
        try:
            # Set gain to autolevel
            # TODO : have parameter in config.yml, add API endpoint in serverconfig.py
            #url = f'http://{HTTP_HOST}:{HTTP_PORT_RTL433}/cmd'
            #data = {'cmd': 'gain', 'arg': '0'}
            #response = requests.post(url, data=data)
            #print('gain set to autolevel',response.text)

            # Open the HTTP (chunked) streaming API of JSON events
            for chunk in stream_events(HTTP_HOST, HTTP_PORT_RTL433):
                # print(chunk)
                chunk = chunk.rstrip()
                if not chunk:
                    # filter out keep-alive empty lines
                    continue
                handle_event(chunk)
        except requests.ConnectionError:
            print('rtl_433 connection failed, retrying...')
            sleep(5)

def server_listen_thread_function():
    """Listen to all messages in a loop forever."""
    while True:
        try:
            # Open the HTTP (chunked) streaming API of JSON events
            for chunk in stream_events(HTTP_HOST, HTTP_PORT_SERVER):
                # print(chunk)
                chunk = chunk.rstrip()
                if not chunk:
                    # filter out keep-alive empty lines
                    continue
                handle_event(chunk)
        except requests.ConnectionError:
            print('server connection failed, retrying...')
            sleep(5)

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

def play_sound(soundfile):
    # update sound volume
    with open(CONFIG_FILE) as c:
        configYAML = yaml.load(c, Loader=yaml.SafeLoader)
    VOLUME = configYAML['INFOS']['volume']
    mpc_set_vol(VOLUME)
    mpc_play(soundfile)

def play_thread_function():

    while True:
        task = q.get()
        if task == "get_ip":
            play_sound(os.path.join(IP_SOUNDS_FOLDER, "bip.wav"))
            if get_local_ip(os.path.join(IP_SOUNDS_FOLDER, "ip.wav")):
                play_sound(os.path.join(IP_SOUNDS_FOLDER, "ip.wav"))
            else:
                play_sound(os.path.join(IP_SOUNDS_FOLDER, "ip_not_found.wav"))
        else:
            soundfile = sound_to_play()
            if soundfile is not None:
                play_sound(soundfile)
            else:
                play_sound(os.path.join(IP_SOUNDS_FOLDER, "bip.wav"))
        q.task_done()
        with q.mutex:
            q.queue.clear()

def detect():
    print("Ouistici !")
    q.put("ouistici")

q = queue.Queue()

play_thread = Thread(target=play_thread_function)
play_thread.start()

listen_rtl_433_thread = Thread(target=rtl_433_listen_thread_function)
listen_rtl_433_thread.start()

listen_server_thread = Thread(target=server_listen_thread_function)
listen_server_thread.start()

#
# Part exclusive to Raspberry Pi
#

try:
    import RPi.GPIO as GPIO

    if CALL_BUTTON_ENABLED:
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(CALL_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def myInterrupt(channel):
        start_time = time()
        while GPIO.input(channel) == 0: # Wait for the button up
            # pass
            sleep(0.1)
        buttonTime = time() - start_time
        print(buttonTime)
        if buttonTime >= 5:
            # long push
            print("Long Push ! Get IP !")
            q.put("get_ip")
        else:
            print("Ouistici Button !")
            q.put("ouistici button")

    if CALL_BUTTON_ENABLED:
        GPIO.add_event_detect(CALL_BUTTON, GPIO.FALLING, callback=myInterrupt, bouncetime=500 )
except:
    print("Skip Raspberry Pi part as it's not executed on this platform.")

#
# End of Raspberry Pi part
#

q.join()
