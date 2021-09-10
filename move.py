#!/usr/bin/env python3
import json
import sys
import os
import RPi.GPIO as GPIO

from pb.home_sensor import HomeSensor
from pb.stepper import Stepper
from pb.homing_motor import HomingMotor


def build(name: str, dir_pin: int, step_pin: int, ms1_pin: int, ms2_pin: int, ms3_pin: int, sensor_pin: int,
          max_steps: int, inverted: bool) -> HomingMotor:
    s = HomeSensor(sensor_pin)
    stepper = Stepper(dir_pin, step_pin, ms1_pin, ms2_pin, ms3_pin)
    return HomingMotor(name, stepper, s, max_steps, inverted)


def read_config():
    try:
        home = os.path.expanduser('~/')
        with open(home + '.plotbot.json', 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}
        write_config(data)
    return data


def write_config(data):
    home = os.path.expanduser('~/')
    with open(home + '.plotbot.json', 'w') as f:
        json.dump(data, f)
        f.write('\n')


def move(motor: HomingMotor, dist_arg: str, unit_arg: str):
    if dist_arg.startswith('+') or dist_arg.startswith('-'):
        move_relative(motor, dist_arg, unit_arg)
    else:
        move_absolute(motor, dist_arg, unit_arg)


def move_absolute(motor: HomingMotor, dist_arg: int, unit_arg: str):
    global x
    if unit_arg == "steps":
        try:
            pos = int(dist_arg)
        except ValueError as verr:
            print('Distance must be an integer value or \'home\' or \'max\'')
    elif unit_arg == "mm":
        try:
            pos = int(dist_arg) * steps_per_mm[motor]
        except ValueError as verr:
            print('Distance must be an integer value or \'home\' or \'max\'')
    else:
        raise Exception("Units must be 'steps' or 'mm'")

    count = motor.goto_pos(pos)
    print('Moved {} steps to get to current position: {}/{}'.format(count, motor.get_pos(), motor.get_max_steps()))


def move_relative(motor: HomingMotor, dist_arg: str, unit_arg: str):
    if dist_arg[0] == '+':
        forward = True
    else:
        forward = False
    try:
        num = int(str(dist_arg)[1:])
    except ValueError as verr:
        print('Distance must be an integer value or \'home\' or \'max\'')

    if unit_arg == "steps":
        steps = num
    elif unit_arg == "mm":
        steps = num * steps_per_mm[motor]
    else:
        raise Exception("Units must be 'steps' or 'mm'")

    count = 0
    for x in range(int(steps)):
        if motor.is_inverted():
            if forward:
                count += motor.step_backward()
            else:
                count += motor.step_forward()
        else:
            if forward:
                count += motor.step_forward()
            else:
                count += motor.step_backward()

    print('Moved {} steps to get to current position: {}/{}'.format(count, motor.get_pos(), motor.get_max_steps()))


if __name__ == '__main__':

    try:
        GPIO.setmode(GPIO.BCM)

        x = build("x", dir_pin=5, step_pin=6, ms1_pin=26, ms2_pin=19, ms3_pin=13, sensor_pin=24,
                  max_steps=920, inverted=False)
        y = build("y", dir_pin=27, step_pin=22, ms1_pin=9, ms2_pin=10, ms3_pin=11, sensor_pin=23,
                  max_steps=950, inverted=False)
        z = build("z", dir_pin=1, step_pin=12, ms1_pin=21, ms2_pin=20, ms3_pin=16, sensor_pin=25,
                  max_steps=1200, inverted=True)

        X_RIGHT = 1
        X_LEFT = 0
        Y_BACK = 0
        Y_FWD = 1
        Z_UP = 0
        Z_DOWN = 1

        steps_per_mm = {x: 1 / 0.2, y: 1 / 0.2, z: 1 / 0.0064}

        # directions = {'up': Z_UP, 'down': Z_DOWN, 'back': Y_BACK, 'forward': Y_FWD, 'left': X_LEFT, 'right': X_RIGHT}
        axis = {'x': x, 'y': y, 'z': z}

        dirArg = sys.argv[1].lower()
        if dirArg not in axis:
            raise Exception('Argument 1 must be x, y or z')

        config = read_config()

        for motor in [x, y, z]:
            pos_key = '{}-pos'.format(motor.get_name())
            if pos_key in config:
                motor.set_pos(config[pos_key])
            else:
                count = motor.go_home()
                print('{} moved {}/{} steps back to find home'
                      .format(motor.get_name(), count, motor.get_step_size()))
                config['{}-pos'.format(motor.get_name())] = 0

        motor = axis[dirArg]

        motor.set_step_size(1)
        dist_arg = sys.argv[2].lower()

        if dist_arg == 'home':
            motor.go_home()
        elif dist_arg == 'max':
            motor.goto_pos(motor.get_max_steps())
        else:
            unit_arg = sys.argv[3].lower()
            move(motor, dist_arg, unit_arg)
        config['{}-pos'.format(motor.get_name())] = motor.get_pos()
        write_config(config)
        GPIO.cleanup()

    except Exception:
        GPIO.cleanup()
