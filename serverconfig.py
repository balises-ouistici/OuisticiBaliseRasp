from flask import Flask, request, jsonify, send_from_directory, Response
import yaml

# import secrets
from werkzeug.utils import secure_filename
import os
import time
from mpd import MPDClient


CONFIG_FILE = "config.yml"

UPLOAD_FOLDER = "media/uploads/"
ALLOWED_EXTENSIONS = {"mp3", "wav", "wave", "tmp"}
MAX_CONTENT_LENGTH = 16 * 1000 * 1000

# Variable globale indépendante de la session
shared_data = {"test_sound": False}

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def map_volume(volume):
    volume = max(min(volume, 100), 0)
    mapped_volume = int(60 + volume / 100 * 40)
    return mapped_volume


def unmap_volume(mapped_volume):
    volume = int((mapped_volume - 60) / 40 * 100)
    volume = max(min(volume, 100), 0)
    return volume


def get_balise_dict_infos():
    with open(CONFIG_FILE) as c:
        config = yaml.load(c, Loader=yaml.SafeLoader)
    volume = int(config["INFOS"]["volume"])
    volume = unmap_volume(volume)
    balise = config["INFOS"]
    balise.update({"volume": volume})
    print(balise)
    return balise


def get_balise_dict():
    with open(CONFIG_FILE) as c:
        config = yaml.load(c, Loader=yaml.SafeLoader)
    volume = int(config["INFOS"]["volume"])
    volume = unmap_volume(volume)
    balise = config["INFOS"]
    balise.update({"volume": volume})
    annonces = config["ANNONCES"]
    timeslots = config["TIME_SLOTS"]
    return {"balise": balise, "annonces": annonces, "timeslots": timeslots}


def get_annonces_dict():
    with open(CONFIG_FILE) as c:
        config = yaml.load(c, Loader=yaml.SafeLoader)
    return config["ANNONCES"]


def get_plages_dict():
    pass


def clean_unused_sounds():
    pass


@app.route("/")
def index():
    return "Hello world"


@app.route("/balise", methods=["GET"])
def query_infos():
    """
    Get the balise
    GET /balise
    Returns the balise dict if successful
    """
    try:
        return jsonify(get_balise_dict()), 200
    except:
        return jsonify({"error": "data not found"}), 204


@app.route("/volume", methods=["POST"])
def set_volume():
    """
    Set the volume of the balise
    POST /volume {volume: int}
    Returns the updated balise dict infos if successful
    """
    try:
        data = request.get_json(force=True)
        volume = int(data.get("volume"))
        mapped_volume = map_volume(volume)
        print("mapped volume = ", mapped_volume)
        # save to configfile
        with open(CONFIG_FILE) as c:
            config = yaml.load(c, Loader=yaml.SafeLoader)
        config["INFOS"]["volume"] = mapped_volume
        with open(CONFIG_FILE, "w") as c:
            yaml.dump(config, c, sort_keys=False, Dumper=yaml.SafeDumper)
        return jsonify(get_balise_dict_infos()), 200
    except:
        return jsonify({"error": "failed to update volume"}), 400


@app.route("/plages_horaire", methods=["POST"])
def set_plages_horaire():
    """
    Set the timeslots of the balise
    POST /plages_horaire {timeslots: list}
    Returns the updated balise dict infos if successful
    """
    try:
        data = request.get_json(force=True)
        print(data)
        plages_horaire = data.get("timeslots")
        # save to configfile
        with open(CONFIG_FILE) as c:
            config = yaml.load(c, Loader=yaml.SafeLoader)
        config["INFOS"]["timeslots"] = plages_horaire
        with open(CONFIG_FILE, "w") as c:
            yaml.dump(config, c, sort_keys=False, Dumper=yaml.SafeDumper)
        return jsonify(get_balise_dict_infos()), 200
    except:
        return jsonify({"error": "failed to update timeslots"}), 400


