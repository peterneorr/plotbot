#!/usr/bin/env python3
import sys
import time
import RPi.GPIO as GPIO

# microsecond sleep
usleep = lambda x: time.sleep(x / 1000000.0)
pulse_length_us = 500


class Stepper:
    def __init__(self, dir_pin, step_pin, ms1_pin, ms2_pin, ms3_pin):
        self.__dir_pin = dir_pin
        self.__step_pin = step_pin
        self.__ms1_pin = ms1_pin
        self.__ms2_pin = ms2_pin
        self.__ms3_pin = ms3_pin
        self.__direction = 1
        for pin in [self.__dir_pin, self.__step_pin, self.__ms1_pin, self.__ms2_pin, self.__ms3_pin]:
            GPIO.setup(pin, GPIO.OUT)

    def set_direction(self, direction):
        if direction == 1:
            self.__direction = 1
        elif direction == 0:
            self.__direction = 0
        else:
            raise Exception('Stepper direction must be either 1 or 0')
        GPIO.output(self.__dir_pin, self.__direction)

    def get_direction(self):
        return self.__direction

    def pulse(self):
        GPIO.output(self.__step_pin, 1)
        usleep(pulse_length_us)
        GPIO.output(self.__step_pin, 0)

    def set_step_size(self, step_size):
        if 16 == step_size:
            GPIO.output(self.__ms1_pin, 1)
            GPIO.output(self.__ms2_pin, 1)
            GPIO.output(self.__ms3_pin, 1)
        elif 8 == step_size:
            GPIO.output(self.__ms1_pin, 1)
            GPIO.output(self.__ms2_pin, 1)
            GPIO.output(self.__ms3_pin, 0)
        elif 4 == step_size:
            GPIO.output(self.__ms1_pin, 0)
            GPIO.output(self.__ms2_pin, 1)
            GPIO.output(self.__ms3_pin, 0)
        elif 2 == step_size:
            GPIO.output(self.__ms1_pin, 1)
            GPIO.output(self.__ms2_pin, 0)
            GPIO.output(self.__ms3_pin, 0)
        elif 1 == step_size:
            GPIO.output(self.__ms1_pin, 0)
            GPIO.output(self.__ms2_pin, 0)
            GPIO.output(self.__ms3_pin, 0)
        else:
            raise Exception('Stepper step_size {} invalid.  Must be 1, 2, 4, 8, or 16'.format(step_size))


if __name__ == '__main__':
    try:
        GPIO.setmode(GPIO.BCM)
        X_STEP = 2
        X_DIR = 3
        X_MS1 = 4
        X_MS2 = 5
        X_MS3 = 6
        tick = .1
        steps = 15
        s = Stepper(dir_pin=X_DIR, step_pin=X_STEP, ms1_pin=X_MS1, ms2_pin=X_MS2, ms3_pin=X_MS3)
        while True:
            for speed in (1, 2, 4, 8, 16):
                s.set_step_size(speed)
                print('1/{} step size'.format(speed))
                s.set_direction(0)
                for x in range(steps):
                    s.pulse()
                    time.sleep(tick)
                s.set_direction(1)
                for x in range(steps):
                    s.pulse()
                    time.sleep(tick)

    except KeyboardInterrupt:
        GPIO.cleanup()
    sys.exit()
