#!/usr/bin/env python3
import logging
import math
import threading
import sys
import time
import threading

import RPi.GPIO as GPIO
from pb.home_sensor import HomeSensor
from pb.homing_motor import HomingMotor
from pb.stepper import Stepper
from PIL import Image


def init_x() -> HomingMotor:
    dir = 5
    step = 6
    ms1 = 26
    ms2 = 19
    ms3 = 13
    sensor = HomeSensor(24)
    stepper = Stepper(dir_pin=dir, step_pin=step, ms1_pin=ms1, ms2_pin=ms2, ms3_pin=ms3)
    xmax = 904
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


def go_percent(m: HomingMotor, percent: float):
    pos = percent * m.get_max_steps()
    m.goto_pos(pos)


def avg_pixel_sum(i: Image):
    ttl = 0
    pixels = i.load()  # this is not a list
    width, height = i.size
    for py in range(height):
        for px in range(width):
            cur_pixel = pixels[px, py]
            ttl = ttl + sum(cur_pixel)
    return ttl / (width * height)


def is_darker_than(p, num) -> bool:
    cur_pixel_mono = sum(p)
    if cur_pixel_mono < num:
        # print('dark:{}'.format(p))
        return True
    # print('light:{}'.format(p))
    return False


def next_pixel(px, py, width: int, height: int):
    nx = px + 1
    ny = py
    if nx == width:
        ny = py + 1
        nx = 0
    if ny == height:
        return -1
    return nx, ny




def main():
    GPIO.setmode(GPIO.BCM)
    x, y, z = init_x(), init_y(), init_z()
    pen_down = lambda: z.goto_pos(1220)
    pen_up = lambda: z.goto_pos(1000)

    time.sleep(1)
    try:

        x.go_home()
        y.go_home()
        z.go_home()

        i = Image.open(sys.argv[1])
        i.thumbnail((100,100))
        i = i.transpose(Image.FLIP_TOP_BOTTOM)

        avg = avg_pixel_sum(i)
        pixels = i.load()  # this is not a list
        width, height = i.size
        for py in range(height):
            for px in range(width):
                cur_pixel = pixels[px, py]
                nxt_pixel = next_pixel(px, py, width, height)
                # print('current px: ({},{}), next px:{})'.format(px, py, nxt_pixel))

                if is_darker_than(cur_pixel, avg):
                    go_percent(y, py / height)
                    go_percent(x, px / width)
                    pen_down()
                    if px == width - 1 or py == height - 1:
                        pen_up()
                    elif nxt_pixel != -1 and not is_darker_than(pixels[nxt_pixel], avg):
                        pen_up()

        z.go_home()
        GPIO.cleanup()

    except KeyboardInterrupt:
        GPIO.cleanup()


if __name__ == '__main__':
    main()
