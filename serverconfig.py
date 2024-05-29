from flask import Flask, request, jsonify, send_from_directory
import configparser
import yaml
import secrets
from werkzeug.utils import secure_filename
import os
import alsaaudio


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
    balise = config["INFOS"]
    balise.update({"volume":volume})
    print(balise)
    return balise

def get_balise_dict():
    with open(CONFIG_FILE) as c:
        config = yaml.load(c, Loader=yaml.SafeLoader)
    volume = int(config['INFOS']['volume'])
    volume = unmap_volume(volume)
    balise = config["INFOS"]
    balise.update({"volume":volume})
    annonces = config["ANNONCES"]
    timeslots = config["TIME_SLOTS"]
    return {"balise":balise, "annonces":annonces, "timeslots":timeslots}

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

@app.route('/balise', methods=['GET'])
def query_infos():
    try:
        return jsonify(get_balise_dict()), 200
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



@app.route('/plages_horaire', methods=['POST'])
def set_plages_horaire():
    try:
        data = request.get_json(force=True)
        print(data)
        plages_horaire = data.get("plages_horaire")
        # save to configfile
        with open(CONFIG_FILE) as c:
            config = yaml.load(c, Loader=yaml.SafeLoader)
        config['INFOS']['plages_horaire'] = plages_horaire
        with open(CONFIG_FILE, "w") as c:
            yaml.dump(config, c, sort_keys=False, Dumper=yaml.SafeDumper)
        return jsonify(get_balise_dict_infos()), 200
    except:
        return jsonify({'error':'failed to update plages_horaire'}), 400


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
        print("non")

        new_annonce = {"id_annonce":id_annonce, "nom":nom, "type":type, 
            "filename":filename,
            "contenu":contenu, "lang":lang, "duree":duree}
        config["ANNONCES"].append(new_annonce)
        print("oui")

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

@app.route('/delannonce', methods=['POST'])
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
            del annonces[index_annonce]
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
            else:
              return jsonify({'error':'failed to upload audio file'}), 400
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
        if result is not None and "filename" in result:
            filename = result["filename"]
#            print(filename)
        else:
            filename = 'Balise1-0.wav'
        print(filename)
        audio_file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'audio', filename)
        volume = int(config['INFOS']['volume'])
        print(volume)
        m = alsaaudio.Mixer('DAC')
        m.getvolume()
        m.setvolume(volume)        
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


@app.route('/timeslots', methods=['PUT'])
def add_timeslot():
    try:
        data = request.get_json(force=True)
        print(data)
        id_timeslot = int(data.get("id_timeslot"))
        id_annonce = data.get("id_annonce")
        monday = data.get("monday")
        tuesday = data.get("tuesday")
        wednesday = data.get("wednesday")
        thursday = data.get("thursday")
        friday = data.get("friday")
        saturday = data.get("saturday")
        sunday = data.get("sunday")
        time_start = data.get("time_start")
        time_end = data.get("time_end")
        with open(CONFIG_FILE) as c:
            config = yaml.load(c, Loader=yaml.SafeLoader)
        new_timeslot = {"id_timeslot":id_timeslot, "id_annonce":id_annonce, "monday":monday, 
            "tuesday":tuesday, "wednesday":wednesday, "thursday":thursday, "friday":friday, 
            "saturday":saturday, "sunday":sunday, "time_start":time_start, "time_end":time_end}
        config["TIME_SLOTS"].append(new_timeslot)
        with open(CONFIG_FILE, "w") as c:
            yaml.dump(config, c, sort_keys=False, Dumper=yaml.SafeDumper)
        return jsonify(new_timeslot), 201
    except:
        return 'oups', 400


@app.route('/timeslots', methods=['POST'])
def set_timeslot():
    try:
        data = request.get_json(force=True)
        print(data)
        id_timeslot = int(data.get("id_timeslot"))
        id_annonce = data.get("id_annonce")
        monday = data.get("monday")
        tuesday = data.get("tuesday")
        wednesday = data.get("wednesday")
        thursday = data.get("thursday")
        friday = data.get("friday")
        saturday = data.get("saturday")
        sunday = data.get("sunday")
        time_start = data.get("time_start")
        time_end = data.get("time_end")
        with open(CONFIG_FILE) as c:
            config = yaml.load(c, Loader=yaml.SafeLoader)
        timeslots = config['TIME_SLOTS']
        # get timeslots from id_timeslot
        index_timeslot = next((i for i, item in enumerate(timeslots) if item["id_timeslot"] == id_timeslot), None)
        if index_timeslot is not None:
            updated_timeslot = {"id_timeslot":id_timeslot, "id_annonce":id_annonce, "monday":monday, 
            "tuesday":tuesday, "wednesday":wednesday, "thursday":thursday, "friday":friday, 
            "saturday":saturday, "sunday":sunday, "time_start":time_start, "time_end":time_end}
            # save to configfile
            config["TIME_SLOTS"][index_timeslot] = updated_timeslot
            with open(CONFIG_FILE, "w") as c:
                yaml.dump(config, c, sort_keys=False, Dumper=yaml.SafeDumper)
            return jsonify(updated_timeslot), 200
        else:
            return jsonify({'error':'timeslot not found'}), 404
    except:
        return jsonify({'error':'failed to send the id test'}), 400



@app.route('/deltimeslot', methods=['POST'])
def delete_timeslot():
    try:
        data = request.get_json(force=True)
        print(data)
        id_timeslot = int(data.get("id_timeslot"))
        with open(CONFIG_FILE) as c:
            config = yaml.load(c, Loader=yaml.SafeLoader)
        timeslots = config['TIME_SLOTS']
        # get time slot from id_timeslot
        index_timeslot = next((i for i, item in enumerate(timeslots) if item["id_timeslot"] == id_timeslot), None)
        if index_timeslot is not None:
            del timeslots[index_timeslot]
            # save to configfile
            with open(CONFIG_FILE, "w") as c:
                yaml.dump(config, c, sort_keys=False, Dumper=yaml.SafeDumper)
            return jsonify({'id_timeslot':id_timeslot}), 200
        else:
            return jsonify({'error':'time slot not found'}), 404
    except:
        return jsonify({'error':'failed to send the id test'}), 400


@app.route('/annonce/sound/<int:id_annonce>', methods=['GET'])
def download_files(id_annonce):
    try:
        with open(CONFIG_FILE) as c:
            config = yaml.load(c, Loader=yaml.SafeLoader)
        annonces = config['ANNONCES']
        # get annonce from id_annonce
        index_annonce = next((i for i, item in enumerate(annonces) if item["id_annonce"] == id_annonce), None)
        if index_annonce is not None and "filename" in annonces[index_annonce]:
            filename = annonces[index_annonce]["filename"]
            print(filename)
            path = os.path.join(app.config['UPLOAD_FOLDER'], 'audio')
            return send_from_directory(path, filename, as_attachment=True), 200
        else:
            return jsonify({'error':'soundfile not found'}), 404
    except:
        return jsonify({'error':'failed to download soundfile'}), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
