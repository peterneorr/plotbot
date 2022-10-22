#!/usr/bin/env python3
import logging
import math
import threading
import sys
import time
import threading

import  RPi.GPIO as GPIO
from pb.home_sensor import HomeSensor
from pb.homing_motor import HomingMotor
from pb.stepper import Stepper
from PIL import Image
import pb.plotbot as PB
from plotbot import get_profile


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

    config, motors = PB.init()
    profile = get_profile('ballpoint')
    x, y, z = (motors['x'], motors['y'], motors['z'])
    pen_down = lambda: z.goto_pos(PB.named_point(profile, 'z', 'down'))
    pen_up = lambda: z.goto_pos(PB.named_point(profile, 'z', 'up'))
    y_home = PB.named_point(profile, 'y', 'home')
    x_home = PB.named_point(profile, 'x', 'home')

    try:
        PB.reset()
        x.goto_pos(x_home)
        y.goto_pos(y_home)

        i = Image.open(sys.argv[1])
        i.thumbnail((300, 300))
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
                    x.goto_pos((px + x_home))
                    y.goto_pos((py + y_home))
                    #go_percent(y, py / height)
                    #go_percent(x, px / width)

                    pen_down()
                    if px == width - 1 or py == height - 1:
                        pen_up()
                    elif nxt_pixel != -1 and not is_darker_than(pixels[nxt_pixel], avg):
                        pen_up()

        z.go_home()
        # move tray forward
        PB.tray_forward()
        GPIO.cleanup()

    except KeyboardInterrupt:
        GPIO.cleanup()


if __name__ == '__main__':
    main()
