#import RPi.GPIO as GPIO
#from picamera import PiCamera
from datetime import datetime as date_util
from dbcommands import *
import time
import json
import requests
from twilio.rest import Client
import sqlite3

keys = json.load(open('twilio_config.json'))
client = Client(keys['account_sid'], keys['auth_token'])
IMAGE_FOLDER = '/home/pi/Desktop/LitterBox/images'

conn = sqlite3.connect('litterbox.db', detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)

messages = ['Please clean the litter box',
'Clean ur litter box nerd!',
'Hurry up and clean the litter box please!',
'Litter box maximum threat level reached',
'Litter box maximum threat level exceeded']

#GPIO.setmode(GPIO.BCM)
 
GPIO_TRIGGER = 18
GPIO_ECHO = 24

#Tick speed
POLL_DELAY = 1

#distance measurements less than this length are considered in determining events
DISTANCE_THRESH = 50

#must measure a distance less than DISTANCE thresh EVENT_THRESH times within this time window
EVENT_LENGTH = 45

#must measure a distance less than DISTANCE_THRESH this many times within EVENT_LENGTH
EVENT_THRESH = 4

#after an event is detected, ignore all measurements for this many seconds before considering more events
EVENT_SEP = 10

#number of events until text message is sent
EVENT_COUNT = 3

#wait this long before sending the text messsage to meet cat privacy standards
PRIVACY_DELAY = 5

#GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
#GPIO.setup(GPIO_ECHO, GPIO.IN)

#used for old ngrok setup to get the public URL of the image server
def get_ngrok_url():
    url = "http://localhost:4041/api/tunnels/"
    res = requests.get(url)
    res_unicode = res.content.decode("utf-8")
    res_json = json.loads(res_unicode)
    for i in res_json["tunnels"]:
        if i['name'] == 'command_line (http)':
            return i['public_url']

def distance():
    GPIO.output(GPIO_TRIGGER, True)
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)
 
    StartTime = time.time()
    StopTime = time.time()
    
    while GPIO.input(GPIO_ECHO) == 0:
        StartTime = time.time()
    while GPIO.input(GPIO_ECHO) == 1:
        StopTime = time.time()
 
    TimeElapsed = StopTime - StartTime
    distance = (TimeElapsed * 34300) / 2
 
    return distance

def send_text(count):
    if count > len(messages) - 1: count = len(messages) - 1
    now = date_util.now()

    print(messages[count])

    '''
    dt_string = now.strftime("%d-%m-%Y-H:%M:%S")
    camera = PiCamera()
    camera.capture("./images/" + dt_string + ".png")
    camera.close()
    
    print('ngrok URL:', get_ngrok_url())
    message = client.messages.create(
        body=messages[count],
        media_url=['http://76.206.246.29:5843' + '/uploads/' + dt_string + '.png'],
        from_=keys['twilio_phone'],
        to=keys['send_phone']
    )
    '''
    
try:
    trigger_count = 0
    start_time = -1
    last_event_time = -1
    msg_detect_time = -1

    test_dist_trigger = False
    
    while True:
        #dist = distance()
        now = time.time()
        print(test_dist_trigger, 'trigcount', trigger_count, 'winstart', start_time, 'lastevent', last_event_time, 'msgtime', msg_detect_time, 'now', now)
        
        #If there is a noteworthy measurement and the program is not paused due to recent event
        if test_dist_trigger and (last_event_time == -1 or now - last_event_time > EVENT_SEP):
            
            if start_time == -1:
                #If the event window is not active
                start_time = now
                trigger_count += 1
            else:
                #If the event window is active
                elapsed = now - start_time
                if elapsed < EVENT_LENGTH:
                    #This measurement counts for this event window
                    trigger_count += 1
                else:
                    #The last active event window is over, so start over with 1 trigger count
                    start_time = now
                    trigger_count = 1
                    
        if trigger_count == EVENT_THRESH:
            #If required trigger count reached, resent event window and add event to db
            start_time = -1
            trigger_count = 0
            last_event_time = now

            db_event = get_recent_event(conn)
            count = insert_litterbox_event(conn, db_event)

            if count >= EVENT_COUNT:
                msg_detect_time = now
                
        if msg_detect_time != -1 and now - msg_detect_time > PRIVACY_DELAY:
            #final step - sending text after privacy delay
            msg_detect_time = -1
            send_text(get_recent_event(conn)[2] - EVENT_COUNT)
        
        #.sleep(1)
        test_input = input()
        if test_input == '1': test_dist_trigger = True
        else: test_dist_trigger = False

except KeyboardInterrupt:
    print("Measurement stopped by User")
    #GPIO.cleanup()

send_text()