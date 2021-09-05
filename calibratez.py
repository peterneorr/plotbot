#!/usr/bin/env python3
import sys
import time

import RPi.GPIO as GPIO
from pb.stepper import Stepper
from pb.homing_motor import HomingMotor
from pb.home_sensor import HomeSensor

if __name__ == '__main__':
    try:
        GPIO.setmode(GPIO.BCM)
        Z_STEP = 12
        Z_DIR = 13
        Z_MS1 = 14
        Z_MS2 = 15
        Z_MS3 = 16
        stepper = Stepper(dir_pin=Z_DIR, step_pin=Z_STEP, ms1_pin=Z_MS1, ms2_pin=Z_MS2, ms3_pin=Z_MS3)
        sensor = HomeSensor(19)

        MAX = 20794
        print('MAX STEPS IS {}'.format(MAX))
        m = HomingMotor("Z-Motor", stepper, sensor, MAX, False)

        count = m.goto_pos(m.get_max_steps()/4)
        print('{} moved {}/{} steps to get to 25% position {}'.format(m.get_name(), count, m.get_step_size(), m.get_pos()))

        count = m.go_home()
        print('{} moved {}/{} steps back to find home'.format(m.get_name(), count, m.get_step_size()))

        count = m.goto_pos(m.get_max_steps() / 2)
        print('{} moved {}/{} steps to get to 50% position {}'.format(m.get_name(), count, m.get_step_size(), m.get_pos()))

    except KeyboardInterrupt:
        GPIO.cleanup()
    sys.exit()
