#!/usr/bin/python

# Library for PiMotor Shield V2
# Developed by: SB Components
# Project: RPi Motor Shield - imported from https://github.com/sbcshop/MotorShield PiMotor.py updated for the PowerHorse project
# updateed to use gpiozero library instead of RPi.GPIO  

from gpiozero import PWMOutputDevice, DigitalOutputDevice, InputDevice
from time import sleep

class Motor:
    ''' Class to handle interaction with the motor pins
    Supports redefinition of "forward" and "backward" depending on how motors are connected
    Use the supplied Motorshieldtest module to test the correct configuration for your project.
    
    Arguments:
    motor = string motor pin label (i.e. "MOTOR1","MOTOR2","MOTOR3","MOTOR4") identifying the pins to which
            the motor is connected.
    config = int defining which pins control "forward" and "backward" movement.
    '''
    motorpins = {"MOTOR4":{"config":{1:{"e":32,"f":24,"r":26},2:{"e":32,"f":26,"r":24}},"arrow":1},
                 "MOTOR3":{"config":{1:{"e":19,"f":21,"r":23},2:{"e":19,"f":23,"r":21}}, "arrow":2},
                 "MOTOR2":{"config":{1:{"e":22,"f":16,"r":18},2:{"e":22,"f":18,"r":16}}, "arrow":3},
                 "MOTOR1":{"config":{1:{"e":11,"f":15,"r":13},2:{"e":11,"f":13,"r":15}},"arrow":4}}
                 
    
    def __init__(self, motor, config):
        self.testMode = False
        self.arrow = Arrow(self.motorpins[motor]["arrow"])
        self.pins = self.motorpins[motor]["config"][config]
        self.PWM = PWMOutputDevice(self.pins['e'])
        self.forward_pin = DigitalOutputDevice(self.pins['f'])
        self.reverse_pin = DigitalOutputDevice(self.pins['r'])
        self.PWM.value = 0
        self.forward_pin.off()
        self.reverse_pin.off()

    def test(self, state):
        ''' Puts the motor into test mode
        When in test mode the Arrow associated with the motor receives power on "forward"
        rather than the motor. Useful when testing your code. 
        
        Arguments:
        state = boolean
        '''
        self.testMode = state

    def forward(self, speed):
        ''' Starts the motor turning in its configured "forward" direction.

        Arguments:
        speed = Duty Cycle Percentage from 0 to 100.
        0 - stop and 100 - maximum speed
        '''    
        print("Forward")
        if self.testMode:
            self.arrow.on()
        else:
            self.PWM.value = speed / 100.0
            self.forward_pin.on()
            self.reverse_pin.off()

    def reverse(self,speed):
        ''' Starts the motor turning in its configured "reverse" direction.

        Arguments:
        speed = Duty Cycle Percentage from 0 to 100.
        0 - stop and 100 - maximum speed
     '''
        print("Reverse")
        if self.testMode:
            self.arrow.off()
        else:
            self.PWM.value = speed / 100.0
            self.forward_pin.off()
            self.reverse_pin.on()

    def stop(self):
        ''' Stops power to the motor,
     '''
        print("Stop")
        self.arrow.off()
        self.PWM.value = 0
        self.forward_pin.off()
        self.reverse_pin.off()

    def speed(self):
        ''' Control Speed of Motor,
     '''

class LinkedMotors:
    ''' Links 2 or more motors together as a set.
    
        This allows a single command to be used to control a linked set of motors
        e.g. For a 4x wheel vehicle this allows a single command to make all 4 wheels go forward.
        Starts the motor turning in its configured "forward" direction.
        
        Arguments:
        *motors = a list of Motor objects
     '''
    def __init__(self, *motors):
        self.motor = []
        for i in motors:
            print(i.pins)
            self.motor.append(i)

    def forward(self,speed):
        ''' Starts the motor turning in its configured "forward" direction.

        Arguments:
        speed = Duty Cycle Percentage from 0 to 100.
        0 - stop and 100 - maximum speed 
     '''
        for i in range(len(self.motor)):
            self.motor[i].forward(speed)

    def reverse(self,speed):
        ''' Starts the motor turning in its configured "reverse" direction.

        Arguments:
        speed = Duty Cycle Percentage from 0 to 100.
        0 - stop and 100 - maximum speed
     '''
        for i in range(len(self.motor)):
            self.motor[i].reverse(speed)

    def stop(self):
        ''' Stops power to the motor,
     '''
        for i in range(len(self.motor)):
            self.motor[i].stop()


class Sensor:
    ''' Defines a sensor connected to the sensor pins on the MotorShield
    
        Arguments:
        sensortype = string identifying which sensor is being configured.
            i.e. "IR1", "IR2", "ULTRASONIC"
        boundary = an integer specifying the minimum distance at which the sensor
            will return a Triggered response of True. 
    '''
    Triggered = False
    def iRCheck(self):
        input_state = self.echo.is_active
        if input_state:
            print("Sensor 2: Object Detected")
            self.Triggered = True
        else:
            self.Triggered = False

    def sonicCheck(self):
        print("SonicCheck has been triggered")
        time.sleep(0.333)
        self.trigger.on()
        time.sleep(0.00001)
        self.trigger.off()
        start = time.time()
        while not self.echo.is_active:
            start = time.time()
        while self.echo.is_active:
            stop = time.time()
        elapsed = stop-start
        measure = (elapsed * 34300)/2
        self.lastRead = measure
        if self.boundary > measure:
            print("Boundary breached")
            print(self.boundary)
            print(measure)
            self.Triggered = True
        else:
            self.Triggered = False
        
    sensorpins = {"IR1":{"echo":7, "check":iRCheck}, "IR2":{"echo":12, "check":iRCheck},
                  "ULTRASONIC":{"trigger":29, "echo": 31, "check":sonicCheck}}

    def trigger(self):
        ''' Executes the relevant routine that activates and takes a reading from the specified sensor.
    
        If the specified "boundary" has been breached the Sensor's Triggered attribute gets set to True.
    ''' 
        self.config["check"](self)
        print("Trigger Called")

    def __init__(self, sensortype, boundary):
        self.config = self.sensorpins[sensortype]
        self.boundary = boundary
        self.lastRead = 0
        if "trigger" in self.config:
            print("trigger")
            self.trigger = DigitalOutputDevice(self.config["trigger"])
        self.echo = InputDevice(self.config["echo"]) 

class Arrow():
    ''' Defines an object for controlling one of the LED arrows on the Motorshield.
    
        Arguments:
        which = integer label for each arrow. The arrow number if arbitrary starting with:
            1 = Arrow closest to the Motorshield's power pins and running clockwise round the board
            ...
            4 = Arrow closest to the motor pins.
    '''
    arrowpins={1:13,2:19,3:26,4:16}

    def __init__(self, which):
        self.pin = DigitalOutputDevice(self.arrowpins[which])
        self.pin.off()

    def on(self):
        self.pin.on()

    def off(self):
        self.pin.off()