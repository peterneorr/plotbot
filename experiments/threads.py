#!/usr/bin/python3

import logging
import threading
import sys
import time

import RPi.GPIO as GPIO

from pb.home_sensor import HomeSensor
from pb.stepper import Stepper

# microsecond sleep
usleep = lambda x: time.sleep(x / 1000000.0)

GPIO.setmode(GPIO.BCM)
# pins for x,y,z steppers
X_DIR = 5
X_STEP = 6
X_MS1 = 26
X_MS2 = 19
X_MS3 = 13
x_stepper = Stepper(dir_pin=X_DIR, step_pin=X_STEP, ms1_pin=X_MS1, ms2_pin=X_MS2, ms3_pin=X_MS3)

Y_DIR = 27
Y_STEP = 22
Y_MS1 = 9
Y_MS2 = 10
Y_MS3 = 11
y_stepper = Stepper(dir_pin=Y_DIR, step_pin=Y_STEP, ms1_pin=Y_MS1, ms2_pin=Y_MS2, ms3_pin=Y_MS3)

Z_DIR = 1
Z_STEP = 12
Z_MS1 = 21
Z_MS2 = 20
Z_MS3 = 16
z_stepper = Stepper(dir_pin=Z_DIR, step_pin=Z_STEP, ms1_pin=Z_MS1, ms2_pin=Z_MS2, ms3_pin=Z_MS3)

x_home = HomeSensor(24)
y_home = HomeSensor(23)
z_home = HomeSensor(25)

EAST = True
NORTH = False
WEST = not EAST
SOUTH = not NORTH
UP = True
DOWN = not UP


def x_thread(name):
    logging.info("Thread %s: starting", name)
    while True:
        x_stepper.set_direction(WEST)
        x_stepper.set_step_size(1)
        for x in range(200):
            x_stepper.pulse()
            time.sleep(step_wait)
        x_stepper.set_direction(EAST)
        x_stepper.set_step_size(2)
        for x in range(400):
            x_stepper.pulse()
            time.sleep(step_wait)


def y_thread(name):
    while True:
        y_stepper.set_direction(NORTH)
        for x in range(200):
            y_stepper.pulse()
            time.sleep(step_wait)
        y_stepper.set_direction(SOUTH)
        for x in range(200):
            y_stepper.pulse()
            time.sleep(step_wait)


def z_thread(name):
    while True:
        z_stepper.set_direction(UP)
        for x in range(2000):
            z_stepper.pulse()
            time.sleep(step_wait / 2)
        z_stepper.set_direction(DOWN)
        for x in range(2000):
            z_stepper.pulse()
            time.sleep(step_wait / 2)

try:
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")

    logging.info("Main    : before creating thread")

    pulse_length_us = 500

    step_wait = .001
    x_stepper.set_step_size(4)
    y_stepper.set_step_size(4)

    x = threading.Thread(target=x_thread, args=(1,))
    y = threading.Thread(target=y_thread, args=(2,))
    z = threading.Thread(target=z_thread, args=(3,))
    logging.info("Main    : before running thread")
    x.start()
    y.start()
    z.start()

    while True:
        print('x home sensor {}'.format(x_home.is_home()))
        print('y home sensor {}'.format(y_home.is_home()))
        print('z home sensor {}'.format(z_home.is_home()))
        print()
        time.sleep(2)

except KeyboardInterrupt:
    # print('interrupted!')
    GPIO.cleanup()

GPIO.cleanup()
sys.exit()
