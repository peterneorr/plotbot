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


def init_x() -> HomingMotor:
    dir = 5
    step = 6
    ms1 = 26
    ms2 = 19
    ms3 = 13
    sensor = HomeSensor(24)
    stepper = Stepper(dir_pin=dir, step_pin=step, ms1_pin=ms1, ms2_pin=ms2, ms3_pin=ms3)
    xmax = 920
    m = HomingMotor("X-Motor", stepper, sensor, xmax, False)
    return m


def init_y() -> HomingMotor:
    y_dir = 27
    y_step = 22
    y_ms1 = 9
    y_ms2 = 10
    y_ms3 = 11
    stepper = Stepper(dir_pin=y_dir, step_pin=y_step, ms1_pin=y_ms1, ms2_pin=y_ms2, ms3_pin=y_ms3)
    sensor = HomeSensor(23)
    ymax = 950
    m = HomingMotor("Y-Motor", stepper, sensor, ymax, False, .001)
    m.set_step_size(2)
    return m


def init_z() -> HomingMotor:
    z_dir = 1
    z_step = 12
    z_ms1 = 21
    z_ms2 = 20
    z_ms3 = 16
    stepper = Stepper(dir_pin=z_dir, step_pin=z_step, ms1_pin=z_ms1, ms2_pin=z_ms2, ms3_pin=z_ms3)
    sensor = HomeSensor(25)
    zmax = 3422
    m = HomingMotor("Z-Motor", stepper, sensor, zmax, True)
    return m


def wave(m: HomingMotor, percent: float, signal):
    """Runs indefinitely.  Intended to run in a thread"""
    if percent > 1 or percent < 0:
        raise Exception('Wave percent must be between 0 and 1')
    center = m.get_max_steps() / 2
    max = percent * m.get_max_steps()
    min = m.get_max_steps() - max
    m.goto_pos(center)
    while signal():
        m.goto_pos(max)
        m.goto_pos(min)


def dash(m: HomingMotor, len: float, signal):
    while signal():
        pen_down(m)
        time.sleep(len)
        pen_up(m)


def pen_up(z: HomingMotor):
    z.goto_pos(2100)


def pen_down(z: HomingMotor):
    z.goto_pos(2100 - 350)


def main():
    GPIO.setmode(GPIO.BCM)
    x, y, z = init_x(), init_y(), init_z()
    time.sleep(5)
    x.set_step_size(4)
    try:
        go = True
        x_thread = threading.Thread(target=wave, args=(x, .8, lambda: go))
        x_thread.start()
        y_thread = threading.Thread(target=wave, args=(y, .8, lambda: go))
        y_thread.start()


        time.sleep(2)
        z.goto_pos(2100)
        time.sleep(3600)
        print('time to stop!')
        go = False
        x_thread.join()
        y_thread.join()
        z_thread.join()

        GPIO.cleanup()

    except KeyboardInterrupt:
        go = False
        x_thread.join()
        y_thread.join()
        z_thread.join()
        z.go_home()
        GPIO.cleanup()


if __name__ == '__main__':
    main()
