import netifaces
from time import sleep
import uuid
from espeakng import Speaker


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


def get_local_ip(output_path):
    # look for local ip
    ip = None
    netifaces.interfaces()
    # ['lo', 'wlan0']
    for i in range(10):
        try:
            ip = netifaces.ifaddresses("wlan0")[2][0]["addr"]
            # '192.168.30.64'
            break
        except:
            sleep(0.5)

    if ip is not None:
        text = "Mon adresse IP : " + ip.replace(".", " point ")
        speaker = Speaker()
        speaker.voice = "fr"
        speaker.say(text, export_path=str.encode(output_path))

    return ip


if __name__ == "__main__":
    get_local_ip("media/ip/ip.wav")
