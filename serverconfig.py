from flask import Flask, request, jsonify
import configparser
import yaml
import secrets
from werkzeug.utils import secure_filename
import os

UPLOAD_FOLDER = '/home/pi/uploads/'
ALLOWED_EXTENSIONS = {'mp3', 'wav', 'wave'}
MAX_CONTENT_LENGTH = 16 * 1000 * 1000

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def map_volume(volume):
    volume = max(min(volume, 100), 0)
    mapped_volume = int(60 + volume/100*40)
    return mapped_volume

def unmap_volume(mapped_volume):
    volume = int((mapped_volume-60)/40*100)
    volume = max(min(volume, 100), 0)
    return volume

def get_balise_dict_infos():
    config = configparser.ConfigParser()
    config.read('config.ini')
    volume = int(config['INFOS']['default_volume'])
    volume = unmap_volume(volume)
    nom = config['INFOS']['nom']
    lieu = config['INFOS']['lieu']
    default_message = int(config['INFOS']['default_message'])
    print(default_message)
#    return {'balId':3434 ,'nom':nom, 'lieu':lieu, 'defaultMessage':default_message, 'volume':volume}
    with open('config.yaml') as c:
        config = yaml.load(c, Loader=yaml.SafeLoader) 
    volume = int(config['INFOS']['volume'])
    volume = unmap_volume(volume)
    nom = config['INFOS']['nom']
    lieu = config['INFOS']['lieu']
    default_message = int(config['INFOS']['default_message'])
    return {'balId':3434 ,'nom':nom, 'lieu':lieu, 'defaultMessage':default_message, 'volume':volume}


def get_annonces_dict():
    with open('config.yaml') as c:
        config = yaml.load(c, Loader=yaml.SafeLoader)
    return config["ANNONCES"]

def get_plages_dict():
    pass

def clean_unused_sounds():
    pass

@app.route('/')
def index():
    return 'Hello world'

@app.route('/infos', methods=['GET'])
def query_infos():
    try:
        return jsonify(get_balise_dict_infos()), 200
    except:
        return jsonify({'error': 'data not found'}), 204

@app.route('/volume', methods=['POST'])
def set_volume():
    try:
   #     try:
        data = request.get_json(force=True)
        print("data", data)
        volume = int(data.get("volume"))
#        except:
 #           data2 = request.get_json(force=True)
  #          volume = int(data2)
        mapped_volume = map_volume(volume)
        print("mapped = ",mapped_volume)
        config = configparser.ConfigParser()
        config.read('config.ini')
        config.set('INFOS', 'DEFAULT_VOLUME', str(mapped_volume))
        with open('config.ini', 'w') as configfile:
            config.write(configfile)
        return jsonify(get_balise_dict_infos()), 200
    except:
        return jsonify({'error':'failed to update volume'}), 400

@app.route('/infos', methods=['POST'])
def set_infos():
    try:
        data = request.get_json(force=True)
        nom = data.get("nom")
        lieu = data.get("lieu")
        config = configparser.ConfigParser()
        config.read('config.ini')
        config.set('INFOS', 'NOM', nom)
        config.set('INFOS', 'LIEU', lieu)
        with open('config.ini', 'w') as configfile:
            config.write(configfile)
        return jsonify(get_balise_dict_infos()), 200
    except:
        return jsonify({'error':'failed to update name or/and place'}), 400

@app.route('/defaultmessage', methods=['POST'])
def set_default_message():
    try:
        data = request.get_json(force=True)
        print(data)
        default_message = int(data.get("id_message"))
        config = configparser.ConfigParser()
        config.read('config.ini')
        config.set('INFOS', 'DEFAULT_MESSAGE', str(default_message))
        with open('config.ini', 'w') as configfile:
            config.write(configfile)
        return jsonify(get_balise_dict_infos()), 200
    except:
        return jsonify({'error':'failed to update default message'}), 400

@app.route('/annonces', methods=['GET'])
def get_annonces():
    return jsonify(get_annonces_dict())

@app.route('/annonce', methods=['PUT'])
def add_annonce():
    try:
        data = request.get_json(force=True)
        print(data)
        id_annonce = int(data.get("id_annonce"))
        nom = data.get("nom")
        type = data.get("type")
        filename = secrets.token_urlsafe(6) + "_" + str(id_annonce)
        contenu = data.get("contenu")
        lang = data.get("lang")
        duree = data.get("duree")
        with open('config.yaml') as c:
            config = yaml.load(c, Loader=yaml.SafeLoader)
        new_annonce = {"id_annonce":id_annonce, "nom":nom, "type":type, \
            #"filename":filename, \
            "contenu":contenu, "lang":lang, "duree":duree}
        #config["ANNONCES"].append(new_annonce)

        response_body = {"id_annonce":id_annonce, "nom":nom, "type":type, \
            "contenu":contenu, "lang":lang, "duree":duree}
        response_body.update({"upload_sound_url":"/annonce/upload_sound/" + filename})
        return jsonify(response_body), 200
    except:
        return 'oups', 400
#@app.route('/')

@app.route('/annonce/upload_sound/<string:token>', methods=['POST'])
@app.route('/annonce/upload_sound', methods=['POST'])
def upload_sound():
    if True:
        try: 
            file = request.files['audiofile']
            print("youpi")
            if file.filename == '':
                return jsonify({'error': 'failed to upload audio file'}), 400
            print(file.filename)
            if file and allowed_file(file.filename):
                print("ça avance hein")
                filename = secure_filename(file.filename)
                print(filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'audio', filename))
            return jsonify({"code":33}), 200 
        except:
            return jsonify({'error':'failed to upload audio file'}), 400
    return jsonify({'error':'failed to upload audio file'}), 403


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
