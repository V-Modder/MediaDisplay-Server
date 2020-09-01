import json
from flask import Flask, request
import pystream

flaskApp = Flask(__name__)

def main():
    flaskApp.run(host='0.0.0.0')

@flaskApp.route("/sync", methods=["POST"])
def sync():
    image_file = request.files["render_image"]
    image_bytes = image_file.read()
    action = pystream.pystream.window.update_gui(image_bytes)
    return json.dumps(action)  
