#!/usr/bin/env python3
import argparse
import copy
import traceback

import RPi.GPIO as GPIO

from pb.homing_motor import HomingMotor
import pb.plotbot as PB

current_profile = 'default'
steps_per_mm = {'x': 1 / 0.2, 'y': 1 / 0.2, 'z': 1 / 0.0064}


def parse_args():
    """Defines CLI arguments, parses args, and returns parsed results"""
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(title='Command', dest="command", required=True)

    parser_reset = subparsers.add_parser('reset', help='Move print head to home position')
    parser_status = subparsers.add_parser('status', help='Display current status')

    # create parser for the goto command
    parser_move = subparsers.add_parser('goto', help='Move the print head to a named position')
    parser_move.add_argument('axis', choices='xyz', help='Select which axis to move')
    parser_move.add_argument('name', help='Name of the saved position')

    # create parser for the move command
    parser_move = subparsers.add_parser('move', help='Move the print head')
    parser_move.add_argument('axis', choices='xyz', help='Select which axis to move')
    parser_move.add_argument('count', help='Distance to move the print head')
    parser_move.add_argument('units', choices=['steps', 'mm'], help='Units to use for distance')

    # create parser for the set command
    parser_set = subparsers.add_parser('set', help='Save current position to profile')
    parser_set.add_argument('axis', choices='xyz', help='Select which axis position to save')
    parser_set.add_argument('name', type=str, help='Name for the saved position')

    # create parser for the profile command
    parser_profile = subparsers.add_parser('profile', help='Profile actions')
    group = parser_profile.add_mutually_exclusive_group()
    group.required = True
    group.add_argument('-l', '--list', help='List available profiles', action="store_true")
    group.add_argument('-s', '--save', help='Save current profile as name', action='store', metavar='name')
    group.add_argument('--load', help='Load named profile', metavar='name')
    group.add_argument('--delete', help='Delete named profile', metavar='name')

    args = parser.parse_args()
    return args


def init():
    GPIO.setmode(GPIO.BCM)
    config = PB.read_config()
    x, y, z = PB.init_motors(config)
    motors = {'x': x, 'y': y, 'z': z}
    return config, motors


def handle_move(args):
    """Move the print head a specific distance along a given axis"""
    (config, motors) = init()
    motor = motors[args.axis]
    count = args.count
    units = args.units
    if count.startswith('+') or count.startswith('-'):
        move_relative(motor, count, units)
    else:
        move_absolute(motor, count, units)
    save_state(config, motors)


def save_state(config, motors):
    (x, y, z) = (motors['x'], motors['y'], motors['z'])
    PB.save(config, x, y, z)


def move_relative(motor: HomingMotor, dist_arg: str, unit_arg: str):
    if dist_arg[0] == '+':
        forward = True
    else:
        forward = False
    try:
        num = float(str(dist_arg)[1:])
    except ValueError:
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


def move_absolute(motor: HomingMotor, dist_arg: int, unit_arg: str):
    """Move to an absolute position for the given axis"""
    if unit_arg == "steps":
        try:
            pos = float(dist_arg)
        except ValueError:
            raise RuntimeError('Distance in steps must be an numeric value')
    elif unit_arg == "mm":
        try:
            pos = float(dist_arg) * steps_per_mm[motor.get_name()]
        except ValueError:
            raise RuntimeError('Distance in mm must be an numeric value')
    else:
        raise RuntimeError("Units must be 'steps' or 'mm'")

    count = motor.goto_pos(pos)
    print('{} moved {} pulses to get to current position: {}/{}'
          .format(motor.get_name(), count, motor.get_pos(), motor.get_max_steps()))


def handle_reset():
    """Move the print head to home position"""
    (config, motors) = init()

    # delete current position - it might be incorrect
    config.pop('position', None)

    # return all motors to home position
    # Always do z first!  Lift the pen before you ramming things around!
    for name in ('z', 'x', 'y'):
        motor = motors[name]
        count = motor.go_home()
        print('{} moved {} pulses to get to MIN position: {}/{}'
              .format(motor.get_name(), count, motor.get_pos(), motor.get_max_steps()))
    save_state(config, motors)


