#!/usr/bin/python

import time
from gpiozero import PWMOutputDevice, DigitalOutputDevice

class MotorControl:
    def __init__(self, motor_num, debug=False):
        self.debug = debug
        # Define motor control pins
        self.PWMA = PWMOutputDevice(17)  # Example GPIO pin
        self.AIN1 = DigitalOutputDevice(27)  # Example GPIO pin
        self.AIN2 = DigitalOutputDevice(22)  # Example GPIO pin
        self.PWMB = PWMOutputDevice(23)  # Example GPIO pin
        self.BIN1 = DigitalOutputDevice(24)  # Example GPIO pin
        self.BIN2 = DigitalOutputDevice(25)  # Example GPIO pin
        self.motor_num = motor_num

    def setDutycycle(self, pwm_device, pulse):
        # Set the duty cycle for a specific PWM device
        pwm_device.value = pulse / 100.0

    def setLevel(self, device, value):
        # Set the level for a specific digital device
        device.value = value

    def MotorRun(self, motor, index, speed):
        # Run the motor at a specified speed and direction
        if speed > 100:
            return
        if motor == 0:
            self.setDutycycle(self.PWMA, speed)
            if index == 0:
                self.setLevel(self.AIN1, 0)
                self.setLevel(self.AIN2, 1)
            else:
                self.setLevel(self.AIN1, 1)
                self.setLevel(self.AIN2, 0)
        else:
            self.setDutycycle(self.PWMB, speed)
            if index == 0:
                self.setLevel(self.BIN1, 0)
                self.setLevel(self.BIN2, 1)
            else:
                self.setLevel(self.BIN1, 1)
                self.setLevel(self.BIN2, 0)

    def MotorStop(self, motor):
        # Stop the motor
        if motor == 0:
            self.setDutycycle(self.PWMA, 0)
        else:
            self.setDutycycle(self.PWMB, 0)

# Example usage
# motor_control = MotorControl(motor_num=0, debug=False)
# motor_control.MotorRun(motor=0, index=0, speed=50)