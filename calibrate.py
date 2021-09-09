#!/usr/bin/env python3
import sys
import time

import RPi.GPIO as GPIO
from pb.stepper import Stepper
from pb.homing_motor import HomingMotor
from pb.home_sensor import HomeSensor


def build(name: str, dir_pin: int, step_pin: int, ms1_pin: int, ms2_pin: int, ms3_pin: int, sensor_pin: int,
          max_steps: int, inverted: bool) -> HomingMotor:
    s = HomeSensor(sensor_pin)
    stepper = Stepper(dir_pin, step_pin, ms1_pin, ms2_pin, ms3_pin)
    motor = HomingMotor(name, stepper, s, max_steps, inverted)
    return motor


def move(m: HomingMotor):
    print('{} max steps is {}'
          .format(m.get_name(), m.get_max_steps()))
    count = m.goto_pos(m.get_max_steps() / 4)
    print('{} moved {}/{} steps to get to 25% position {}'
          .format(m.get_name(), count, m.get_step_size(), m.get_pos()))
    count = m.go_home()
    print('{} moved {}/{} steps back to find home'
          .format(m.get_name(), count, m.get_step_size()))
    count = m.goto_pos(m.get_max_steps() / 2)
    print('{} moved {}/{} steps to get to 50% position {}'
          .format(m.get_name(), count, m.get_step_size(), m.get_pos()))
    count = m.go_home()
    print('{} moved {}/{} steps back to find home'
          .format(m.get_name(), count, m.get_step_size()))
    count = m.goto_pos(m.get_max_steps())
    print('{} moved {}/{} steps to get to 100% position {}'
          .format(m.get_name(), count, m.get_step_size(), m.get_pos()))


if __name__ == '__main__':
    try:
        GPIO.setmode(GPIO.BCM)
        x = build("X-Motor", dir_pin=5, step_pin=6, ms1_pin=26, ms2_pin=19, ms3_pin=13, sensor_pin=24,
                  max_steps=920, inverted=False)
        y = build("Y-Motor", dir_pin=27, step_pin=22, ms1_pin=9, ms2_pin=10, ms3_pin=11, sensor_pin=23,
                  max_steps=950, inverted=False)
        z = build("Z-Motor", dir_pin=1, step_pin=12, ms1_pin=21, ms2_pin=20, ms3_pin=16, sensor_pin=25,
                  max_steps=1200, inverted=True)

        move(x)
        move(y)
        move(z)
        z.go_home()
        y.go_home()
        x.go_home()

    except KeyboardInterrupt:
        x.go_home()
        y.go_home()
        z.go_home()
        GPIO.cleanup()

    GPIO.cleanup()
    sys.exit()
