from mpd import MPDClient

mpc = MPDClient()

def mpc_connect():
    mpc.connect("localhost", 6600)
    mpc.update()

def mpc_disconnect(mpc):
    mpc.close()
    mpc.disconnect()

def mpc_init():
    mpc_connect()
    mpc.consume(1)
    mpc_disconnect(mpc)

def mpc_play(filename):
    mpc_connect()
    mpc.add(filename)
    mpc.play()
    mpc_disconnect(mpc)

def mpc_set_vol(volume):
    mpc_connect()
    mpc.setvol(volume)
    mpc_disconnect(mpc)
