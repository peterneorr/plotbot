#!/usr/bin/env python3

import sys
import time

import RPi.GPIO as GPIO
from pb.home_sensor import HomeSensor
from pb.stepper import Stepper

if __name__ == '__main__':

    try:
        GPIO.setmode(GPIO.BCM)

        Z_DIR = 1
        Z_STEP = 12
        Z_MS1 = 21
        Z_MS2 = 20
        Z_MS3 = 16
        z_stepper = Stepper(dir_pin=Z_DIR, step_pin=Z_STEP, ms1_pin=Z_MS1, ms2_pin=Z_MS2, ms3_pin=Z_MS3)
        z_home = HomeSensor(19)
        Z_UP = 1
        Z_DOWN = 0

        X_DIR = 5
        X_STEP = 6
        X_MS1 = 26
        X_MS2 = 19
        X_MS3 = 13
        x_stepper = Stepper(dir_pin=X_DIR, step_pin=X_STEP, ms1_pin=X_MS1, ms2_pin=X_MS2, ms3_pin=X_MS3)
        x_home = HomeSensor(24)
        X_RIGHT = 1
        X_LEFT = 0

        Y_DIR = 27
        Y_STEP = 22
        Y_MS1 = 9
        Y_MS2 = 10
        Y_MS3 = 11
        y_stepper = Stepper(dir_pin=Y_DIR, step_pin=Y_STEP, ms1_pin=Y_MS1, ms2_pin=Y_MS2, ms3_pin=Y_MS3)
        y_home = HomeSensor(23)
        Y_BACK = 0
        Y_FWD = 1
        directions = {'up': Z_UP, 'down': Z_DOWN, 'back': Y_BACK, 'forward': Y_FWD, 'left': X_LEFT, 'right': X_RIGHT}

        dirArg = sys.argv[1].lower()
        if dirArg not in directions:
            raise Exception('arg1 must be up, down, left, right, forward, or back')

        if dirArg in ['up', 'down']:
            stepper = z_stepper
        elif dirArg in ['left', 'right']:
            stepper = x_stepper
        elif dirArg in ['forward', 'back']:
            stepper = y_stepper
        stepper.set_step_size(1)
        stepper.set_direction(directions[dirArg])
        for x in range(int(sys.argv[2])):
            stepper.pulse()
            time.sleep(.001)

    except KeyboardInterrupt:
        GPIO.cleanup()
    sys.exit()
