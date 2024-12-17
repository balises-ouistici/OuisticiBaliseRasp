import netifaces
from time import sleep
# from dimits import Dimits
import subprocess

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
        # dt = Dimits("fr-siwis-low")
        # dt.text_2_audio_file(text, "welcome_ip", output_path, format="wav")
        
        # text to speech
        subprocess.run(("/home/pi/piper/piper", 
            "--model", "/home/pi/piper/voices/siwis/fr-siwis-low.onnx", 
            "--output_file", 
            str.encode(output_path)), 
            input=str.encode(text), 
            check=True)
    
    return ip

if __name__ == "__main__":
    get_local_ip("/home/pi/balises/media/ip/ip.wav")
