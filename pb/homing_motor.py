#!/usr/bin/env python3
import sys
import time

import RPi.GPIO as GPIO
from .home_sensor import HomeSensor
from .stepper import Stepper


class HomingMotor:
    def __init__(self, name, stepper, home_sensor, max_steps=50, inverted=False):
        self.__name = name
        self.__stepper = stepper
        self.__home = home_sensor
        self.__inverted = inverted
        self.__max_steps = max_steps
        self.__position = 0
        count = self.go_home()
        print('{} init - moved {}/{} steps back to find home'.format(name, count, self.__stepper.get_step_size()))

    def get_name(self):
        return self.__name

    def set_name(self, name):
        self.__name = name

    def set_max_steps(self, steps: int):
        self.__max_steps = steps

    def get_max_steps(self) -> int:
        return self.__max_steps

    def is_inverted(self):
        return self.__inverted

    def go_home(self) -> int:
        step_count = 0
        while not self.is_home():
            self.backward()
            step_count += 1
        return step_count

    def backward(self):
        if self.is_home():
            return
        if self.__inverted:
            self.__stepper.set_direction(1)
        else:
            self.__stepper.set_direction(0)
        self.__pulse()

    def forward(self):
        if self.get_pos() >= self.__max_steps:
            return
        if self.__inverted:
            self.__stepper.set_direction(0)
        else:
            self.__stepper.set_direction(1)
        self.__pulse()

    def __pulse(self):
        self.__stepper.pulse()
        direction = self.__stepper.get_direction()
        if self.__inverted:
            direction = not direction
        if direction:
            self.__position += (1 / self.__stepper.get_step_size())
        else:
            self.__position -= (1 / self.__stepper.get_step_size())
        time.sleep(.001)

    def is_home(self):
        if self.__home.is_home():
            self.__position = 0
            return True
        return False

    def get_pos(self):
        return self.__position

    def goto_pos(self, n: int) -> int:
        if n > self.__max_steps:
            raise Exception('Cannot move motor {} to {}. (beyond max steps of {})'.format(self.__name, n, self.__max_steps))
        elif n < 0:
            raise Exception('Cannot move motor {} to position less than 0'.format(self.__name, n, self.__max_steps))
        step_count = 0
        while self.get_pos() < n:
            self.forward()
            step_count += 1
        while self.get_pos() > n and not self.is_home():
            self.backward()
            step_count += 1
        return step_count

    def set_step_size(self, step_size: int):
        self.__stepper.set_step_size(step_size)

    def get_step_size(self) -> int:
        return self.__stepper.get_step_size()


if __name__ == '__main__':
    try:
        GPIO.setmode(GPIO.BCM)
        STEP = 2
        DIR = 3
        MS1 = 4
        MS2 = 5
        MS3 = 6
        sensor = HomeSensor(17)
        stepper = Stepper(dir_pin=DIR, step_pin=STEP, ms1_pin=MS1, ms2_pin=MS2, ms3_pin=MS3)
        stepper.set_step_size(4)

        m = HomingMotor("XMotor", stepper, sensor, 460)
        for x in range(3):
            count = m.goto_pos(m.get_max_steps()/4)
            print('{} moved {} steps to get to position {}'.format(m.get_name(), count, m.get_pos()))
            x = m.go_home()
            print('{} moved {} steps back to find home'.format(m.get_name(), x))
        count = m.goto_pos(m.get_max_steps() / 2)
        print('{} moved {} steps to get to position {}'.format(m.get_name(), count, m.get_pos()))
    except KeyboardInterrupt:
        GPIO.cleanup()
    sys.exit()
