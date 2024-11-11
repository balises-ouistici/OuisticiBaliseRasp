# Balise
# using rtlsdr-nfs32002 lib
# pip install rtlsdr-nfs32002
from rtlsdr_nfs32002.protocol import *
from pygame import mixer
from threading import Thread
import queue
from time import sleep
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
#GPIO.setup(4, GPIO.OUT)

button = 4
GPIO.setup(button, GPIO.IN, GPIO.PUD_UP)

sound2_index = 0
sounds2 = ['presence.wav', 'absence.wav']
ANOTHER_MESSAGE = True

def set_sound(button):
    global sound2_index
    button_state = GPIO.input(button)
    print(button_state)
    if button_state == GPIO.HIGH:
        sleep(0.5)
        if GPIO.input(button) == GPIO.HIGH:
            print("high")
            sound2_index = 0
    else:
        sleep(0.5)
        if GPIO.input(button) == GPIO.LOW:
            print("low")
            sound2_index = 1

def play_thread_function():
    mixer.init()
    while True:
        soundPath = q.get()
        mixer.music.load(soundPath)
        mixer.music.play()
        while mixer.music.get_busy():
            sleep(0.2)
        if ANOTHER_MESSAGE:
            sleep(0.2)
            mixer.music.load(sounds2[sound2_index])
            mixer.music.play()
            while mixer.music.get_busy():
                sleep(0.2)
        q.task_done()
        with q.mutex:
            q.queue.clear()

def detect():
    print("Ouistici !")
    q.put('traitdunion.wav')

q = queue.Queue()

play_thread = Thread(target=play_thread_function)
play_thread.start()

GPIO.add_event_detect(button, GPIO.BOTH, callback=set_sound)

sdr = RtlSdr_NFS32002()
sdr.sdr.gain = 4
sdr.startDetection(callback=detect)

q.join()
