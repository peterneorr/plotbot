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
        Y_STEP = 7
        Y_DIR = 8
        Y_MS1 = 9
        Y_MS2 = 10
        Y_MS3 = 11
        stepper = Stepper(dir_pin=Y_DIR, step_pin=Y_STEP, ms1_pin=Y_MS1, ms2_pin=Y_MS2, ms3_pin=Y_MS3)
        sensor = HomeSensor(18)

        MAX = 460
        print('MAX STEPS IS {}'.format(MAX))
        m = HomingMotor("Y-Motor", stepper, sensor, MAX, False)

        count = m.goto_pos(m.get_max_steps()/4)
        print('{} moved {}/{} steps to get to 25% position {}'.format(m.get_name(), count, m.get_step_size(), m.get_pos()))

        count = m.go_home()
        print('{} moved {}/{} steps back to find home'.format(m.get_name(), count, m.get_step_size()))

        count = m.goto_pos(m.get_max_steps() / 2)
        print('{} moved {}/{} steps to get to 50% position {}'.format(m.get_name(), count, m.get_step_size(), m.get_pos()))

        count = m.go_home()
        print('{} moved {}/{} steps back to find home'.format(m.get_name(), count, m.get_step_size()))

        count = m.goto_pos(m.get_max_steps())
        print('{} moved {}/{} steps to get to 100% position {}'.format(m.get_name(), count, m.get_step_size(), m.get_pos()))

    except KeyboardInterrupt:
        GPIO.cleanup()
    sys.exit()
