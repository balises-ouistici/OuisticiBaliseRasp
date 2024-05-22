from flask import Flask, request, jsonify
import configparser
import yaml
import secrets
from werkzeug.utils import secure_filename
import os

CONFIG_FILE = 'config.yml'

UPLOAD_FOLDER = '/home/pi/uploads/'
ALLOWED_EXTENSIONS = {'mp3', 'wav', 'wave', 'tmp'}
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
    with open(CONFIG_FILE) as c:
        config = yaml.load(c, Loader=yaml.SafeLoader)
    volume = int(config['INFOS']['volume'])
    volume = unmap_volume(volume)
    nom = config['INFOS']['nom']
    lieu = config['INFOS']['lieu']
    default_message = int(config['INFOS']['default_message'])
    plages_horaires = config['INFOS']['plages_horaires']
    return {'balId':3434 ,'nom':nom, 'lieu':lieu, \
        'defaultMessage':default_message, \
        'volume':volume, \
        'plages_horaires':plages_horaires}

def get_annonces_dict():
    with open(CONFIG_FILE) as c:
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
        data = request.get_json(force=True)
        volume = int(data.get("volume"))
        mapped_volume = map_volume(volume)
        print("mapped volume = ", mapped_volume)
        # save to configfile
        with open(CONFIG_FILE) as c:
            config = yaml.load(c, Loader=yaml.SafeLoader)
        config['INFOS']['volume'] = mapped_volume
        yaml_str = yaml.dump(config, sort_keys=False, Dumper=yaml.SafeDumper)
        with open(CONFIG_FILE, "w") as c:
            yaml.dump(config, c, sort_keys=False, Dumper=yaml.SafeDumper)
        return jsonify(get_balise_dict_infos()), 200
    except:
        return jsonify({'error':'failed to update volume'}), 400

@app.route('/infos', methods=['POST'])
def set_infos():
    try:
        data = request.get_json(force=True)
        nom = data.get("nom")
        lieu = data.get("lieu")
        # save to configfile
        with open(CONFIG_FILE) as c:
            config = yaml.load(c, Loader=yaml.SafeLoader)
        config['INFOS']['nom'] = nom
        config['INFOS']['lieu'] = lieu
        with open(CONFIG_FILE, "w") as c:
            yaml.dump(config, c, sort_keys=False, Dumper=yaml.SafeDumper)
        return jsonify(get_balise_dict_infos()), 200
    except:
        return jsonify({'error':'failed to update name or/and place'}), 400

@app.route('/plages_horaires', methods=['POST'])
def set_plages_horaires():
    pass

@app.route('/defaultmessage', methods=['POST'])
def set_default_message():
    try:
        data = request.get_json(force=True)
        print(data)
        default_message = int(data.get("id_message"))
        # save to configfile
        with open(CONFIG_FILE) as c:
            config = yaml.load(c, Loader=yaml.SafeLoader)
        config['INFOS']['default_message'] = default_message
        with open(CONFIG_FILE, "w") as c:
            yaml.dump(config, c, sort_keys=False, Dumper=yaml.SafeDumper)
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
        filename = data.get("filename")
        contenu = data.get("contenu")
        lang = data.get("lang")
        duree = data.get("duree")
        with open(CONFIG_FILE) as c:
            config = yaml.load(c, Loader=yaml.SafeLoader)
        new_annonce = {"id_annonce":id_annonce, "nom":nom, "type":type, \
            "filename":filename,
            "contenu":contenu, "lang":lang, "duree":duree}
        config["ANNONCES"].append(new_annonce)
        with open(CONFIG_FILE, "w") as c:
            yaml.dump(config, c, sort_keys=False, Dumper=yaml.SafeDumper)
        response_body = new_annonce
 #       token = secrets.token_urlsafe(6) + "_" + str(id_annonce)
 #       response_body.update({"upload_sound_url":"/annonce/upload_sound/" + token})
        return jsonify(response_body), 201
    except:
        return 'oups', 400

