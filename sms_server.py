test_mode = True

import json
import requests
import sqlite3
from flask import Flask
import time
from datetime import datetime as date_util
import logging
from flask import request
from flask import send_from_directory
from dbcommands import *
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse

logging.basicConfig(filename='sms_server.log', level=logging.INFO)

keys = json.load(open('twilio_config.json'))
client = Client(keys['account_sid'], keys['auth_token'])
IMAGE_FOLDER = '/home/pi/Desktop/LitterBox/images'

clean_messages = ['OK don\'t remember asking', 
    'Cool.', 
    'Thank you.', 
    'Thanks!', 
    'Wow. Needed that.', 
    'Yikes. Do better next time', 
    'Thanks, you\'re a horrible pet owner', 
    'What is wrong with you?']

app = Flask(__name__)
app.config

def connect_db():
    return sqlite3.connect('litterbox.db', detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)

def box_cleaned():
    conn = connect_db()
    count = insert_clean_event(conn)
    conn.close()
    logging.info('Box cleaned with %d uses', count)
    if(count > len(clean_messages) - 1): count = len(clean_messages) - 1
    resp = MessagingResponse()
    resp.message(clean_messages[count])
    return str(resp)

def stats():
    logging.info('Fetching stats')
    conn = connect_db()
    uses_since_clean = get_recent_box_use(conn)[1]
    avg_per_clean = round(get_avg_uses_before_clean(conn, 100), 2)
    avg_per_day = round(get_avg_daily_uses(conn, 100), 2)
    conn.close()

    resp = MessagingResponse()
    resp.message('Uses since cleaned: ' + str(uses_since_clean) + "\n" +
        'Avg uses before cleaning: ' + str(avg_per_clean) + "\n" +
        'Avg uses each day: ' + str(avg_per_day))
    return str(resp)

@app.route('/uploads/<filename>', methods=['GET'])
def uploaded_file(filename):
    return send_from_directory(IMAGE_FOLDER,
                               filename)

@app.route("/sms", methods=['GET', 'POST'])
def sms_reply():
    logging.info('SMS recieved at time %s', date_util.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))
    body = request.values.get('Body', None).lower()
    if 'stat' in body: return stats()
    elif 'ok' in body or 'clean' in body: return box_cleaned()

if __name__ == "__main__":
    if test_mode:
        print(stats())
    else:
        app.run(host='192.168.1.64', port=5000, debug=False)
