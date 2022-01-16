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

def box_cleaned():
    count = insert_clean_event(conn)
    if(count > len(clean_messages) - 1): count = len(clean_messages) - 1
    resp = MessagingResponse()
    resp.message(clean_messages[count])
    return str(resp)

def stats():
    uses_since_clean = get_recent_box_use(conn)[1]
    avg_per_clean = round(get_avg_uses_before_clean(conn, 100), 2)
    avg_per_day = round(get_avg_daily_uses(conn, 100), 2)
    
    resp = MessagingResponse()
    resp.message('Uses since cleaned: ' + str(uses_since_clean) + "\n" +
        'Avg uses before cleaning: ' + str(avg_per_clean) + "\n" +
        'Avg uses each day: ' + str(avg_per_day))
    return str(resp)

@app.route('/uploads/<filename>', methods=['GET'])
def uploaded_file(filename):
    print(filename)
    return send_from_directory(IMAGE_FOLDER,
                               filename)

@app.route("/sms", methods=['GET', 'POST'])
def sms_reply():
    body = request.values.get('Body', None)
    if 'stat' in body: return stats()
    elif 'ok' in body or 'clean' in body: return box_cleaned()

if __name__ == "__main__":
    #app.run(host='192.168.1.64', port=5000, debug=False)
    #print(test_sms_reply())
    print(sms_reply())

'''
db structure
Each row is an "event"
ID, type, count, timestamp
type 1 is detect litter box use
type 2 is clean litter box
count is number of litter box usages between cleaning
'''