@app.route('/annonce', methods=['POST'])
def set_annonce():
    try:
        data = request.get_json(force=True)
        print(data)
        id_annonce = int(data.get("id_annonce"))
        nom = data.get("nom")
        type = data.get("type")
        filename = data.get("filename")
        contenu = data.get("contenu")
        lang = data.get("lang")
        duree = data.get("duree")
        with open(CONFIG_FILE) as c:
            config = yaml.load(c, Loader=yaml.SafeLoader)
        annonces = config['ANNONCES']
        # get annonce from id_annonce
        index_annonce = next((i for i, item in enumerate(annonces) if item["id_annonce"] == id_annonce), None)
        if index_annonce is not None:
            updated_annonce = {"id_annonce":id_annonce, "nom":nom, "type":type, \
                "filename":filename,
                "contenu":contenu, "lang":lang, "duree":duree}
            # save to configfile
            config["ANNONCES"][index_annonce] = updated_annonce
            with open(CONFIG_FILE, "w") as c:
                yaml.dump(config, c, sort_keys=False, Dumper=yaml.SafeDumper)
            return jsonify(updated_annonce), 200
        else:
            return jsonify({'error':'annonce not found'}), 404
    except:
        return jsonify({'error':'failed to send the sound test'}), 400

@app.route('/annonce', methods=['DELETE'])
def delete_annonce():
    try:
        data = request.get_json(force=True)
        print(data)
        id_annonce = int(data.get("id_annonce"))
        with open(CONFIG_FILE) as c:
            config = yaml.load(c, Loader=yaml.SafeLoader)
        annonces = config['ANNONCES']
        # get annonce from id_annonce
        index_annonce = next((i for i, item in enumerate(annonces) if item["id_annonce"] == id_annonce), None)
        if index_annonce is not None:
            del annonces[id_annonces]
            # save to configfile
            with open(CONFIG_FILE, "w") as c:
                yaml.dump(config, c, sort_keys=False, Dumper=yaml.SafeDumper)
            return jsonify({'id_annonce':id_annonce}), 200
        else:
            return jsonify({'error':'annonce not found'}), 404
    except:
        return jsonify({'error':'failed to send the sound test'}), 400


#@app.route('/annonce/upload_sound/<string:token>', methods=['POST'])
@app.route('/annonce/upload_sound', methods=['POST'])
def upload_sound():
    if True:
        try:
            file = request.files['audiofile']
            if file.filename == '':
                return jsonify({'error': 'failed to upload audio file'}), 400
            print(file.filename)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                print(filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'audio', filename))
            return jsonify({"code":33}), 200
        except:
            return jsonify({'error':'failed to upload audio file'}), 400
    return jsonify({'error':'failed to upload audio file'}), 403

@app.route('/test_sound', methods=['GET'])
def test_balise():
    try:
        with open(CONFIG_FILE) as c:
            config = yaml.load(c, Loader=yaml.SafeLoader)
        default_message = int(config['INFOS']['default_message'])
        annonces = config['ANNONCES']
        # get annonce from default_message id
        result = next((item for item in annonces if item["id_annonce"] == default_message), None)
        # check if filename exists
        if "filename" in result:
            filename = result["filename"]
#            print(filename)
        else:
            filename = 'Balise1-0.wav'
        print(filename)
        audio_file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'audio', filename)
        volume = int(config['INFOS']['volume'])
        volume = int(volume*1024/100)
        # play sound
        if (result["type"]=="AUDIO") :
            vlc_command = f"vlc --play-and-exit {audio_file_path}"
            os.system(vlc_command)
        else :
            aplay_command = f"aplay {audio_file_path}"
            os.system(aplay_command)
        return jsonify({'success':'sound test sent'}), 200
    except:
        return jsonify({'error':'failed to send the sound test'}), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
