import flask
from flask import Flask, request, jsonify


app = Flask(__name__)
@app.route('/', methods=['GET'])
def index():
    return flask.send_from_directory('static', 'index.html')

@app.route('/api/models', methods=['GET'])
def get_models():
    models = [
        {'name': 'Model A', 'version': '1.0', 'imgUrl': 'images/0.jpg', 'description': 'Description of Model A'},
        {'name': 'Model B', 'version': '2.0', 'imgUrl': 'images/1.jpg', 'description': 'Description of Model B'},
        {'name': 'Model C', 'version': '3.0', 'imgUrl': 'images/2.jpg', 'description': 'Description of Model C'},
    ]
    return jsonify(models)
@app.route('/<path:path>', methods=['GET'])
def static_files(path):
    return flask.send_from_directory('static', path)

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')