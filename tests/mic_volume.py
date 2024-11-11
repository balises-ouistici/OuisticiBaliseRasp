import pyaudio
import numpy as np

import alsaaudio

CHUNK = 2 ** 11
MIC_RATE = 44100 # 48000
FPS = 50
frames_per_buffer = int(MIC_RATE / FPS)
THRESHOLD = 300
CHUNK_SIZE = frames_per_buffer

PEAK_DECAY = 10

m = alsaaudio.Mixer('DAC')
m.getvolume()

p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16, \
                channels=1, \
                rate=MIC_RATE, \
                input=True, \
                frames_per_buffer=CHUNK_SIZE)
peak_max = 0
#while len(data) < int(TIME * MIC_RATE / CHUNK_SIZE
while True:  # go for a few seconds
    data = np.frombuffer(stream.read(CHUNK), dtype=np.int16)
    peak = np.mean(np.abs(data))
    #print(peak)
    peak_max -= PEAK_DECAY
    if peak > peak_max:
        print(peak)
        peak_max = peak
        print(peak_max)
        volume = int(70 + (peak_max**0.6/100)*30)
        m.setvolume(volume)
    if peak > THRESHOLD:
        #do stuff
        print("ola---")

stream.stop_stream()
strem.close()
p.terminate()