def handle_goto(args):
    """Move the print head to a position specifically named in the current profile"""
    (config, motors) = init()
    axis = args.axis
    motor = motors[axis]
    name = args.name
    if name == 'min':
        count = motor.go_home()
        print('{} moved {} pulses to get to MIN position: {}/{}'
              .format(motor.get_name(), count, motor.get_pos(), motor.get_max_steps()))
    elif name == 'mid':
        mid = (motor.get_max_steps() / 2)
        count = motor.goto_pos(mid)
        print('{} moved {} pulses to get to MID position: {}/{}'
              .format(motor.get_name(), count, motor.get_pos(), motor.get_max_steps()))
    elif name == 'max':
        count = motor.goto_pos(motor.get_max_steps())
        print('{} moved {} pulses to get to MAX position: {}/{}'
              .format(motor.get_name(), count, motor.get_pos(), motor.get_max_steps()))
    else:
        global current_profile
        profiles = config['profiles']
        profile = [p for p in profiles if p['id'] == current_profile][0]
        points = profile['named-points'][axis]
        if name in points.keys():
            pos = points[name]
            move_absolute(motor, pos, 'steps')
        else:
            print("Error: named-point '{}' does not exist for {} axis in the active profile"
                  .format(name, axis))
    save_state(config, motors)


def handle_set(args):
    """Add the current position as a named position to the current profile"""
    (config, motors) = init()
    axis = args.axis
    motor = motors[axis]
    name = args.name
    print(args)
    profiles = config['profiles']
    profile = [p for p in profiles if p['id'] == current_profile][0]

    if 'named-points' not in profile:
        profile['named-points'] = {}
    named_points = profile['named-points']
    if motor.get_name() not in named_points:
        named_points[motor.get_name()] = {}
    points_for_motor = named_points[motor.get_name()]
    points_for_motor[name] = motor.get_pos()
    save_state(config, motors)
    print("Set named-point '{}' for {} axis at position {}".format(name, motor.get_name(), motor.get_pos()))


def delete_profile(config, name):
    """Remove the named profile from the given  config object"""
    if name == 'default':
        print('Error:  default profile cannot be deleted')
        return
    profiles = config['profiles']
    if name not in (p['id'] for p in profiles):
        print('Error:  profile "{}" does not exist'.format(name))
    else:
        config['profiles'] = [p for p in profiles if p['id'] != name]
        print('Deleted profile "{}"'.format(name))


def save_profile(config, name):
    """Makes a copy of current_profile with name and adds to the the  config"""
    global current_profile
    profiles = config['profiles']
    original = [p for p in profiles if p['id'] == current_profile][0]
    exists = [p for p in profiles if p['id'] == name][0]
    if exists:
        print("Error: profile '{}' already exists".format(name))
        return
    clone = copy.deepcopy(original)
    clone['id'] = name
    profiles.append(clone)
    print("Profile '{}' saved as '{}'".format(current_profile, name))


def handle_profile(args):
    """Handle profile CRUD operations"""
    (config, motors) = init()
    profiles = config['profiles']
    if args.list:
        for p in profiles:
            print(p['id'])
    elif args.save:
        save_profile(config, args.save)
    elif args.load:
        if args.load not in (p['id'] for p in profiles):
            print('Error:  profile "{}" does not exist'.format(args.load))
        else:
            config['current-profile'] = args.load
            print("Active profile set to '{}'".format(args.load))
    elif args.delete:
        delete_profile(config, args.delete)
    save_state(config, motors)


def handle_status():
    """Display status information"""
    config = PB.read_config()
    print('current-profile: {}'.format(current_profile))
    print('position: {}'.format(config['position']))


def main():
    try:
        args = parse_args()
        config = PB.read_config()
        global current_profile
        current_profile = config['current-profile']
        if args.command == 'move':
            handle_move(args)
        elif args.command == 'set':
            handle_set(args)
        elif args.command == 'profile':
            handle_profile(args)
        elif args.command == 'reset':
            handle_reset()
        elif args.command == 'goto':
            handle_goto(args)
        elif args.command == 'status':
            handle_status()

    except Exception as ex:
        print('Error: {}'.format(ex))
        print(traceback.format_exc())

    finally:
        # cleanup
        GPIO.cleanup()


if __name__ == '__main__':
    main()
