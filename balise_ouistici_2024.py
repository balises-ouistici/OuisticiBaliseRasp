# Balise
from pygame import mixer
from threading import Thread
import queue
from time import sleep, time
import yaml
from datetime import datetime
import os
import alsaaudio
from utils import get_local_ip
import RPi.GPIO as GPIO
import requests
import json

import asyncio
import uuid
from bless import (  # type: ignore
    BlessServer,
    BlessGATTCharacteristic,
    GATTCharacteristicProperties,
    GATTAttributePermissions,
)

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

HTTP_HOST = "127.0.0.1"
HTTP_PORT_RTL433 = 8433
HTTP_PORT_SERVER = 5000

CONFIG_FILE = 'config.yml'
SOUNDS_FOLDER = '/home/pi/balises/media/uploads/'
IP_SOUNDS_FOLDER = '/home/pi/balises/media/ip/'

with open(CONFIG_FILE) as c:
    configYAML = yaml.load(c, Loader=yaml.SafeLoader)

VOLUME = configYAML['INFOS']['volume']
AUTOVOLUME = configYAML['DEFAULT']['autovolume']

CALL_BUTTON_ENABLED = True
CALL_BUTTON = 4
NAV_BUTTON_ENABLED = False
NAV_BUTTON = 17

if CALL_BUTTON_ENABLED:
    # GPIO.setmode(GPIO.BOARD)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(CALL_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)

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
            url = f'http://{http_host}:{http_port}/cmd'
            data = {'cmd': 'gain', 'arg': '0'}
            response = requests.post(url, data=data)
            print('gain set to autolevel',response.text)

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

# read request for the characteristic
def read_request(characteristic: BlessGATTCharacteristic, **kwargs):
    # return the value of the characteristic
    return characteristic.value

def write_request(characteristic: BlessGATTCharacteristic, value, **kwargs):
    # if 0xDEADBEEF is written to the characteristic, print "NICE"
    print(value)
    if value == b'\x93\x19\x06\x19':
        detect()

async def ble_server(loop):
    # BLE Configuration
    # Instantiate the server
    service_name= "BALISE"
    server = BlessServer(name=service_name, loop=loop)

    server.read_request_func = read_request
    server.write_request_func = write_request

    # Add Service
    ble_service_uid = generate_uuid()
    await server.add_new_service(ble_service_uid)

    # Add a Characteristic to the service
    char_uid = "01234567-89ab-cdef-0123-456789abcdef"
    char_flags = (
        GATTCharacteristicProperties.read
        | GATTCharacteristicProperties.write
        | GATTCharacteristicProperties.indicate
    )
    permissions = GATTAttributePermissions.readable | GATTAttributePermissions.writeable
    await server.add_new_characteristic(
        ble_service_uid, char_uid, char_flags, None, permissions
    )

    await server.start()
    print(f"BLE server started with service {service_name}")

def play_sound(m, mixer, soundfile):
    mixer.music.load(soundfile)
    '''
    setDefaultVolume()
    if AUTOVOLUME:
        autovolume_q.put('start')
        sleep(0.5)
        autovolume_q.put('stop')
    '''
    # update sound volume
    with open(CONFIG_FILE) as c:
        configYAML = yaml.load(c, Loader=yaml.SafeLoader)
    VOLUME = configYAML['INFOS']['volume']
    m.getvolume()
    m.setvolume(VOLUME)
    mixer.music.play()
    # vlc_command = f"vlc --play-and-exit {audio_file_path}"
    # os.system(vlc_command)
    while mixer.music.get_busy():
        sleep(0.2)

def play_thread_function():
    mixer.init()
    m = alsaaudio.Mixer('DAC')

    while True:
        task = q.get()
        if task == "get_ip":
            play_sound(m, mixer, os.path.join(IP_SOUNDS_FOLDER, "bip.wav"))
            if get_local_ip(os.path.join(IP_SOUNDS_FOLDER, "ip.wav")):
                play_sound(m, mixer, os.path.join(IP_SOUNDS_FOLDER, "ip.wav"))
            else:
                play_sound(m, mixer, os.path.join(IP_SOUNDS_FOLDER, "ip_not_found.wav"))
        else:
            soundfile = sound_to_play()
            if soundfile is not None:
                play_sound(m, mixer, soundfile)
            else:
                play_sound(m, mixer, os.path.join(IP_SOUNDS_FOLDER, "bip.wav"))
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

# non-blocking ble server start
# loop = asyncio.get_event_loop()
# loop.create_task(ble_server(loop))

'''
if AUTOVOLUME:
    autovolume_q = queue.Queue()
    autovolume_thread = Thread(target=autovolume_thread_function,args=(autovolume_q,))
    autovolume_thread.start()
'''
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

q.join()

'''
if AUTOVOLUME:
    autovolume_q.join()
'''

