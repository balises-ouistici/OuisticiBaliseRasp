# Balise
# using rtlsdr-nfs32002 lib
# pip install rtlsdr-nfs32002
import pyaudio
import numpy as np
import alsaaudio
import yaml
#from time import sleep

CHUNK = 2 ** 11
MIC_RATE = 44100 # 48000
FPS = 50
CHUNK_SIZE = int(MIC_RATE / FPS)
THRESHOLD = 300
PEAK_DECAY = 5

CONFIG_FILE = 'config.yml'

with open(CONFIG_FILE) as c:
    config = yaml.load(c, Loader=yaml.SafeLoader)
DEFAULT_VOLUME = int(config['INFOS']['volume'])
#DEFAULT_VOLUME = int(max(75, min(95, int(config['INFOS']['volume']))))

def setDefaultVolume():
    mixer = alsaaudio.Mixer('DAC')
    mixer.setvolume(DEFAULT_VOLUME)

def updateVolume(mixer, peak_max):
    volume = int(75 + (peak_max**0.5/100)*30)
    volume = int(max(75, min(95, volume)))
    mixer.setvolume(volume)
    # manage overflow (we dont care much about loosing values)

def autovolume_thread_function(autovolume_q):
    mixer = alsaaudio.Mixer('DAC')
    mixer.getvolume()
    p = pyaudio.PyAudio()
    while True:
        message = autovolume_q.get()
        autovolume_q.task_done()

        if message == 'start':
            print("START autovolume")
            stream = p.open(format=pyaudio.paInt16, \
                channels=1, \
                rate=MIC_RATE, \
                input=True, \
                frames_per_buffer=CHUNK_SIZE)
            peak_max = 0
            while True:
                # update peak_max and volume
                data = np.frombuffer(stream.read(CHUNK_SIZE), dtype=np.int16)
                peak = np.mean(np.abs(data))
                peak_max -= PEAK_DECAY
                if peak > peak_max:
                    #print(peak)
                    peak_max = peak
                if peak > THRESHOLD:
                    print("ola---")
                updateVolume(mixer,peak_max)
                #sleep(0.5)
                try:
                    message = autovolume_q.get(False)
                    autovolume_q.task_done()
                    if message == 'stop':
                        print("STOP autovolume")
                        break
                except:
                    pass
            stream.stop_stream()
            stream.close()
    p.terminate()
