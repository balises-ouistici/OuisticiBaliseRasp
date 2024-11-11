import netifaces
from time import sleep
from dimits import Dimits

def get_local_ip(output_path):
    # look for local ip
    ip = None
    netifaces.interfaces()
    # ['lo', 'wlan0']
    for i in range(10):
        try:
            ip = netifaces.ifaddresses('wlan0')[2][0]['addr']
            # '192.168.30.64'
            break
        except:
            sleep(0.5)

    if ip is not None:
        # print("hello", ip)
        text = "Mon adresse i p : " + ip.replace(".", " point ")
        dt = Dimits("fr-siwis-low")
        dt.text_2_audio_file(text, "welcome_ip", output_path, format="wav")
    
    return ip