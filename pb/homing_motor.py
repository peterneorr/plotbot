#!/usr/bin/env python3
import json
import sys
import time
from dataclasses import dataclass

import RPi.GPIO as GPIO
from .home_sensor import HomeSensor
from .stepper import Stepper


class HomingMotor:
    def __init__(self, name: str, stepper: Stepper, home_sensor: HomeSensor, max_steps=50, inverted=False,
                 pulse_delay=.001, step_size=1):
        self.__name = name
        self.__stepper = stepper
        self.__sensor = home_sensor
        self.__inverted = inverted
        self.__max_steps = max_steps
        self.__position = 0
        self.__pulse_delay = pulse_delay
        self.__stepper.set_step_size(step_size)
        # count = self.go_home()
        # print('{} init - moved {}/{} steps back to find home'.format(name, count, self.__stepper.get_step_size()))

    def get_config(self):
        return {'name': self.__name,
                'max_steps': self.__max_steps,
                'inverted': self.__inverted,
                'pulse_delay': self.__pulse_delay,
                'stepper': self.__stepper.get_config(),
                'sensor': self.__sensor.get_config()
                }

    def set_pos(self, p: int):
        self.__position = p

    def get_pulse_delay(self) -> float:
        """Returns the current delay in seconds between stepper motor pulses. Default is .001s  """
        return self.__pulse_delay

    def set_pulse_delay(self, t: float):
        """Sets the delay in seconds between stepper motor pulses. Default is .001s  """
        self.__pulse_delay = t

    def get_name(self) -> str:
        return self.__name

    def set_name(self, name: str):
        self.__name = name

    def set_max_steps(self, steps: int):
        self.__max_steps = steps

    def get_max_steps(self) -> int:
        return self.__max_steps

    def is_inverted(self) -> bool:
        return self.__inverted

    def go_home(self) -> int:
        step_count = 0
        while not self.is_home():
            self.step_backward()
            step_count += 1
        return step_count

    def step_backward(self):
        """Returns 1 if moved or 0 if not moved because motor is already at min or max"""
        if self.is_home():
            return 0
        if self.__inverted:
            self.__stepper.set_direction(1)
        else:
            self.__stepper.set_direction(0)
        self.__pulse()
        return 1

    def step_forward(self) -> int:
        """Returns 1 if moved or 0 if not moved because motor is already at min or max"""
        if self.get_pos() >= self.__max_steps:
            return 0
        if self.__inverted:
            self.__stepper.set_direction(0)
        else:
            self.__stepper.set_direction(1)
        self.__pulse()
        return 1

    def __pulse(self):
        self.__stepper.pulse()
        direction = self.__stepper.get_direction()
        if self.__inverted:
            direction = not direction
        if direction:
            self.__position += (1 / self.__stepper.get_step_size())
        else:
            self.__position -= (1 / self.__stepper.get_step_size())
        time.sleep(self.__pulse_delay)

    def is_home(self) -> bool:
        if self.__sensor.is_home():
            self.__position = 0
            return True
        return False

    def get_pos(self) -> float:
        return self.__position

    def goto_pos(self, n: int) -> int:
        if n > self.__max_steps:
            raise RuntimeError(
                'Cannot move motor {} to {}. (beyond max steps of {})'.format(self.__name, n, self.__max_steps))
        elif n < 0:
            raise RuntimeError('Cannot move motor {} to position less than 0'.format(self.__name, n, self.__max_steps))
        step_count = 0
        while self.get_pos() < n:
            self.step_forward()
            step_count += 1
        while self.get_pos() > n and not self.is_home():
            self.step_backward()
            step_count += 1
        return step_count

    def set_step_size(self, step_size: int):
        if self.__stepper is None:
            return
        self.__stepper.set_step_size(step_size)

    def get_step_size(self) -> int:
        return self.__stepper.get_step_size()


def main():
    try:
        GPIO.setmode(GPIO.BCM)
        sensor = HomeSensor(24)
        stepper = Stepper(dir_pin=5, step_pin=6, ms1_pin=26, ms2_pin=19, ms3_pin=13)
        stepper.set_step_size(4)

        m = HomingMotor("XMotor", stepper, sensor, 460)

        for x in range(3):
            count = m.goto_pos(m.get_max_steps() / 4)
            print('{} moved {} steps to get to position {}'.format(m.get_name(), count, m.get_pos()))
            x = m.go_home()
            print('{} moved {} steps back to find home'.format(m.get_name(), x))
        count = m.goto_pos(m.get_max_steps() / 2)
        print('{} moved {} steps to get to position {}'.format(m.get_name(), count, m.get_pos()))
    except KeyboardInterrupt:
        pass
    finally:
        GPIO.cleanup()


if __name__ == '__main__':
    main()
