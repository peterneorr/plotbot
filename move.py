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


def move_distance(motor: HomingMotor, dist_arg: int, go_forward: bool, unit_arg:str):
    global x
    if unit_arg == "steps":
        try:
            steps = int(dist_arg)
            for x in range(steps):
                if go_forward:
                    motor.step_forward()
                else:
                    motor.step_forward()
        except ValueError as verr:
            print('Distance must be an integer value or \'home\' or \'max\'')
    elif unit_arg == "mm":
        try:
            steps = int(dist_arg) * steps_per_mm[motor]
            print(steps)
            for x in range(int(steps)):
                if go_forward:
                    motor.step_forward()
                else:
                    motor.step_forward()
        except ValueError as verr:
            print('Distance must be an integer value or \'home\' or \'max\'')
    else:
        print("Units must be 'steps' or 'mm'")


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
        Z_UP = 1
        Z_DOWN = 0

        steps_per_mm = {x: 1/0.2, y: 1/0.2, z: 1/0.0064}

        directions = {'up': Z_UP, 'down': Z_DOWN, 'back': Y_BACK, 'forward': Y_FWD, 'left': X_LEFT, 'right': X_RIGHT}

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

        dirArg = sys.argv[1].lower()
        if dirArg not in directions:
            raise Exception('Argument 1 must be up, down, left, right, forward, or back')
        go_forward = directions[dirArg]

        if dirArg in ['up', 'down']:
            motor = z
        elif dirArg in ['left', 'right']:
            motor = x
        elif dirArg in ['forward', 'back']:
            motor = y

        motor.set_step_size(1)
        dist_arg = sys.argv[2].lower()

        if dist_arg == 'home':
            motor.go_home()
        elif dist_arg == 'max':
            motor.goto_pos(motor.get_max_steps())
        else:
            unit_arg = sys.argv[3].lower()
            move_distance(motor, dist_arg, go_forward, unit_arg)
        print('Current position: {}'.format(motor.get_pos()))
        config['{}-pos'.format(motor.get_name())] = motor.get_pos()
        write_config(config)
        GPIO.cleanup()

    except KeyboardInterrupt:

        GPIO.cleanup()
