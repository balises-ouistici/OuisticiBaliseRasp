# Balise
# using rtlsdr-nfs32002 lib
# pip install rtlsdr-nfs32002
#import sys
#sys.path.append('/home/pi/balises/rtlsdr')
from rtlsdr_nfs32002.protocol import RtlSdr_NFS32002
from pygame import mixer
from threading import Thread
import queue
from time import sleep
import yaml
from datetime import datetime
import os
import alsaaudio

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

CONFIG_FILE = 'config.yml'
SOUNDS_FOLDER = '/home/pi/balises/media/uploads/'

RTLSDR_GAIN = 0.5

with open(CONFIG_FILE) as c:
    configYAML = yaml.load(c, Loader=yaml.SafeLoader)

VOLUME = configYAML['INFOS']['volume']
AUTOVOLUME = configYAML['DEFAULT']['autovolume']

CALL_BUTTON_ENABLED = True
CALL_BUTTON = 5
NAV_BUTTON_ENABLED = False
NAV_BUTTON = 6

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

        q.task_done()
        with q.mutex:
            q.queue.clear()

def detect():
    print("Ouistici !")
    q.put("Ouistici !")

q = queue.Queue()

play_thread = Thread(target=play_thread_function)
play_thread.start()

# non-blocking ble server start
loop = asyncio.get_event_loop()
loop.create_task(ble_server(loop))

'''
if AUTOVOLUME:
    autovolume_q = queue.Queue()
    autovolume_thread = Thread(target=autovolume_thread_function,args=(autovolume_q,))
    autovolume_thread.start()

if SWITCH: 
    GPIO.add_event_detect(button, GPIO.BOTH, callback=set_sound)
'''


sdr = RtlSdr_NFS32002()
# sdr.setManualGain(RTLSDR_GAIN)
sdr.setAutomaticGain()
sdr.startDetection(callback=detect, error_rate = 0.2, simple_detect=False)

q.join()

'''
if AUTOVOLUME:
    autovolume_q.join()
'''

