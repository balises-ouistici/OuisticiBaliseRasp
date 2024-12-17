from flask import Flask, Response, jsonify
import time

app = Flask(__name__)

# Variable globale indépendante de la session
shared_data = {
    'data': False
}

@app.route('/set_data/<value>', methods=['GET'])
def set_data(value):
    """Route pour mettre à jour la variable globale"""
    shared_data['data'] = value
    return jsonify(message=f'Data set to: {value}')

@app.route('/set', methods=['GET'])
def set_true():
    """Route pour mettre à jour la variable globale"""
    shared_data['data'] = True
    return jsonify(message=f'Data set to: True')

@app.route('/get_data', methods=['GET'])
def get_data():
    """Route pour streamer la variable globale en temps réel"""
    
    def generate_data():
        """Générateur pour émettre des événements SSE"""
        last_hello_time = time.time()
        while True:
            # Obtenir la valeur actuelle de shared_data
            data = shared_data.get('data', False)
            current_time = time.time()
            # Émettre la donnée sous forme d'événement SSE
            if data:
                yield f"data: {data}\n\n"
                shared_data['data'] = False
            elif current_time - last_hello_time >= 30:
                yield f"\n\n"
                last_hello_time = current_time
            time.sleep(0.5)  # Attendre 1 seconde avant de renvoyer la prochaine valeur
            
    return Response(generate_data(), mimetype='text/event-stream')

if __name__ == '__main__':
    app.run(debug=True)
