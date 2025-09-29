from mpd import MPDClient
from threading import Lock


class LockableMPDClient(MPDClient):
    def __init__(self):
        super(LockableMPDClient, self).__init__()
        self._lock = Lock()

    def acquire(self):
        self._lock.acquire()

    def release(self):
        self._lock.release()

    def __enter__(self):
        self.acquire()

    def __exit__(self, type, value, traceback):
        self.release()
