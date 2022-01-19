test_mode = True

from datetime import datetime as date_util
from dbcommands import *
import time
import json
import requests
from twilio.rest import Client
import sqlite3
if not test_mode:
    import RPi.GPIO as GPIO
    from picamera import PiCamera

keys = json.load(open('twilio_config.json'))
client = Client(keys['account_sid'], keys['auth_token'])

IMAGE_FOLDER = '/home/pi/Desktop/LitterBox/images'

conn = sqlite3.connect('litterbox.db', detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)

settings = json.load(open('detect_settings.json'))['test' if test_mode else 'normal']

messages = ['Please clean the litter box',
    'Clean ur litter box nerd!',
    'Hurry up and clean the litter box please!',
    'Litter box maximum threat level reached',
    'Litter box maximum threat level exceeded']
 
GPIO_TRIGGER = 18
GPIO_ECHO = 24

def setup_GPIO():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
    GPIO.setup(GPIO_ECHO, GPIO.IN)

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

    if not test_mode:
        dt_string = now.strftime("%d-%m-%Y-H:%M:%S")
        camera = PiCamera()
        camera.capture("./images/" + dt_string + ".png")
        camera.close()
        
        message = client.messages.create(
            body=messages[count],
            media_url=['http://76.206.246.29:5843' + '/uploads/' + dt_string + '.png'],
            from_=keys['twilio_phone'],
            to=keys['send_phone']
        )
    
try:
    if not test_mode: setup_GPIO()
    trigger_count = 0
    start_time = -1
    last_event_time = get_recent_box_use(conn)[2].timestamp()
    msg_detect_time = -1

    test_dist_trigger = False
    
    while True:
        now = time.time()
        
        if not test_mode:
            dist = distance()
            print(dist, 'trigcount', trigger_count, 'winstart', start_time, 'lastevent', last_event_time, 'msgtime', msg_detect_time, 'now', now)
            triggered = dist <= settings['distance_thresh']
        else: 
            print(test_dist_trigger, 'trigcount', trigger_count, 'winstart', start_time, 'lastevent', last_event_time, 'msgtime', msg_detect_time, 'now', now)
            triggered = test_dist_trigger
        
        #If there is a noteworthy measurement and the program is not paused due to recent event
        if triggered and now - last_event_time > settings['event_sep']:   
            if start_time == -1:
                #If the event window is not active
                start_time = now
                trigger_count += 1
            else:
                #If the event window is active
                elapsed = now - start_time
                if elapsed < settings['event_length']:
                    #This measurement counts for this event window
                    trigger_count += 1
                else:
                    #The last active event window is over, so start over with 1 trigger count
                    start_time = now
                    trigger_count = 1
                    
        if trigger_count == settings['event_thresh']:
            #If required trigger count reached, resent event window and add event to db
            start_time = -1
            trigger_count = 0
            last_event_time = now
            count = insert_box_use_event(conn)
            if count >= settings['event_count']:
                msg_detect_time = now
                
        if msg_detect_time != -1 and now - msg_detect_time > settings['privacy_delay']:
            #final step - sending text after privacy delay
            msg_detect_time = -1
            send_text(get_recent_box_use(conn)[1] - settings['event_count'])
        
        if not test_mode:
            time.sleep(1)
        else:
            test_input = input()
            if test_input == '1': test_dist_trigger = True
            else: test_dist_trigger = False

except KeyboardInterrupt:
    print("Measurement stopped by User")
    if not test_mode: GPIO.cleanup()