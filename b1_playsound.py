import numpy as np
import asyncio
from rtlsdr import RtlSdr
from playsound import playsound
from threading import Thread
import queue


def dataToBinary(data):
    data = np.abs(data)**2
    mean = np.mean(data)
    normalized = np.where(data > mean, 1, 0)
    # bin = normalized[np.where(normalized != 0)[0][0]:]
    # bin = np.append([0], bin)
    bin = normalized
    bin = bin[0::250]
    binlist = "".join(list(map(str,bin.tolist())))
    sequence = "001101010011010101010100101101001010101010101010"
    return sequence in binlist

q = queue.Queue()

def play_thread_function():
    while True:
        soundPath = q.get()
        print("POUET 🤩")
        playsound(soundPath)
        q.task_done()
        with q.mutex:
            q.queue.clear()

async def streaming():
    sdr = RtlSdr()
    # configure device
    sdr.sample_rate = 1e6
    sdr.center_freq = 868.3e6
    sdr.gain = 4
    samples_array = np.array([])

    async for samples in sdr.stream():
        # do something with samples
        # samples_array = np.append(samples_array, samples)
        # if len(samples_array) > 13665*5:
        if dataToBinary(samples):
            q.put('traitdunion.wav')
            # samples_array = np.array([])
            # break

    # to stop streaming:
    await sdr.stop()
    # done
    sdr.close()

play_thread = Thread(target=play_thread_function)
play_thread.start()
loop = asyncio.get_event_loop()
loop.run_until_complete(streaming())
q.join()
