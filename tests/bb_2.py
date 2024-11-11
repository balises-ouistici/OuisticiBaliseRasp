import numpy as np
import asyncio
from rtlsdr import RtlSdr
from threading import Thread
import queue
from pygame import mixer
import numpy as np
from time import sleep

# https://gist.github.com/alimanfoo/c5977e87111abe8127453b21204c1065
def find_runs(x):
    """Find runs of consecutive items in an array."""
    # ensure array
    x = np.asanyarray(x)
    if x.ndim != 1:
        raise ValueError('only 1D array supported')
    n = x.shape[0]
    # handle empty array
    if n == 0:
        return np.array([]), np.array([]), np.array([])
    else:
        # find run starts
        loc_run_start = np.empty(n, dtype=bool)
        loc_run_start[0] = True
        np.not_equal(x[:-1], x[1:], out=loc_run_start[1:])
        run_starts = np.nonzero(loc_run_start)[0]
        # find run values
        run_values = x[loc_run_start]
        # find run lengths
        run_lengths = np.diff(np.append(run_starts, n))

        return run_values, run_lengths

def dataToBinary(data):
    data = np.abs(data)**2
    mean = np.mean(data)
    normalized = np.where(data > mean, 1, 0)
    bin = normalized[np.where(normalized != 0)[0][0]:]
    bin = np.append([0], bin)

    values, timings = find_runs(bin)
    error_rate = 0.2
    error_rate_min, error_rate_max = 1-error_rate, 1+error_rate
    data_timings = [625, 312.5, 312.5, 207.5, 207.5, 500, 500, 250, 250, 250, 250, 500, 500, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 500, 250, 250, 500, 250, 250, 500, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250]

    i = 0
    while i < len(values):
        # Check the presence of a syncword
        data = True
        if values[i] == 1:
            j = i
            for timing in data_timings:
                if (timings[j] >= (timing*error_rate_min) and \
                    timings[j] <= (timing*error_rate_max) and \
                    j<len(values)):
                    j += 1
                else:
                    data = False
                    break
            if data:
                return True
        i += 1

q = queue.Queue()

def play_thread_function():
    mixer.init()
    while True:
        soundPath = q.get()
        print("POUET 🤩")
        mixer.music.load(soundPath)
        mixer.music.play()
        while mixer.music.get_busy():
            sleep(0.2)
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
            #print("POUET 🤩")
            q.put('traitdunion.wav')
            # samples_array = np.array([])
            # break

    # to stop streaming:
    await sdr.stop()
    # done
    sdr.close()

play_thread = Thread(target=play_thread_function, daemon=True)
play_thread.start()
loop = asyncio.get_event_loop()
loop.run_until_complete(streaming())
q.join()
