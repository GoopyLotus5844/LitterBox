import json
import requests
from flask import Flask
from flask import request
from flask import send_from_directory
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse

keys = json.load(open('twilio_config.json'))
client = Client(keys['account_sid'], keys['auth_token'])
IMAGE_FOLDER = '/home/pi/Desktop/LitterBox/images'

app = Flask(__name__)
app.config

@app.route('/uploads/<filename>', methods=['GET'])
def uploaded_file(filename):
    print(filename)
    return send_from_directory(IMAGE_FOLDER,
                               filename)

@app.route("/sms", methods=['GET', 'POST'])
def sms_reply():
    resp = MessagingResponse()
    resp.message("The Robots are coming! Head for the hills!")
    return str(resp)

if __name__ == "__main__":
    app.run(host='192.168.1.64', port=5000, debug=False)
