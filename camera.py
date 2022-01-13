from picamera import PiCamera
from time import sleep
from datetime import datetime

now = datetime.now()
dt_string = now.strftime("%d-%m-%Y-H:%M:%S")
camera = PiCamera()
camera.capture(dt_string + ".png")
camera.close()
