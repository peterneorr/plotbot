#!/usr/bin/python3

import RPi.GPIO as GPIO
import sys, time

#microsecond sleep
usleep = lambda x: time.sleep(x/1000000.0)

GPIO.setmode(GPIO.BCM)
PIN_STEP = 2
PIN_DIR = 3
PIN_MS1 = 4
PIN_MS2 = 5
PIN_MS3 = 6

GPIO.setup(PIN_STEP,  GPIO.OUT)
GPIO.setup(PIN_DIR,  GPIO.OUT)
GPIO.setup(PIN_MS1,  GPIO.OUT)
GPIO.setup(PIN_MS2,  GPIO.OUT)
GPIO.setup(PIN_MS3,  GPIO.OUT)

# SET STEP SIZE
GPIO.output(PIN_MS1, 0)
GPIO.output(PIN_MS2, 0)
GPIO.output(PIN_MS3, 0)
try:

    pulse_length_us=500
    num_steps=10
    step_wait=1

    while True:    
        GPIO.output(PIN_DIR,1)
        # Makes 400 pulses for making one full cycle rotation
        
        for x in range(num_steps):
            GPIO.output(PIN_STEP,1)
            usleep(pulse_length_us)
            GPIO.output(PIN_STEP,0)            
            time.sleep(step_wait)
    
        GPIO.output(PIN_DIR,0)#Changes the rotations direction
        
        # Makes 400 pulses for making two full cycle rotation
        for x in range(num_steps):
            GPIO.output(PIN_STEP,1)
            usleep(pulse_length_us)
            GPIO.output(PIN_STEP,0)
            time.sleep(step_wait)

except KeyboardInterrupt:
    #print('interrupted!')
    GPIO.cleanup()
   
sys.exit()    
  
    