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
        STEP = 2
        DIR = 3
        MS1 = 4
        MS2 = 5
        MS3 = 6
        sensor = HomeSensor(17)
        stepper = Stepper(dir_pin=DIR, step_pin=STEP, ms1_pin=MS1, ms2_pin=MS2, ms3_pin=MS3)
        stepper.set_step_size(4)
        XMAX = 460
        print('MAX STEPS IS {}'.format(XMAX))
        m = HomingMotor("X-Motor", stepper, sensor, XMAX, False)

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
