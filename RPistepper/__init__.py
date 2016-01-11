#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
RPistepper is a library containing:
    * A class to control a stepper motor with a RPi.
    * A function to execute a zig-zag motion with two motors.
    * A function to execute a square_spiral motion with two motors.

Copyright (C) 2015 Luiz Eduardo Amaral <luizamaral306@gmail.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

#______________________________________________________________________
# imports
import RPi.GPIO as GPIO
from time import sleep

#______________________________________________________________________
# version
__version__ = '0.3a0'

#______________________________________________________________________
# globals
m0 = [2, 3, 4, 17],
m1 = [14, 15, 18, 23],
m2 = [27, 22, 10, 9],
m3 = [24, 25, 8, 7],
m4 = [11, 0, 5, 6],
m5 = [1, 12, 16, 20],
m6 = [13, 19, 26, 21]

#______________________________________________________________________
# classes
class Motor(object):
    '''
    This class allows the user to control a 6 pin stepper motor using
    4 GPIO pins of a RPi.

    Software uses BCM mode for pin indexing.

    This class is best used with the 'with' statement to properly
    handle the cleanup of the GPIOs.

    self.steps is a property of this class that will get the number of
    steps taken from the initial position or set to a specific step,
    similar to self.move.

    In order to save power, it's advised to call self.release() when
    the motor is idle.
    '''

    #__________________________________________________________________
    # class attributes
    DELAY = 0.02
    VERBOSE = False

    #__________________________________________________________________
    # magic methods
    def __init__(self, pins, delay=DELAY, verbose=VERBOSE):
        '''
        Arguments are a list with the 4 pins (Coil_A1, Coil_A2,
        Coil_B1, Coil_B2), the delay between steps (default = 20ms) and
        verbose to display reports on the motor movements, the last two
        are optional.
        '''
        self.PINS = pins
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.PINS, GPIO.OUT)
        self.DELAY = delay
        self.VERBOSE = verbose
        self.actual_state = []
        self.locked = False
        self._step_list = [
            (1, 1, 0, 0),
            (1, 0, 1, 0),
            (0, 1, 1, 0),
            (0, 1, 0, 1),
            (0, 0, 1, 1),
            (1, 0, 0, 1)]
        self._release_all = [0]*4
        self._steps = 0
        self._set_step(self._step_list[0])
        self.release()

    def __repr__(self):
        return 'Motor at pins: {0}, Steps: {1}, Position: {2}'.format(
            self.PINS, self.steps, self.actual_state)

    def __enter__(self):
        return self

    def __exit__(self, type, value, tb):
        self.cleanup()

    #__________________________________________________________________
    # properties
    @property
    def steps(self):
        '''
        Number of steps taken from the initial position
        '''
        return self._steps

    @steps.setter
    def steps(self, value):
        steps = value - self._steps
        self.move(steps)

    #__________________________________________________________________
    # methods
    def move(self, steps):
        '''
        Moves the motor 'steps' steps. Negative steps moves the motor
        backwards
        '''
        if steps == 0:
            return
        if self.VERBOSE:
            print(str(self)+ ', Moving: {0} steps'.format(steps))
        rotation = steps//abs(steps)
        for i in range(0, steps, rotation):
            index = (self._steps + rotation)%len(self._step_list)
            self._set_step(self._step_list[index])
            sleep(self.DELAY)
            self._steps += rotation
        self.locked = True

    def release(self):
        '''
        Sets all pins low. Power saving mode
        '''
        self._set_step(self._release_all)
        self.actual_state = self._release_all
        self.locked = False

    def lock(self):
        '''
        Locks the pins in the last known step
        '''
        index = (self._steps)%len(self._step_list)
        self._set_step(self._step_list[index])
        self.locked = True

    def reset(self):
        '''
        Returns the motor to it's initial position
        '''
        self.steps = 0
        self.locked = True

    def zero(self):
        '''
        Sets the motor to the next position which Coil_A1 and Coil_A2
        are on. Sets this position as the reference (steps = 0).
        '''
        self._steps = 0
        self.steps = 6
        self.steps = 0
        self.locked = True

    def cleanup(self):
        '''
        Cleans the GPIO resources
        '''
        GPIO.cleanup(self.PINS)

    #__________________________________________________________________
    # private methods
    def _set_step(self, states):
        '''
        Sets the pins A_1, A_2, B_1, B_2, 1 or 0 (HIGH ou LOW)
        '''
        self.actual_state = states
        GPIO.output(self.PINS, states)

#______________________________________________________________________
# backwards compatibility
RPiStepper = Motor

#______________________________________________________________________
# functions
def zig_zag(motor1, motor2, amp1, amp2, delay=None):
    '''
    Executes a zig-zag movement with two RPistepper objects.
    Arguments are: motor1 and motor2 objects and amp1, amp2, the
    amplitude of movement, a tuple (step, rep) representing the number
    of steps per iteration and the number of iterations of the following
    algorithm:
        Repeat rep1 times:
            1. Moves motor 2 step2*rep2 steps forward
            2. Moves motor 1 step1 steps forward
            3. Moves motor 2 step2*rep2 steps backwards
            4. Moves motor 1 step1 steps forward
        Reset to initial state
        Release the motors
    It's possible to change the delay between steps with the 'delay'
    argument
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
    motor1.release()
    motor2.release()

def square_spiral(motor1, motor2, amplitude, delay=None):
    '''
    Executes a square spiral movement with two RPistepper objects.
    Arguments are: motor1 and motor2 objects and the amplitude of movement,
    a tuple (step, rep) representing the number of steps per iteration and
    the number of iterations of the following algorithm:
        for i in range(rep):
            1. Moves motor 2 to position i
            2. Moves motor 1 to position i
            3. Moves motor 1 to position -i
            4. Moves motor 2 to position -i
        Reset to initial state
        Release the motors
    It's possible to change the delay between steps with the 'delay'
    argument
    '''
    step, rep = amplitude
    if delay:
        motor1.delay = delay
        motor2.delay = delay
    for i in range(rep):
        motor2.steps = (i+1)*step
        motor1.steps = (i+1)*step
        motor1.steps = -(i+1)*step
        motor2.steps = -(i+1)*step
    motor1.reset()
    motor2.reset()
    motor1.release()
    motor2.release()
