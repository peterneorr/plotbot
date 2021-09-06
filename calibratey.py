#!/usr/bin/env python3
import sys
import time

import RPi.GPIO as GPIO
from pb.stepper import Stepper
from pb.homing_motor import HomingMotor
from pb.home_sensor import HomeSensor
import jsons

if __name__ == '__main__':
    try:
        GPIO.setmode(GPIO.BCM)
        Y_DIR = 27
        Y_STEP = 22
        Y_MS1 = 9
        Y_MS2 = 10
        Y_MS3 = 11
        stepper = Stepper(dir_pin=Y_DIR, step_pin=Y_STEP, ms1_pin=Y_MS1, ms2_pin=Y_MS2, ms3_pin=Y_MS3)
        sensor = HomeSensor(23)
        MAX = 950
        print('MAX STEPS IS {}'.format(MAX))
        m = HomingMotor("Y-Motor", stepper, sensor, MAX, False, .001)
        m.set_step_size(2)



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

        filename = 'ymotor.json'
        with open(filename, 'w') as outp:  # Overwrites any existing file.
            outp.writelines(jsons.dumps(m))
    except KeyboardInterrupt:
        GPIO.cleanup()

    GPIO.cleanup()
    sys.exit()
