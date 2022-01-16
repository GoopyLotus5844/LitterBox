import json
import requests
import sqlite3
from flask import Flask
from flask import request
from flask import send_from_directory
from dbcommands import *
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse

keys = json.load(open('twilio_config.json'))
client = Client(keys['account_sid'], keys['auth_token'])
IMAGE_FOLDER = '/home/pi/Desktop/LitterBox/images'

conn = sqlite3.connect('litterbox.db', detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)

clean_messages = ['OK don\'t remember asking', 'Cool.', 'Thank you.', 'Thanks!', 'Wow. Needed that.', 'Yikes. Do better next time', 'Thanks, you\'re a horrible pet owner', 'What is wrong with you?']

app = Flask(__name__)
app.config

def db_box_cleaned():
    insertQuery = 'INSERT INTO EVENTS(type, count, time) VALUES (?,?)'
    conn.execute(insertQuery, (2, -1, datetime.datetime.now()))

@app.route('/uploads/<filename>', methods=['GET'])
def uploaded_file(filename):
    print(filename)
    return send_from_directory(IMAGE_FOLDER,
                               filename)

def test_sms_reply():
    count = insert_clean_event(conn)
    if(count > len(clean_messages) - 1): count = len(clean_messages) - 1
    #resp = MessagingResponse()
    #resp.message(clean_messages[count])
    return str(clean_messages[count])

@app.route("/sms", methods=['GET', 'POST'])
def sms_reply():
    count = insert_clean_event(conn)
    if(count > len(clean_messages) - 1): count = len(clean_messages) - 1
    resp = MessagingResponse()
    resp.message(clean_messages[count])
    return str(resp)

if __name__ == "__main__":
    #app.run(host='192.168.1.64', port=5000, debug=False)
    print(test_sms_reply())

'''
db structure
Each row is an "event"
ID, type, count, timestamp
type 1 is detect litter box use
type 2 is clean litter box
count is number of litter box usages between cleaning
'''
