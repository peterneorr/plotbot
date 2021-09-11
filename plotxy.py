#!/usr/bin/env python3
import logging
import threading
import sys
import time
import threading

import RPi.GPIO as GPIO
from pb.home_sensor import HomeSensor
from pb.homing_motor import HomingMotor
from pb.stepper import Stepper



def build(name: str, dir_pin: int, step_pin: int, ms1_pin: int, ms2_pin: int, ms3_pin: int, sensor_pin: int,
          max_steps: int, inverted: bool, pulse_delay: float = .001) -> HomingMotor:
    s = HomeSensor(sensor_pin)
    stepper = Stepper(dir_pin, step_pin, ms1_pin, ms2_pin, ms3_pin)
    return HomingMotor(name, stepper, s, max_steps, inverted, pulse_delay=pulse_delay)


UP = 700
DOWN = 956






def go_percent(m: HomingMotor, percent: float):
    pos = percent * m.get_max_steps()
    m.goto_pos(pos)


def main():
    GPIO.setmode(GPIO.BCM)
    x = build("x", dir_pin=5, step_pin=6, ms1_pin=26, ms2_pin=19, ms3_pin=13, sensor_pin=24,
              max_steps=920, inverted=False, pulse_delay=.0001)
    y = build("y", dir_pin=27, step_pin=22, ms1_pin=9, ms2_pin=10, ms3_pin=11, sensor_pin=23,
              max_steps=950, inverted=False)
    z = build("z", dir_pin=1, step_pin=12, ms1_pin=21, ms2_pin=20, ms3_pin=16, sensor_pin=25,
              max_steps=956, inverted=True, pulse_delay=.0005)
    pen_down = lambda: z.goto_pos(DOWN)
    pen_up = lambda: z.goto_pos(UP)

    def border():
        # draw bounding box
        x.go_home()
        y.go_home()
        pen_down();
        x.goto_pos(x.get_max_steps())
        y.goto_pos(y.get_max_steps())
        x.go_home()
        y.go_home()
        pen_up()

    time.sleep(1)
    try:
        z.go_home()
        x.go_home()
        y.go_home()

        for j in range(100, 200):
            go_percent(y, j / 200)
            for i in range(1, 200):
                go_percent(x, i / 200)
                pen_down()
                pen_up()
        z.go_home()
        GPIO.cleanup()

    except KeyboardInterrupt:
        z.go_home()
        GPIO.cleanup()


if __name__ == '__main__':
    main()
