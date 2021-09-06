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
        DIR = 5
        STEP = 6
        MS1 = 26
        MS2 = 19
        MS3 = 13
        sensor = HomeSensor(24)
        stepper = Stepper(dir_pin=DIR, step_pin=STEP, ms1_pin=MS1, ms2_pin=MS2, ms3_pin=MS3)
        XMAX = 920
        print('MAX STEPS IS {}'.format(XMAX))
        m = HomingMotor("X-Motor", stepper, sensor, XMAX, False)


        count = m.goto_pos(m.get_max_steps() / 4)
        print('{} moved {}/{} steps to get to 25% position {}'.format(m.get_name(), count, m.get_step_size(),
                                                                      m.get_pos()))
        count = m.go_home()
        print('{} moved {}/{} steps back to find home'.format(m.get_name(), count, m.get_step_size()))

        count = m.goto_pos(m.get_max_steps() / 2)
        print('{} moved {}/{} steps to get to 50% position {}'.format(m.get_name(), count, m.get_step_size(),
                                                                      m.get_pos()))

        count = m.go_home()
        print('{} moved {}/{} steps back to find home'.format(m.get_name(), count, m.get_step_size()))

        count = m.goto_pos(m.get_max_steps())
        print('{} moved {}/{} steps to get to 100% position {}'.format(m.get_name(), count, m.get_step_size(),
                                                                       m.get_pos()))

        filename = 'xmotor.json'
        with open(filename, 'w') as outp:  # Overwrites any existing file.
            outp.writelines(jsons.dumps(m))

    except KeyboardInterrupt:
        GPIO.cleanup()

    GPIO.cleanup()
    sys.exit()
