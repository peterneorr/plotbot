#!/usr/bin/env python3
import sys
import time
import RPi.GPIO as GPIO


class HomeSensor:
    def __init__(self, input_pin):
        self.pin = input_pin
        GPIO.setup(self.pin, GPIO.IN)

    def is_home(self):
        return GPIO.input(self.pin)


if __name__ == '__main__':
    try:
        GPIO.setmode(GPIO.BCM)
        x_home = HomeSensor(17)
        while True:
            print('home sensor value is : {}'.format(x_home.is_home()))
            time.sleep(1)
    except KeyboardInterrupt:
        GPIO.cleanup()

    sys.exit()
