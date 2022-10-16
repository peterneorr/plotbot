#!/usr/bin/env python3
import argparse
import copy
import traceback

import RPi.GPIO as GPIO

from pb.homing_motor import HomingMotor
import pb.plotbot as PB
from pb.homing_motor import HomingMotor
from plotbot import save_state

steps_per_mm = {'x': 1 / 0.2, 'y': 1 / 0.2, 'z': 1 / 0.0064}
unit = 100  # 5=1mm, 50=1cm, 100=2cm
profile = 'ballpoint'

# Directions:  1 = right,  2 = up, 3 = left, 4 = down

current_dir: int = 1  # starting direction is left
motors = {}
config = {}


def init():
    """Do some basic setup.  Put the pen just over bottom left corner"""
    global motors, config
    GPIO.setmode(GPIO.BCM)
    config = PB.read_config()
    x, y, z = PB.init_motors(config)
    motors = {'x': x, 'y': y, 'z': z}

    # delete current position - it might be incorrect
    config.pop('position', None)

    # return all motors to home position
    # Always do z first!  Lift the pen before you ramming things around!
    for name in ('z', 'x', 'y'):
        motor = motors[name]
        count = motor.go_home()
    save_state(config, motors)

    bottom = profile()['named-points']['y']['bottom-edge']
    left = profile()['named-points']['x']['left-edge']
    up = profile()['named-points']['z']['up']
    x.goto_pos(left)
    y.goto_pos(bottom)
    z.goto_pos(up)
    return config, motors


def profile():
    """returns the correct profile to use"""
    return [p for p in config['profiles'] if p['id'] == 'ballpoint'][0]


def cleanup():
    """lifts the pen up to a safe height when we're done"""
    for name in 'z':
        motor = motors[name]
        motor.go_home()
    save_state(config, motors)


def turn_left():
    """Change next movement 90 degrees to the left"""
    global current_dir
    current_dir = current_dir + 1
    if current_dir > 4:
        current_dir = 1


def pen_down():
    """Place the pen down on the drawing surface"""
    pos = profile()['named-points']['z']['down']
    motors['z'].goto_pos(pos)


def pen_up():
    """Lift the pen up off the drawing surface"""
    pos = profile()['named-points']['z']['up']
    motors['z'].goto_pos(pos)


def move():
    """move the pen 1 step in the current direction"""
    bottom = profile()['named-points']['y']['bottom-edge']
    top = profile()['named-points']['y']['top-edge']
    right = profile()['named-points']['x']['right-edge']
    left = profile()['named-points']['x']['left-edge']
    if current_dir == 1:
        # right
        axis = 'x'
        dist = 1
    elif current_dir == 2:
        # up
        axis = 'y'
        dist = 1
    elif current_dir == 3:
        # left
        axis = 'x'
        dist = -1
    elif current_dir == 4:
        # down
        axis = 'y'
        dist = -1
    motor = motors[axis];
    pos = motor.get_pos()
    global unit
    destination = pos + (dist * unit)
    print("{} pos is {}; destination is {}".format(axis, motor.get_pos(), destination))
    if (axis == 'y' and bottom <= destination <= top) or (axis == 'x' and left <= destination <= right):
        motor.goto_pos(destination)
    else:
        print("Warn: {} position {} is out of bounds".format(axis, destination))


def main():
    """Make the plot bot act like Karel the dog"""
    try:
        init()
        start()

    except Exception as ex:
        print('Error: {}'.format(ex))
        print(traceback.format_exc())

    finally:
        # cleanup
        cleanup()
        GPIO.cleanup()


if __name__ == '__main__':
    main()


def start():
    # students put their code here:
    # Only functions they start with is move(), turn_left(), pen_up(), and pen_down()

    # draw a square
    pen_down()
    move()
    move()
    turn_left()
    move()
    move()
    turn_left()
    move()
    move()
    turn_left()
    move()
    move()
    pen_up()
