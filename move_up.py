#!/usr/bin/env python3

import sys
import time

import RPi.GPIO as GPIO
from pb.home_sensor import HomeSensor
from pb.stepper import Stepper

if __name__ == '__main__':

    try:
        GPIO.setmode(GPIO.BCM)

        Z_STEP = 12
        Z_DIR = 13
        Z_MS1 = 14
        Z_MS2 = 15
        Z_MS3 = 16
        z_stepper = Stepper(dir_pin=Z_DIR, step_pin=Z_STEP, ms1_pin=Z_MS1, ms2_pin=Z_MS2, ms3_pin=Z_MS3)

        z_home = HomeSensor(19)

        Z_UP = 1
        Z_DOWN = 0
        z_stepper.set_direction(Z_UP)
        for x in range(int(sys.argv[1])):
            z_stepper.pulse()
            time.sleep(.001)

    except KeyboardInterrupt:
        GPIO.cleanup()
    sys.exit()
