#!/usr/bin/env python


from RPi_AS3935 import RPi_AS3935

import RPi.GPIO as GPIO
import time
from datetime import datetime
import logging

# https://github.com/Hexalyse/LightningTweeter
# added for tweepy
import thread
import tweepy

# Initialize Twitter API, you need to get these from twitter
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)


GPIO.setmode(GPIO.BCM)

# LED attached to GPIO22 will be used as an indicator that the app has started
ledpin = 22 #GPIO22


GPIO.setup(ledpin, GPIO.OUT) #make pin 15, GPIO22 an output 

# Rev. 1 Raspberry Pis should leave bus set at 0, while rev. 2 Pis should set
# bus equal to 1. The address should be changed to match the address of the
# sensor. (Common implementations are in README.md)
sensor = RPi_AS3935(address=0x03, bus=1)

# 
sensor.set_indoors(True)

sensor.set_noise_floor(0)

# 0x06 came from the sensor packaging, do not change
sensor.calibrate(tun_cap=0x06)

# setup logger

logging.basicConfig(filename='lightning_data.csv', level=logging.WARNING, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y, %H:%M:%S,')


# I was seeing spurious reports of lightning with no storms in the area, so set min strikes to 5
# valid values are 1,5,9,16
sensor.set_min_strikes(5)

# variables for managing tweepy
last_alert = datetime.min
strikes_since_last_alert = 0

# We use a function to send tweet so that we can run it in a different thread and avoid spending too much time in the
# interrupt handle
def send_tweet(tweet):
    api.update_status(tweet)
	
	
def handle_interrupt(channel):
    # tweepy init
    global last_alert
    global strikes_since_last_alert
    global sensor
	
    current_timestamp = datetime.now()
	
    time.sleep(0.003)

    reason = sensor.get_interrupt()
    if reason == 0x01:
	logging.warning('Noise level too high - adjusting')
        sensor.raise_noise_floor()
    elif reason == 0x04:
        logging.warning('Disturber detected - masking')
        sensor.set_mask_disturber(True)
    elif reason == 0x08:
        distance = sensor.get_distance()
	energy = sensor.get_energy()
	logging.warning('%s,%s', distance,energy)
	#tweepy
	# if it has been < 300 sec since last tweet, increment the counter and exit
	if (current_timestamp - last_alert).seconds < 300:
            #print("Last strike is too recent, incrementing counter since last alert.")
            strikes_since_last_alert += 1
            return

	# if it has been >= 300 sec and this is the first strike, tweet it
	if strikes_since_last_alert == 0:
            thread.start_new_thread(send_tweet, ("Lightning detected {1}km away at a strength of {0}".format(energy, distance),))
        else:
	   # otherwise, it has been 300 sec and not the first strike, tweet the accumulated info
	   thread.start_new_thread(send_tweet, ("{2} strikes detected in the last {3} minutes. Power of the last strike : {0} - distance to the head of the storm : {1}km".format(energy, distance, strikes_since_last_alert + 1, (current_timestamp - last_alert).seconds / 60),))
	   # reset the strike counter and last alert time
           strikes_since_last_alert = 0
	last_alert = current_timestamp
		
	#tweepy


pin = 17

GPIO.setup(pin, GPIO.IN)
GPIO.add_event_detect(pin, GPIO.RISING, callback=handle_interrupt)

#print "Waiting for lightning - or at least something that looks like it"

GPIO.output(ledpin, GPIO.LOW) #turn on LED to let the world know we are running
# log configuration 
logging.warning('** Lightning detector has started, Minimum strikes is %s, Indoors is %s, Sensor Mask is %s', sensor.get_min_strikes(), sensor.get_indoors(), sensor.get_mask_disturber())
# log data header
logging.warning('distance, energy')
thread.start_new_thread(send_tweet, ("Lightning detector is online",))

try:
	while (True):
		# 
		time.sleep(1.0)

except: KeyboardInterrupt
GPIO.output(ledpin, GPIO.HIGH) #turn off LED to let the world know we are not running
thread.start_new_thread(send_tweet, ("Lightning detector is going offline",))
# give some time for the tweet before exiting
time.sleep(10)
GPIO.cleanup()

