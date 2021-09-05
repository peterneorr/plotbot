#!/usr/bin/env python3

import sys
import time

import RPi.GPIO as GPIO
from pb.home_sensor import HomeSensor
from pb.stepper import Stepper

if __name__ == '__main__':
    try:
        GPIO.setmode(GPIO.BCM)

        X_STEP = 2
        X_DIR = 3
        X_MS1 = 4
        X_MS2 = 5
        X_MS3 = 6
        x_stepper = Stepper(dir_pin=X_DIR, step_pin=X_STEP, ms1_pin=X_MS1, ms2_pin=X_MS2, ms3_pin=X_MS3)

        x_home = HomeSensor(17)

        X_RIGHT = 1
        X_LEFT = 0
        x_stepper.set_direction(X_RIGHT)
        for x in range(int(sys.argv[1])):
            x_stepper.pulse()
            time.sleep(.001)

    except KeyboardInterrupt:
        GPIO.cleanup()
    sys.exit()
