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

        Y_STEP = 7
        Y_DIR = 8
        Y_MS1 = 9
        Y_MS2 = 10
        Y_MS3 = 11
        y_stepper = Stepper(dir_pin=Y_DIR, step_pin=Y_STEP, ms1_pin=Y_MS1, ms2_pin=Y_MS2, ms3_pin=Y_MS3)

        Z_STEP = 12
        Z_DIR = 13
        Z_MS1 = 14
        Z_MS2 = 15
        Z_MS3 = 16
        z_stepper = Stepper(dir_pin=Z_DIR, step_pin=Z_STEP, ms1_pin=Z_MS1, ms2_pin=Z_MS2, ms3_pin=Z_MS3)

        x_home = HomeSensor(17)
        y_home = HomeSensor(18)
        z_home = HomeSensor(19)

        y_stepper.set_direction(0)
        # direction 0 = towards front.
        #    increasing y value for traditional x,y cartesian coord plane
        # direction 1 = towards back.  decreasing y val


        while True:
            y_stepper.set_direction(0)
            x_stepper.set_direction(0)
            x_stepper.set_step_size(1)
            for x in range(300):
#                y_stepper.pulse()
                x_stepper.pulse()
                time.sleep(.001)
            y_stepper.set_direction(1)
            x_stepper.set_direction(1)
            for x in range(300):
#                y_stepper.pulse()
                x_stepper.pulse()
                time.sleep(.001)

        #z direction 1 = UP   0 = DOWN
        #while True:
            z_stepper.set_direction(0)
            for x in range(500):
                z_stepper.pulse()
                time.sleep(.001)
            z_stepper.set_direction(1)
            for x in range(500):
                z_stepper.pulse()
                time.sleep(.001)

    except KeyboardInterrupt:
        GPIO.cleanup()
    sys.exit()
