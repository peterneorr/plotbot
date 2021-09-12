#!/usr/bin/env python3
import json
import sys
import os
import RPi.GPIO as GPIO

from pb.home_sensor import HomeSensor
from pb.stepper import Stepper
from pb.homing_motor import HomingMotor

X_RIGHT = 1
X_LEFT = 0
Y_BACK = 0
Y_FWD = 1
Z_UP = 0
Z_DOWN = 1

steps_per_mm = {'x': 1 / 0.2, 'y': 1 / 0.2, 'z': 1 / 0.0064}
margins = {'x': 4 / 0.2, 'y': 4 / 0.2, 'z': 0}


def build(name: str, dir_pin: int, step_pin: int, ms1_pin: int, ms2_pin: int, ms3_pin: int, sensor_pin: int,
          max_steps: int, inverted: bool, pulse_delay: float = .001) -> HomingMotor:
    s = HomeSensor(sensor_pin)
    stepper = Stepper(dir_pin, step_pin, ms1_pin, ms2_pin, ms3_pin)
    return HomingMotor(name, stepper, s, max_steps, inverted, pulse_delay=pulse_delay)


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
        json.dump(data, f, indent=4, sort_keys=True)
        f.write('\n')


def move_distance(motor: HomingMotor, dist_arg: str, unit_arg: str):
    if unit_arg not in ['steps', 'mm']:
        raise RuntimeError("Units must be 'steps' or 'mm'")
    if dist_arg.startswith('+') or dist_arg.startswith('-'):
        move_relative(motor, dist_arg, unit_arg)
    else:
        move_absolute(motor, dist_arg, unit_arg)


def move_absolute(motor: HomingMotor, dist_arg: int, unit_arg: str):
    if unit_arg == "steps":
        try:
            pos = int(dist_arg)
        except ValueError as verr:
            raise RuntimeError('Distance in steps must be an integer value')
    elif unit_arg == "mm":
        try:
            pos = float(dist_arg) * steps_per_mm[motor.get_name()]
        except ValueError as verr:
            raise RuntimeError('Distance in mm must be an numeric value')
    else:
        raise RuntimeError("Units must be 'steps' or 'mm'")

    count = motor.goto_pos(pos)
    print('{} pulses to get to current position: {}/{}'.format(count, motor.get_pos(), motor.get_max_steps()))


def move_relative(motor: HomingMotor, dist_arg: str, unit_arg: str):
    if dist_arg[0] == '+':
        forward = True
    else:
        forward = False
    try:
        num = float(str(dist_arg)[1:])
    except ValueError as verr:
        raise RuntimeError('Distance must be an numeric value')

    if unit_arg == "steps":
        steps = int(num)
    elif unit_arg == "mm":
        steps = num * motor.get_step_size() * steps_per_mm[motor.get_name()]
    else:
        raise RuntimeError("Units must be 'steps' or 'mm'")

    count = 0
    for _ in range(int(steps)):
        if forward:
            count += motor.step_forward()
        else:
            count += motor.step_backward()
    print('{} pulses to get to current position: {}/{}'.format(count, motor.get_pos(), motor.get_max_steps()))


def move_to_preset(motor: HomingMotor, dist_arg: str):
    if dist_arg == 'min':
        count = motor.go_home()
        print('{} pulses to get to MIN position: {}/{}'
              .format(count, motor.get_pos(), motor.get_max_steps()))
    elif dist_arg == 'home':
        count = motor.goto_pos(margins[motor.get_name()])
        print('{} pulses to get to HOME position: {}/{}'
              .format(count, motor.get_pos(), motor.get_max_steps()))
    elif dist_arg == 'mid':
        margin = margins[motor.get_name()]
        mid = ((motor.get_max_steps() - margin) / 2) + margin
        count = motor.goto_pos(mid)
        print('{} pulses to get to MID position: {}/{}'
              .format(count, motor.get_pos(), motor.get_max_steps()))
    elif dist_arg == 'max':
        count = motor.goto_pos(motor.get_max_steps())
        print('{} pulses to get to MAX position: {}/{}'
              .format(count, motor.get_pos(), motor.get_max_steps()))


def move_on_axis(m:HomingMotor):
    dist_arg = sys.argv[2].lower()

    if dist_arg in ('min', 'home', 'mid', 'max'):
        move_to_preset(m, dist_arg)
    else:
        if len(sys.argv) < 4:
            raise RuntimeError("Missing units argument.  Try 'steps' or 'mm'")
        else:
            unit_arg = sys.argv[3].lower()
        move_distance(m, dist_arg, unit_arg)


def init_motors(x: HomingMotor, y: HomingMotor, z: HomingMotor, config: dict) -> dict:
    if 'position' not in config:
        position = {}
    else:
        position = config['position']
    for motor in [z, x, y]:
        pos_key = motor.get_name()
        if pos_key in position:
            motor.set_pos(position[pos_key])
        else:
            print('{} position unknown. Calibrating...'.format(motor.get_name()))
            count = motor.go_home()
            print('{} moved {}/{} steps back to find home'
                  .format(motor.get_name(), count, motor.get_step_size()))
            position[pos_key] = 0
        if pos_key in config:
            if 'stepper' in config[pos_key]:
                if 'step_size' in config[pos_key]['stepper']:
                    motor.set_step_size(config[pos_key]['stepper']['step_size'])
    return position


def set_speed(m:HomingMotor):
    if len(sys.argv) < 4:
        raise RuntimeError("Missing required step size argument")
    speed = int(sys.argv[3])
    m.set_step_size(speed)
    print('Step size for {} set to 1/{}'.format(m.get_name(),m.get_step_size()))



def main():
    try:
        GPIO.setmode(GPIO.BCM)

        x = build("x", dir_pin=5, step_pin=6, ms1_pin=26, ms2_pin=19, ms3_pin=13, sensor_pin=24,
                  max_steps=920, inverted=False, pulse_delay=.001)
        y = build("y", dir_pin=27, step_pin=22, ms1_pin=9, ms2_pin=10, ms3_pin=11, sensor_pin=23,
                  max_steps=930, inverted=False)
        z = build("z", dir_pin=1, step_pin=12, ms1_pin=21, ms2_pin=20, ms3_pin=16, sensor_pin=25,
                  max_steps=4000, inverted=True, pulse_delay=.00001)

        axis = {'x': x, 'y': y, 'z': z}

        if len(sys.argv) < 2:
            raise RuntimeError('Missing argument 1: Must be reset, x, y, or z')

        if sys.argv[1].lower() == 'reset':
            write_config({})

        config = read_config()
        init_motors(x, y, z, config)
        axis = {'x': x, 'y': y, 'z': z}
        axis_arg = sys.argv[1].lower()

        if axis_arg in axis:
            if len(sys.argv)<2:
                raise RuntimeError("Missing expected arguments after '{}'"
                                   .format(sys.argv[1]))
            elif sys.argv[2].lower() == "speed":
                set_speed(axis[axis_arg])
            else:
                move_on_axis(axis[axis_arg])
        else:
            raise RuntimeError('1st argument must be reset, x, y, or z')

        # save current state
        position = {}
        for m in [x, y, z]:
            position[m.get_name()] = m.get_pos()
            config[m.get_name()] = m.get_config()

        config['margins'] = margins
        config['position'] = position
        write_config(config)

    except KeyboardInterrupt:
        # if program was interrupted, assume nothing about motor positions
        # and force a reset next execution.
        config.pop('position', None)
        write_config(config)
    except RuntimeError as ex:
        print('Error: {}'.format(ex))
    finally:
        GPIO.cleanup()


if __name__ == '__main__':
    main()
