#!/usr/bin/env python3
import sys
import time
import RPi.GPIO as GPIO


class HomeSensor:
    def __init__(self, input_pin: int):
        self.__pin = input_pin
        GPIO.setup(self.__pin, GPIO.IN)

    def get_config(self):
        return {'input_pin': self.__pin}

    def is_home(self):
        return GPIO.input(self.__pin)


def main():
    try:
        GPIO.setmode(GPIO.BCM)
        x_home = HomeSensor(24)
        y_home = HomeSensor(23)
        z_home = HomeSensor(25)

        while True:
            print('X home sensor value is : {}'.format(x_home.is_home()))
            print('Y home sensor value is : {}'.format(y_home.is_home()))
            print('Z home sensor value is : {}'.format(z_home.is_home()))
            print()
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        GPIO.cleanup()


if __name__ == '__main__':
    main()
