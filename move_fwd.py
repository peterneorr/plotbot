#!/usr/bin/env python3

import sys
import time

import RPi.GPIO as GPIO
from pb.home_sensor import HomeSensor
from pb.stepper import Stepper

if __name__ == '__main__':
    try:
        GPIO.setmode(GPIO.BCM)

        Y_STEP = 7
        Y_DIR = 8
        Y_MS1 = 9
        Y_MS2 = 10
        Y_MS3 = 11
        y_stepper = Stepper(dir_pin=Y_DIR, step_pin=Y_STEP, ms1_pin=Y_MS1, ms2_pin=Y_MS2, ms3_pin=Y_MS3)

        y_home = HomeSensor(18)

        Y_BACK = 0
        Y_FWD = 1
        y_stepper.set_direction(Y_FWD)
        for x in range(int(sys.argv[1])):
            y_stepper.pulse()
            time.sleep(.001)

    except KeyboardInterrupt:
        GPIO.cleanup()
    sys.exit()
