from flask import Flask
import configparser

app = Flask(__name__)

@app.route('/')
def index():
    return 'Hello world'

@app.route('/volume/<int:value>')
def vol(value):
    try:
        volume = int(value)
        volume = max(min(volume, 100), 60)
    except:
        volume = 70
    config = configparser.ConfigParser()
    config.read('config.ini')
    config.set('DEFAULT', 'DEFAULT_VOLUME', str(volume))
    with open('config.ini', 'w') as configfile:
        config.write(configfile)

    return f'volume set to {volume}'

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0') 