@app.route("/autovolume", methods=["POST"])
def set_autovolume():
    """
    Set the autovolume of the balise
    POST /autovolume {autovolume: bool}
    Returns the updated balise dict infos if successful
    """
    try:
        data = request.get_json(force=True)
        print(data)
        autovolume = data.get("autovolume")
        # save to configfile
        with open(CONFIG_FILE) as c:
            config = yaml.load(c, Loader=yaml.SafeLoader)
        config["INFOS"]["autovolume"] = autovolume
        with open(CONFIG_FILE, "w") as c:
            yaml.dump(config, c, sort_keys=False, Dumper=yaml.SafeDumper)
        return jsonify(get_balise_dict_infos()), 200
    except:
        return jsonify({"error": "failed to update autovolume"}), 400


@app.route("/infos", methods=["POST"])
def set_infos():
    """
    Set the name and place of the balise
    POST /infos {nom: string, lieu: string}
    Returns the updated balise dict infos if successful
    """
    try:
        data = request.get_json(force=True)
        nom = data.get("nom")
        lieu = data.get("lieu")
        default_message = data.get("id_message")
        try:
            default_message = int(default_message)
        except:
            default_message = None

        # save to configfile
        with open(CONFIG_FILE) as c:
            config = yaml.load(c, Loader=yaml.SafeLoader)
        config["INFOS"]["nom"] = nom
        config["INFOS"]["lieu"] = lieu
        config["INFOS"]["default_message"] = default_message
        with open(CONFIG_FILE, "w") as c:
            yaml.dump(config, c, sort_keys=False, Dumper=yaml.SafeDumper)
        return jsonify(get_balise_dict_infos()), 200
    except:
        return jsonify({"error": "failed to update name or/and place"}), 400


@app.route("/defaultmessage", methods=["POST"])
def set_default_message():
    """
    Set the default message of the balise
    POST /defaultmessage {id_message: int}
    Returns the updated balise dict infos if successful
    """
    try:
        data = request.get_json(force=True)
        default_message = data.get("id_message")
        try:
            default_message = int(default_message)
        except:
            default_message = None
        # save to configfile
        with open(CONFIG_FILE) as c:
            config = yaml.load(c, Loader=yaml.SafeLoader)
        config["INFOS"]["default_message"] = default_message
        with open(CONFIG_FILE, "w") as c:
            yaml.dump(config, c, sort_keys=False, Dumper=yaml.SafeDumper)
        return jsonify(get_balise_dict_infos()), 200
    except:
        return jsonify({"error": "failed to update default message"}), 400


@app.route("/annonces", methods=["GET"])
def get_annonces():
    """
    Get the annonces
    GET /annonces
    Returns the annonces dict
    """
    return jsonify(get_annonces_dict())


@app.route("/annonce", methods=["PUT"])
def add_annonce():
    """
    Add an annonce
    PUT /annonce {
        id_annonce: int,
        nom: string,
        type: string,
        filename: string,
        contenu: string,
        lang: string,
        duree: int
        }
    Returns the new annonce if successful
    """
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

        new_annonce = {
            "id_annonce": id_annonce,
            "nom": nom,
            "type": type,
            "filename": os.path.join(app.config["UPLOAD_FOLDER"], filename),
            "contenu": contenu,
            "lang": lang,
            "duree": duree,
        }
        config["ANNONCES"].append(new_annonce)
        print("oui")

        with open(CONFIG_FILE, "w") as c:
            yaml.dump(config, c, sort_keys=False, Dumper=yaml.SafeDumper)
        response_body = new_annonce
        #       token = secrets.token_urlsafe(6) + "_" + str(id_annonce)
        #       response_body.update({"upload_sound_url":"/annonce/upload_sound/" + token})
        return jsonify(response_body), 201
    except:
        return "oups", 400


@app.route("/annonce", methods=["POST"])
def set_annonce():
    """
    Modify an annonce
    POST /annonce {
        id_annonce: int,
        nom: string,
        type: string,
        filename: string,
        contenu: string,
        lang: string,
        duree: int
        }
    Returns the updated annonce if successful
    """
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
        annonces = config["ANNONCES"]
        # get annonce from id_annonce
        index_annonce = next(
            (i for i, item in enumerate(annonces) if item["id_annonce"] == id_annonce),
            None,
        )
        if index_annonce is not None:
            updated_annonce = {
                "id_annonce": id_annonce,
                "nom": nom,
                "type": type,
                "filename": os.path.join(app.config["UPLOAD_FOLDER"], filename),
                "contenu": contenu,
                "lang": lang,
                "duree": duree,
            }
            # save to configfile
            config["ANNONCES"][index_annonce] = updated_annonce
            with open(CONFIG_FILE, "w") as c:
                yaml.dump(config, c, sort_keys=False, Dumper=yaml.SafeDumper)
            return jsonify(updated_annonce), 200
        else:
            return jsonify({"error": "annonce not found"}), 404
    except:
        return jsonify({"error": "failed to send the sound test"}), 400


