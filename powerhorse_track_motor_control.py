#!/usr/bin/python

import time
import math
import smbus

class MotorControl:
    # Registers/etc.
    __SUBADR1 = 0x02
    __SUBADR2 = 0x03
    __SUBADR3 = 0x04
    __MODE1 = 0x00
    __PRESCALE = 0xFE
    __LED0_ON_L = 0x06
    __LED0_ON_H = 0x07
    __LED0_OFF_L = 0x08
    __LED0_OFF_H = 0x09
    __ALLLED_ON_L = 0xFA
    __ALLLED_ON_H = 0xFB
    __ALLLED_OFF_L = 0xFC
    __ALLLED_OFF_H = 0xFD

    def __init__(self, address, motor_num, debug=False):
        # Initialize the I2C bus and set the address
        self.bus = smbus.SMBus(1)
        self.address = address
        self.debug = debug
        if self.debug:
            print("Reseting PCA9685")
        # Reset the PCA9685 mode
        self.write(self.__MODE1, 0x00)
        # Define motor control pins
        self.PWMA = 0
        self.AIN1 = 1
        self.AIN2 = 2
        self.PWMB = 5
        self.BIN1 = 3
        self.BIN2 = 4
        self.motor_num = motor_num

    def write(self, reg, value):
        "Writes an 8-bit value to the specified register/address"
        self.bus.write_byte_data(self.address, reg, value)
        if self.debug:
            print("I2C: Write 0x%02X to register 0x%02X" % (value, reg))

    def read(self, reg):
        "Read an unsigned byte from the I2C device"
        result = self.bus.read_byte_data(self.address, reg)
        if self.debug:
            print("I2C: Device 0x%02X returned 0x%02X from reg 0x%02X" % (self.address, result & 0xFF, reg))
        return result

    def setPWMFreq(self, freq):
        "Sets the PWM frequency"
        prescaleval = 25000000.0    # 25MHz
        prescaleval = prescaleval / 4096.0       # 12-bit
        prescaleval = prescaleval / float(freq)
        prescaleval = prescaleval - 1.0
        if self.debug:
            print("Setting PWM frequency to %d Hz" % freq)
            print("Estimated pre-scale: %d" % prescaleval)
        prescale = math.floor(prescaleval + 0.5)
        if self.debug:
            print("Final pre-scale: %d" % prescale)

        oldmode = self.read(self.__MODE1)
        newmode = (oldmode & 0x7F) | 0x10        # sleep
        self.write(self.__MODE1, newmode)        # go to sleep
        self.write(self.__PRESCALE, int(math.floor(prescale)))
        self.write(self.__MODE1, oldmode)
        time.sleep(0.005)
        self.write(self.__MODE1, oldmode | 0x80)

    def setPWM(self, channel, on, off):
        "Sets a single PWM channel"
        self.write(self.__LED0_ON_L + 4*channel, on & 0xFF)
        self.write(self.__LED0_ON_H + 4*channel, 0xff & (on >> 8))
        self.write(self.__LED0_OFF_L + 4*channel, off & 0xFF)
        self.write(self.__LED0_OFF_H + 4*channel, 0xff & (off >> 8))
        if self.debug:
            print("channel: %d  LED_ON: %d LED_OFF: %d" % (channel, on, off))

    def setDutycycle(self, channel, pulse):
        # Set the duty cycle for a specific channel
        self.setPWM(channel, 0, int(pulse * int(4096 / 100)))

    def setLevel(self, channel, value):
        # Set the level for a specific channel
        if value == 1:
            self.setPWM(channel, 0, 4095)
        else:
            self.setPWM(channel, 0, 0)

    def MotorRun(self, motor, index, speed):
        # Run the motor at a specified speed and direction
        if speed > 100:
            return
        if motor == 0:
            self.setDutycycle(self.PWMA, speed)
            if index == 0:
                print("1")
                self.setLevel(self.AIN1, 0)
                self.setLevel(self.AIN2, 1)
            else:
                print("2")
                self.setLevel(self.AIN1, 1)
                self.setLevel(self.AIN2, 0)
        else:
            self.setDutycycle(self.PWMB, speed)
            if index == 0:
                print("3")
                self.setLevel(self.BIN1, 0)
                self.setLevel(self.BIN2, 1)
            else:
                print("4")
                self.setLevel(self.BIN1, 1)
                self.setLevel(self.BIN2, 0)

    def MotorStop(self, motor):
        # Stop the motor
        if motor == 0:
            self.setDutycycle(self.PWMA, 0)
        else:
            self.setDutycycle(self.PWMB, 0)


# Example usage
# pwm = MotorControl(0x40, debug=False)
# pwm.setPWMFreq(50)