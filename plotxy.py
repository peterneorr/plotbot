#!/usr/bin/env python3
import logging
import threading
import sys
import time
import threading

import RPi.GPIO as GPIO

from pb.homing_motor import HomingMotor
import pb.plotbot as PB


def main():
    GPIO.setmode(GPIO.BCM)

    config = PB.read_config()
    x, y, z = PB.init_motors(config)
    z.go_home()
    x.go_home()
    y.go_home()

    x_home = PB.named_point(config, "x", "home")
    y_home = PB.named_point(config, "y", "home")
    up = PB.named_point(config, "z", "up")
    down = PB.named_point(config, "z", "down")
    x.go_home = lambda: x.goto_pos(x_home)
    y.go_home = lambda: y.goto_pos(y_home)
    pen_down = lambda: z.goto_pos(down)
    pen_up = lambda: z.goto_pos(up)

    def border():
        # draw bounding box
        pen_up()
        x.go_home()
        y.go_home()
        pen_down()
        x.goto_pos(x.get_max_steps())
        y.goto_pos(y.get_max_steps())
        x.go_home()
        y.go_home()
        pen_up()

    try:
        x.go_home()
        y.go_home()
        #border()
        y_center = y_home + (y.get_max_steps() - y_home) / 2
        x_center = x_home + (x.get_max_steps() - x_home) / 2

        x.goto_pos(x_center)
        y.goto_pos(y_center)
        px = x_center
        py = y_center
        i = 1
        pen_down()
        while y.get_max_steps() > py > y_home and\
                x.get_max_steps() > px > x_home:

            px += i * 10
            x.goto_pos(px)
            py += i * 10
            y.goto_pos(py)
            i += 1
            px -= i * 10
            x.goto_pos(px)
            py -= i * 10
            y.goto_pos(py)
            i += 1
        pen_up()
        GPIO.cleanup()

    except KeyboardInterrupt:
        print("shutting down...")
        z.go_home()
        GPIO.cleanup()


if __name__ == '__main__':
    main()