@app.route("/delannonce", methods=["POST"])
def delete_annonce():
    """
    Delete an annonce
    POST /delannonce {
        id_annonce: int
        }
    Returns the deleted annonce id_annonce if successful
    """
    try:
        data = request.get_json(force=True)
        print(data)
        id_annonce = int(data.get("id_annonce"))
        with open(CONFIG_FILE) as c:
            config = yaml.load(c, Loader=yaml.SafeLoader)
        annonces = config["ANNONCES"]
        # get annonce from id_annonce
        index_annonce = next(
            (i for i, item in enumerate(annonces) if item["id_annonce"] == id_annonce),
            None,
        )
        if index_annonce is not None:
            del annonces[index_annonce]
            if config["INFOS"]["default_message"] == index_annonce:
                config["INFOS"]["default_message"] = None
            # save to configfile
            with open(CONFIG_FILE, "w") as c:
                yaml.dump(config, c, sort_keys=False, Dumper=yaml.SafeDumper)
            # TODO : delete audiofile
            return jsonify({"id_annonce": id_annonce}), 200
        else:
            return jsonify({"error": "annonce not found"}), 404
    except:
        return jsonify({"error": "failed to send the sound test"}), 400


# @app.route('/annonce/upload_sound/<string:token>', methods=['POST'])
@app.route("/annonce/upload_sound", methods=["POST"])
def upload_sound():
    """
    Upload an audiofile
    POST /annonce/upload_sound {audiofile: file}
    Returns {code: 33} if successful
    """
    if True:
        try:
            file = request.files["audiofile"]
            if file.filename == "":
                return jsonify({"error": "failed to upload audio file"}), 400
            print(file.filename)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                print(filename)
                file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
                # TODO ?? convert to wave
                # file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'tempsound'))
                # outputfilename = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                # command = "ffmpeg -i tempsound {outputfilename}"
                # os.system(command)
                mpc = MPDClient()
                mpc.connect("localhost", 6600)
                mpc.update()
                mpc.close()
                mpc.disconnect()
                return jsonify({"code": 33}), 200
            else:
                return jsonify({"error": "failed to upload audio file"}), 400
        except:
            return jsonify({"error": "failed to upload audio file"}), 400
    return jsonify({"error": "failed to upload audio file"}), 403


@app.route("/test_sound", methods=["GET"])
def test_balise():
    """
    Test the balise
    GET /test_sound
    Returns {success:'sound test sent'} if successful
    """
    try:
        shared_data["test_sound"] = True
        return jsonify({"success": "sound test sent"}), 200
    except:
        return jsonify({"error": "failed to send the sound test"}), 400


@app.route("/timeslots", methods=["PUT"])
def add_timeslot():
    """
    Add a timeslot
    PUT /timeslots {
        id_timeslot: int,
        id_annonce: int,
        monday: bool,
        tuesday: bool,
        wednesday: bool,
        thursday: bool,
        friday: bool,
        saturday: bool,
        sunday: bool,
        time_start: string,
        time_end: string
        }
    Returns the new timeslot if successful
    """
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
        new_timeslot = {
            "id_timeslot": id_timeslot,
            "id_annonce": id_annonce,
            "monday": monday,
            "tuesday": tuesday,
            "wednesday": wednesday,
            "thursday": thursday,
            "friday": friday,
            "saturday": saturday,
            "sunday": sunday,
            "time_start": time_start,
            "time_end": time_end,
        }
        config["TIME_SLOTS"].append(new_timeslot)
        with open(CONFIG_FILE, "w") as c:
            yaml.dump(config, c, sort_keys=False, Dumper=yaml.SafeDumper)
        return jsonify(new_timeslot), 201
    except:
        return "oups", 400


