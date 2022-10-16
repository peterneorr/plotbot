import json
import os
import RPi.GPIO as GPIO


from pb.homing_motor import HomingMotor, build_from_config, build


def init_motors(config: dict) -> list:
    GPIO.setmode(GPIO.BCM)

    try:
        x = build_from_config(config, 'x')
    except RuntimeError:
        x = build("x", dir_pin=5, step_pin=6, ms1_pin=26, ms2_pin=19, ms3_pin=13, sensor_pin=24,
                  max_steps=770, inverted=False, pulse_delay=.001)
    try:
        y = build_from_config(config, 'y')
    except RuntimeError:
        y = build("y", dir_pin=27, step_pin=22, ms1_pin=9, ms2_pin=10, ms3_pin=11, sensor_pin=23,
                  max_steps=905, inverted=False)
    try:
        z = build_from_config(config, 'z')
    except RuntimeError:
        z = build("z", dir_pin=1, step_pin=12, ms1_pin=21, ms2_pin=20, ms3_pin=16, sensor_pin=25,
                  max_steps=4000, inverted=True, pulse_delay=.00001)

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
            print('{} moved {}/{} steps back to find MIN'
                  .format(motor.get_name(), count, motor.get_step_size()))
            position[pos_key] = 0
    return x, y, z


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
    home_dir = os.path.expanduser('~/')
    with open(home_dir + '.plotbot.json', 'w') as f:
        json.dump(data, f, indent=4, sort_keys=True)
        f.write('\n')


def save(config: dict, x: HomingMotor, y: HomingMotor, z: HomingMotor):
    position = {}
    for m in [x, y, z]:
        position[m.get_name()] = m.get_pos()
        config[m.get_name()] = m.get_config()
    config['position'] = position
    write_config(config)


def named_point(config: dict, motor_name: str, point_name: str):
    points = config['named-points'][motor_name]
    return points[point_name]
