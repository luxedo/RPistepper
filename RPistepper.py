#!/usr/bin/env python2
# -*- coding: utf-8 -*-
'''
RPistepper is a library containing:
    * A class to control a stepper motor with
    * A RPi function to execute a zig-zag motion with two motors
'''

#______________________________________________________________________
# imports
import RPi.GPIO as GPIO
import time

#______________________________________________________________________
# classezz
class RPistepper(object):
    '''
    This class allows the user to control a 4 pin stepper motor using
    4 GPIO pins of a RPi. Software uses BCM mode for pin indexing.
    Arguments are a list with the 4 pins (Coil_A1, Coil_A2, Coil_B1, Coil_B2)
    The delay between steps (default = 20ms) is an optional argument
    This class is best used with the 'with' statement to propperly
    handle the cleanup of the GPIOs
    '''

    #__________________________________________________________________
    # initial setup
    GPIO.setmode(GPIO.BCM)

    #__________________________________________________________________
    # class attributes
    DELAY = 0.02

    #__________________________________________________________________
    # magic methods

    def __init__(self, pins, delay=DELAY):
        self.A1_pin, self.A2_pin, self.B1_pin, self.B2_pin = pins
        self.delay = delay
        GPIO.setup(self.A1_pin, GPIO.OUT)
        GPIO.setup(self.A2_pin, GPIO.OUT)
        GPIO.setup(self.B1_pin, GPIO.OUT)
        GPIO.setup(self.B2_pin, GPIO.OUT)
        self.order = [(1, 0, 1, 0), (0, 1, 1, 0), (0, 1, 0, 1),
            (0, 0, 1, 1), (1, 0, 0, 1), (1, 1, 0, 0)] # steps order
        self.steps_taken = 0
        self.actual_state = []
        self.release()

    def __repr__(self):
        return 'Motor at pins: {0}, {1}, {2}, {3}\nPosition: {4}'.format(self.A1_pin,
            self.A2_pin, self.B1_pin, self.B2_pin, self.actual_state)

    def __enter__(self):
        return self

    def __exit__(self, type, value, tb):
        self.reset()
        GPIO.cleanup(self.A1_pin)
        GPIO.cleanup(self.A2_pin)
        GPIO.cleanup(self.B1_pin)
        GPIO.cleanup(self.B2_pin)

    #__________________________________________________________________
    # methods
    def move(self, steps):
        '''
        Moves the motor 'steps' steps. Negative steps moves the motor backwards
        '''
        if steps < 0:
            rotation = -1
        else:
            rotation = 1
        for i in range(0, steps, rotation):
            index = self.steps_taken%len(self.order)
            self._set_step(*self.order[index])
            time.sleep(self.delay)
            self.steps_taken += rotation

    def release(self):
        '''
        Sets all pins low. Power saving mode
        '''
        self._set_step(0, 0, 0, 0)
        self.actual_state = [0, 0, 0, 0]

    def reset(self):
        '''
        Returns the motor to it's initial position
        '''
        self.move(-self.steps_taken)

    def _set_step(self, w1, w2, w3, w4):
        '''
        Sets the pins A_1, A_2, B_1, B_2, 1 or 0 (HIGH ou LOW)
        '''
        self.actual_state = [w1, w2, w3, w4]
        GPIO.output(self.A1_pin, w1)
        GPIO.output(self.A2_pin, w2)
        GPIO.output(self.B1_pin, w3)
        GPIO.output(self.B2_pin, w4)

#______________________________________________________________________
# functions
def zig_zag(motor1, motor2, amp1, amp2, delay=None):
    '''
    Executes a zig-zag moviment with two RPistepper objects.
    Arguments are: motor1 and motor2 objects and amp1, amp2, the amplitude
    of movement, a tuple (step, rep) representing the number of steps per
    iteration and the number of iterations of the following algorithm:
        Repeat rep1 times:
            1. Moves motor 2 step2*rep2 steps forward
            2. Moves motor 1 step1 steps forward
            3. Moves motor 2 step2*rep2 steps backwards
            4. Moves motor 1 step1 steps forward
        Reset to initial state
    It's possible to change the delay between steps with the 'delay' argument
    '''
    step1, rep1 = amp1
    step2, rep2 = amp2
    if delay:
        motor1.delay = delay
        motor2.delay = delay
    for i in range(rep1):
        motor2.move(step2*rep2)
        motor1.move(step1)
        motor2.move(-step2*rep2)
        motor1.move(step1)
    motor1.reset()
    motor2.reset()

#______________________________________________________________________
# main script
if __name__ == '__main__':
    # Motor Pins: BCM
    M1_pins = [17, 27, 10, 9]
    M2_pins = [14, 15, 23, 24]
    with RPistepper(M1_pins) as M1, RPistepper(M2_pins) as M2:
        zig_zag(M1, M2, (5, 10), (5, 10))   # execute zig-zag
        # for i in range(10):               # moves 20 steps,release and wait
        #     print M1
        #     M1.move(20)
        #     M1.release()
        #     raw_input('enter to execute next step')
