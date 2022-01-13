import RPi.GPIO as GPIO
from picamera import PiCamera
from datetime import datetime
import time
import json
import requests
from twilio.rest import Client

keys = json.load(open('twilio_config.json'))
client = Client(keys['account_sid'], keys['auth_token'])
IMAGE_FOLDER = '/home/pi/Desktop/LitterBox/images'

GPIO.setmode(GPIO.BCM)
 
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
EVENT_SEP = 30

#number of events until text message is sent
EVENT_COUNT = 3

#wait this long before sending the text messsage to meet cat privacy standards
PRIVACY_DELAY = 90

GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)

def get_ngrok_url():
    url = "http://localhost:4041/api/tunnels/"
    res = requests.get(url)
    res_unicode = res.content.decode("utf-8")
    res_json = json.loads(res_unicode)
    for i in res_json["tunnels"]:
        if i['name'] == 'command_line (http)':
            return i['public_url']
            break

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

def send_text():
    now = datetime.now()
    dt_string = now.strftime("%d-%m-%Y-H:%M:%S")
    camera = PiCamera()
    camera.capture("./images/" + dt_string + ".png")
    camera.close()
    
    print('ngrok URL:', get_ngrok_url())
    message = client.messages.create(
        body='Clean ur litter box nerd',
        media_url=['http://76.206.246.29:5843' + '/uploads/' + dt_string + '.png'],
        from_=keys['twilio_phone'],
        to=keys['send_phone']
    )
    
try:
    trigger_count = 0
    start_time = -1
    last_event_time = -1
    
    event_count = 0
    msg_detect_time = -1;
    
    while True:
        dist = distance()
        now = time.time()
        print(dist, 'trigcount', trigger_count, 'winstart', start_time, 'lastevent', last_event_time, 'eventcount', event_count, 'msgtime', msg_detect_time, 'now', now)
        
        #If there is a noteworthy measurement and the program is not paused due to recent event
        if dist <= DISTANCE_THRESH and now - last_event_time > EVENT_SEP:
            
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
            #If required trigger count reached, reset event window, start pause counter, call event
            start_time = -1
            trigger_count = 0
            last_event_time = now
            event_count += 1
            
            if event_count == EVENT_COUNT:
                event_count = 0
                msg_detect_time = now
                
        if msg_detect_time != -1 and now - msg_detect_time > PRIVACY_DELAY:
            #final step - sending text after privacy delay
            msg_detect_time = -1
            send_text()
        
        #.sleep(1)
        input()

except KeyboardInterrupt:
    print("Measurement stopped by User")
    GPIO.cleanup()

send_text()