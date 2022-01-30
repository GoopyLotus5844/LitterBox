test_mode = False

from datetime import datetime as date_util
from dbcommands import *
import logging
import time
import json
import requests
from twilio.rest import Client
import sqlite3
if not test_mode:
    import RPi.GPIO as GPIO
    from picamera import PiCamera

logging.basicConfig(filename='litterbox.log', level=logging.INFO)

keys = json.load(open('twilio_config.json'))
client = Client(keys['account_sid'], keys['auth_token'])

IMAGE_FOLDER = '/home/pi/Desktop/LitterBox/images'

conn = sqlite3.connect('litterbox.db', detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)

settings = json.load(open('detect_settings.json'))['test' if test_mode else 'normal']

messages = ['Please clean {}\'s litter box',
    'Clean ur litter box nerd! -{}',
    'Hurry up and clean the litter box! {} needs help!',
    'Litter box maximum threat level reached. {} is in dire danger.',
    'Litter box maximum threat level exceeded. {} is in dire danger.']
 
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

def send_text(count, dt_string):
    if not test_mode:
        if count > len(messages) - 1: count = len(messages) - 1
        user_settings = get_user_config(conn)
        text = messages[count].format(user_settings[0])

        camera = PiCamera()
        camera.capture("./images/" + dt_string + ".png")
        camera.close()
        
        message = client.messages.create(
            body=text,
            media_url=['http://76.206.246.29:5843' + '/uploads/' + dt_string + '.png'],
            from_=keys['twilio_phone'],
            to=user_settings[4]
        )
    else: print(messages[count].format(get_user_config(conn)[0]))
    
try:
    if not test_mode: setup_GPIO()
    trigger_count = 0
    start_time = -1
    last_event_time = get_recent_box_use(conn)[2].timestamp()
    msg_detect_time = -1
    msg_decect_time_str = ''

    #[cat name, range, uses before remdinder, cleaning pause length]
    user_settings = get_user_config(conn)

    test_dist_trigger = False
    
    while True:
        now = time.time()
        
        if not test_mode:
            dist = distance()
            triggered = dist <= user_settings[1]
        else: 
            triggered = test_dist_trigger
            print(test_dist_trigger, 'trigcount', trigger_count, 'winstart', start_time, 'lastevent', last_event_time, 'msgtime', msg_detect_time, 'now', now)
        
        #If there is a noteworthy measurement and the program is not paused due to recent event
        if triggered and now - last_event_time > settings['event_sep']:
            if start_time == -1:
                #If the event window is not active
                start_time = now
                trigger_count += 1
                #update settings when a new event window is started (not perfect, but bad idea to load settings once per second)
                #the first sensor measurement after changing the detect range will still use the old range
                user_settings = get_user_config(conn)
            else:
                #If the event window is active
                elapsed = now - start_time
                if elapsed < settings['event_length']:
                    #This measurement counts for this event window
                    trigger_count += 1
                else:
                    #The last active event window is over, so start over with 1 trigger count
                    logging.info('New event window started')
                    start_time = now
                    trigger_count = 1
            if not test_mode: 
                logging.info('TRIGGER dist: %.3f, trigcount: %d, time: %s', dist, trigger_count, 
                    date_util.fromtimestamp(now).strftime('%Y-%m-%d %H:%M:%S'))
                    
        if trigger_count == settings['event_thresh']:
            #If required trigger count reached, resent event window and add event to db
            start_time = -1
            trigger_count = 0

            clean_time = get_recent_clean(conn)[2].timestamp()
            
            if now - clean_time > user_settings[3]:
                last_event_time = now
                current_datetime = date_util.now()
                count = insert_box_use_event(conn, current_datetime)
                if count >= user_settings[2]:
                    msg_detect_time = now
                    msg_detect_time_str = current_datetime.isoformat("T", "seconds")
                    logging.info('Message scheduled for %s', msg_detect_time_str)
            else:
                logging.info('Box use event suppressed by cleaning')

        if msg_detect_time != -1 and now - msg_detect_time > settings['privacy_delay']:
            #final step - sending text after privacy delay
            msg_detect_time = -1
            count = get_recent_box_use(conn)[1] - user_settings[2]
            logging.info('Sending message for severity %d', count)
            send_text(count, msg_detect_time_str)
        
        if not test_mode:
            time.sleep(1)
        else:
            test_input = input()
            if test_input == '1': test_dist_trigger = True
            else: test_dist_trigger = False

except KeyboardInterrupt:
    print("Measurement stopped by User")
    if not test_mode: GPIO.cleanup()