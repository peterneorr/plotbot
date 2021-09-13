#!/usr/bin/env python3

import sys
import json
import os
import RPi.GPIO as GPIO

from pb.homing_motor import HomingMotor
import pb.plotbot as PB

X_RIGHT = 1
X_LEFT = 0
Y_BACK = 0
Y_FWD = 1
Z_UP = 0
Z_DOWN = 1

steps_per_mm = {'x': 1 / 0.2, 'y': 1 / 0.2, 'z': 1 / 0.0064}


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
            pos = float(dist_arg)
        except ValueError as verr:
            raise RuntimeError('Distance in steps must be an numeric value')
    elif unit_arg == "mm":
        try:
            pos = float(dist_arg) * steps_per_mm[motor.get_name()]
        except ValueError as verr:
            raise RuntimeError('Distance in mm must be an numeric value')
    else:
        raise RuntimeError("Units must be 'steps' or 'mm'")

    count = motor.goto_pos(pos)
    print('{} moved {} pulses to get to current position: {}/{}'
          .format(motor.get_name(), count, motor.get_pos(), motor.get_max_steps()))


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
    print('{} moved {} pulses to get to current position: {}/{}'.format(motor.get_name(), count, motor.get_pos(),
                                                                        motor.get_max_steps()))


def move_to_preset(motor: HomingMotor, dist_arg: str):
    if dist_arg == 'min':
        count = motor.go_home()
        print('{} moved {} pulses to get to MIN position: {}/{}'
              .format(motor.get_name(), count, motor.get_pos(), motor.get_max_steps()))
    elif dist_arg == 'mid':
        mid = (motor.get_max_steps() / 2)
        count = motor.goto_pos(mid)
        print('{} moved {} pulses to get to MID position: {}/{}'
              .format(motor.get_name(), count, motor.get_pos(), motor.get_max_steps()))
    elif dist_arg == 'max':
        count = motor.goto_pos(motor.get_max_steps())
        print('{} moved {} pulses to get to MAX position: {}/{}'
              .format(motor.get_name(), count, motor.get_pos(), motor.get_max_steps()))


def move_motor(m: HomingMotor, named_points: dict):
    dist_arg = sys.argv[2].lower()
    points = named_points[m.get_name()]
    if dist_arg in ('min', 'mid', 'max'):
        move_to_preset(m, dist_arg)
    elif dist_arg in points:
        steps = str(points[dist_arg])
        move_distance(m, steps, 'steps')
    else:
        if len(sys.argv) < 4:
            raise RuntimeError("Unknown named point '{}' or missing units argument.  Try 'steps' or 'mm'"
                               .format(dist_arg))
        else:
            unit_arg = sys.argv[3].lower()
        move_distance(m, dist_arg, unit_arg)


def set_speed(m: HomingMotor):
    if len(sys.argv) < 4:
        raise RuntimeError("Missing required step size argument")
    speed = int(sys.argv[3])
    m.set_step_size(speed)
    print('Step size for {} set to 1/{}'.format(m.get_name(), m.get_step_size()))


def set_point(m: HomingMotor, name: str, config: dict):
    """ saves the current position of given motor as a named point"""
    if 'named-points' not in config:
        config['named-points'] = {}
    named_points = config['named-points']
    if m.get_name() not in named_points:
        named_points[m.get_name()] = {}
    points_for_motor = named_points[m.get_name()]
    points_for_motor[name] = m.get_pos()


def main():
    try:
        GPIO.setmode(GPIO.BCM)

        if sys.argv[1].lower() == 'reset':
            PB.write_config({})

        config = PB.read_config()
        x, y, z = PB.init_motors(config)
        motors = {'x': x, 'y': y, 'z': z}

        if len(sys.argv) > 2:
            motor_arg = sys.argv[1].lower()
            if motor_arg in motors:
                selected_motor = motors[motor_arg]

                if sys.argv[2].lower() == "speed":
                    set_speed(selected_motor)
                elif sys.argv[2].lower() == "set":
                    set_point(selected_motor, sys.argv[3], config)
                else:
                    move_motor(selected_motor, config['named-points'])
            else:
                raise RuntimeError('1st argument must be reset, x, y, or z')

        # save current state
        PB.save(config, x, y, z)

    except KeyboardInterrupt:
        # if program was interrupted, assume nothing about motor positions
        # and force a reset next execution.
        config.pop('position', None)
        PB.write_config(config)
    except RuntimeError as ex:
        print('Error: {}'.format(ex))
    finally:
        GPIO.cleanup()


if __name__ == '__main__':
    main()
