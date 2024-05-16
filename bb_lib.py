# Balise
# using rtlsdr-nfs32002 lib
# pip install rtlsdr-nfs32002
from rtlsdr_nfs32002.protocol import *
from pygame import mixer
from threading import Thread
import queue
from time import sleep

q = queue.Queue()

def play_thread_function():
    mixer.init()
    while True:
        soundPath = q.get()
        mixer.music.load(soundPath)
        mixer.music.play()
        while mixer.music.get_busy():
            sleep(0.2)
        q.task_done()
        with q.mutex:
            q.queue.clear()

def detect():
    print("Ouistici !")
    q.put('traitdunion.wav')

play_thread = Thread(target=play_thread_function)
play_thread.start()

sdr = RtlSdr_NFS32002()
#sdr.sdr.gain = 4
sdr.startDetection(callback=detect)

q.join()
