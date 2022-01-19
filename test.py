import logging
import time
from datetime import datetime as date_util

logging.basicConfig(filename='sms_server.log', level=logging.INFO)

logging.info('SMS recieved at time %s', date_util.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))