@app.route("/timeslots", methods=["POST"])
def set_timeslot():
    """
    Modify a timeslot
    POST /timeslots {
        id_timeslot: int,
        id_annonce: int,
        monday: bool,
        tuesday: bool,
        wednesday: bool,
        thursday: bool,
        friday: bool,
        saturday: bool,
        sunday: bool,
        time_start: string,
        time_end: string
        }
    Returns the updated timeslot if successful
    """
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
        timeslots = config["TIME_SLOTS"]
        # get timeslots from id_timeslot
        index_timeslot = next(
            (
                i
                for i, item in enumerate(timeslots)
                if item["id_timeslot"] == id_timeslot
            ),
            None,
        )
        if index_timeslot is not None:
            updated_timeslot = {
                "id_timeslot": id_timeslot,
                "id_annonce": id_annonce,
                "monday": monday,
                "tuesday": tuesday,
                "wednesday": wednesday,
                "thursday": thursday,
                "friday": friday,
                "saturday": saturday,
                "sunday": sunday,
                "time_start": time_start,
                "time_end": time_end,
            }
            # save to configfile
            config["TIME_SLOTS"][index_timeslot] = updated_timeslot
            with open(CONFIG_FILE, "w") as c:
                yaml.dump(config, c, sort_keys=False, Dumper=yaml.SafeDumper)
            return jsonify(updated_timeslot), 200
        else:
            return jsonify({"error": "timeslot not found"}), 404
    except:
        return jsonify({"error": "failed to send the id test"}), 400


@app.route("/deltimeslot", methods=["POST"])
def delete_timeslot():
    """
    Delete a timeslot
    POST /deltimeslot {
        id_timeslot: int
        }
    Returns the deleted timeslot timeslot_id if successful
    """
    try:
        data = request.get_json(force=True)
        print(data)
        id_timeslot = int(data.get("id_timeslot"))
        with open(CONFIG_FILE) as c:
            config = yaml.load(c, Loader=yaml.SafeLoader)
        timeslots = config["TIME_SLOTS"]
        # get time slot from id_timeslot
        index_timeslot = next(
            (
                i
                for i, item in enumerate(timeslots)
                if item["id_timeslot"] == id_timeslot
            ),
            None,
        )
        if index_timeslot is not None:
            del timeslots[index_timeslot]
            # save to configfile
            with open(CONFIG_FILE, "w") as c:
                yaml.dump(config, c, sort_keys=False, Dumper=yaml.SafeDumper)
            return jsonify({"id_timeslot": id_timeslot}), 200
        else:
            return jsonify({"error": "time slot not found"}), 404
    except:
        return jsonify({"error": "failed to send the id test"}), 400


@app.route("/annonce/sound/<int:id_annonce>", methods=["GET"])
def download_files(id_annonce):
    """
    Download the soundfile
    GET /annonce/sound/<int:id_annonce>
    Returns the soundfile if successful
    """
    try:
        with open(CONFIG_FILE) as c:
            config = yaml.load(c, Loader=yaml.SafeLoader)
        annonces = config["ANNONCES"]
        # get annonce from id_annonce
        index_annonce = next(
            (i for i, item in enumerate(annonces) if item["id_annonce"] == id_annonce),
            None,
        )
        if index_annonce is not None and "filename" in annonces[index_annonce]:
            filename = annonces[index_annonce]["filename"]
            print(filename)
            path = os.path.join(app.config["UPLOAD_FOLDER"])
            return send_from_directory(path, filename, as_attachment=True), 200
        else:
            return jsonify({"error": "soundfile not found"}), 404
    except:
        return jsonify({"error": "failed to download soundfile"}), 400


@app.route("/events", methods=["GET"])
def stream_events():
    """Route pour streamer la variable globale en temps réel"""

    def generate_stream():
        """Générateur pour émettre des événements SSE"""
        last_hello_time = time.time()
        while True:
            # Obtenir la valeur actuelle de shared_data
            event = shared_data.get("test_sound", False)
            current_time = time.time()
            # Émettre la donnée sous forme d'événement SSE
            if event:
                yield '{"test_sound": true}\n\n'
                shared_data["test_sound"] = False
            elif current_time - last_hello_time >= 30:
                yield "\n\n"
                last_hello_time = current_time
            # Attendre 1 seconde avant de renvoyer la prochaine valeur
            time.sleep(1)

    return Response(generate_stream(), mimetype="text/event-stream")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
