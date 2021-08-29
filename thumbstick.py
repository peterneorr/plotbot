#!/usr/bin/python3

import RPi.GPIO as GPIO
import sys, time

#microsecond sleep
usleep = lambda x: time.sleep(x/1000000.0)

GPIO.setmode(GPIO.BCM)
# pins for x,y,z steppers
X_STEP = 2
X_DIR = 3
X_MS1 = 4
X_MS2 = 5
X_MS3 = 6
Y_STEP = 7
Y_DIR = 8
Y_MS1 = 9
Y_MS2 = 10
Y_MS3 = 11
Z_STEP = 12
Z_DIR = 13
Z_MS1 = 14
Z_MS2 = 15
Z_MS3 = 16
for pin in [X_STEP, X_DIR, X_MS1, X_MS2, X_MS3,
         Y_STEP, Y_DIR, Y_MS1, Y_MS2, Y_MS3,
        Z_STEP, Z_DIR, Z_MS1, Z_MS2, Z_MS3]:
    GPIO.setup(pin,  GPIO.OUT)

X_Home = 17
Y_Home = 18
Z_Home = 19

thumbX = 20
thumbY = 21
thumbB = 22

for pin in [X_Home,Y_Home,Z_Home, 
    thumbX, thumbY, thumbB]:
    GPIO.setup(pin,  GPIO.IN)


def setStepSize(ms1,ms2,ms3, speed):
    if (16 == speed):
        GPIO.output(ms1, 1)
        GPIO.output(ms2, 1)
        GPIO.output(ms3, 1)
    elif (8 == speed):
        GPIO.output(ms1, 1)
        GPIO.output(ms2, 1)
        GPIO.output(ms3, 0)
    elif (4 == speed):
        GPIO.output(ms1, 0)
        GPIO.output(ms2, 1)
        GPIO.output(ms3, 0)
    elif (2 == speed):
        GPIO.output(ms1, 1)
        GPIO.output(ms2, 0)
        GPIO.output(ms3, 0)
    elif (1 == speed) :
        GPIO.output(ms1, 0)
        GPIO.output(ms2, 0)
        GPIO.output(ms3, 0)
    else:
        raise Exception('Stepper speed {} invalid.  Must be 1, 2, 4, 8, or 16'.format(speed))

def pulse(pin):
    GPIO.output(pin,1)
    usleep(pulse_length_us)
    GPIO.output(pin,0)            

setStepSize(X_MS1,X_MS2,X_MS3,1)

EAST = True
NORTH = False
WEST = not EAST
SOUTH = not NORTH

def x_is_home():
 return GPIO.input(X_Home)

try:

    pulse_length_us=500
    num_steps=200
    step_wait=.01

    while True:  		
      
        print ('tx  {}'.format(  GPIO.input(thumbX)))
        print ('ty  {}'.format(  GPIO.input(thumbY)))

        print ()
        time.sleep(step_wait)
    
    
except KeyboardInterrupt:
    #print('interrupted!')
    GPIO.cleanup()
   
sys.exit()    
  
    