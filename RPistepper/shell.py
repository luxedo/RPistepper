#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
RPistepper Shell

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
import cmd
from time import sleep
import RPistepper as stp

#______________________________________________________________________
# classes
class Shell(cmd.Cmd):
    '''Simple command processor example.'''
    #__________________________________________________________________
    # attributes
    PINS = dict(
        M0 = [2, 3, 4, 17],
        M1 = [14, 15, 18, 23],
        M2 = [27, 22, 10, 9],
        M3 = [24, 25, 8, 7],
        M4 = [11, 0, 5, 6],
        M5 = [1, 12, 16, 20],
        M6 = [13, 19, 26, 21])
    prompt = 'RPiStepper-Shell: '
    intro = 'A Simple shell to control stepper motors with a Raspberry Pi'
    motors = {}

    #______________________________________________________________________
    # methods
    def do_new(self, line):
        '''Creates a new motor instance. If no arguments is passed, the next motor in motors list is created
        Usage: new [M0], [M1], [M2], [M3], [M4], [M5], [M6]
        '''
        if len(self.motors) >= len(self.PINS):
            print('Not enough pins for a new motor')
            return False
        args = line.split()
        if args:
            if not self._motor_arguments(args):
                return False
            for motor in args:
                pins = self.PINS[motor]
                self.motors[motor] = stp.Motor(pins)
                print('New motor {0} at pins {1}'.format(motor, pins))
        else:
            for i in range(len(self.PINS)):
                motor ='M'+str(i)
                if motor in self.motors:
                    continue
                else:
                    pins = self.PINS[motor]
                    self.motors[motor] = stp.Motor(pins)
                    print('New motor {0} at pins {1}'.format(motor, pins))
                    return False

    def do_remove(self, line):
        '''Removes a motor instance. If no arguments is passed, the last motor in motors list is removed
        Usage: remove [M0], [M1], [M2], [M3], [M4], [M5], [M6]'''
        if len(self.motors) <= 0:
            print('No motors listed')
            return False
        args = line.split()
        if args:
            if not self._motor_arguments(args):
                return False
            for motor in args:
                self.motors[motor].cleanup()
                pins = self.PINS[motor]
                del self.motors[motor]
                print('Removed motor {0}'.format(motor))
        else:
            for i in reversed(range(len(self.PINS))):
                motor ='M'+str(i)
                if motor in self.motors:
                    self.do_remove(motor)

    def do_setup(self, line):
        '''Configures motors pinout
        Usage: setup <motor> <pinout>
        '''
        pass

    def do_list(self, line):
        '''Lists active motors'''
        args = line.split()
        for motor in self.motors.items():
            print(motor)

    def do_move(self, line):
        '''Moves the motor a number of steps
        Usage: move <motor> <steps>'''
        args = line.split()
        if len(args) == 2:
            motor, steps = args
            if not self._integer_arguments([steps]) or not self._motor_arguments([motor]):
                return False
            else:
                print('Moving motor {0} {1} steps'.format(motor, steps))
                self.motors[motor].move(int(steps))
        else:
            print('Positional arguments are <motor> <steps> where motor is a motor code (M0, M1, M2, M3, M4, M5, M6) and steps is a integer ')

    def do_reset(self, line):
        '''Resets the motor to it's original position
        Usage: reset <motors>
        '''
        self._simple_method(line, 'reset')

    def do_release(self, line):
        '''Releases the motor to, setting coils to zero.
        Usage: release <motors>
        '''
        self._simple_method(line, 'release')

    def do_lock(self, line):
        '''Locks the coils to the last known position.
        Usage: lock <motors>
        '''
        self._simple_method(line, 'lock')

    def do_zero(self, line):
        '''Sets the motor to the next position which Coil_A1 and Coil_A2 are on. Sets this position as the reference (steps = 0).
        Usage: lock <motors>
        '''
        self._simple_method(line, 'zero')

    def do_sleep(self, line):
        '''Waits for some time in miliseconds.
        Usage: sleep <miliseconds>
        '''
        args = line.split()
        if not self._number_of_arguments(args, 1) or not self._integer_arguments(args):
            return False
        else:
            print('Waiting {0} miliseconds'.format(args[0]))
            sleep(float(args[0])/1000)

    def do_waitkey(self, line):
        '''Waits for an 'enter' keypress
        '''
        try:
            input()
        except:
            pass

    def do_EOF(self, line):
        '''Quits the shell'''
        print('quitting')
        for motor in self.motors:
            self.motors[motor].cleanup()
        return True

    #______________________________________________________________________
    # extra methods/ overrides
    def emptyline(self):
        pass

    def _motor_arguments(self, args):
        for motor in args:
            if not motor in self.PINS:
                print('Please use one of the motor codes:\nM0, M1, M2, M3, M4, M5, M6')
                return False
            if motor not in self.motors:
                print('Motor {0} is not listed'.format(motor))
                return False
        return True

    def _integer_arguments(self, args):
        for integer in args:
            try:
                integer = int(integer)
                return True
            except ValueError:
                print('Steps argument must be an integer')
                return False

    def _number_of_arguments(self, args, number):
        if len(args) == number:
            return True
        else:
            return False

    def _simple_method(self, line, func):
        args = line.split()
        if args:
            if not self._motor_arguments(args):
                return False
            for motor in args:
                getattr(self.motors[motor], func)()
                print('{0} motor {1}'.format(func, motor))
        else:
            print('Please sepcify at least one motor to {0}'.format(func))
            return False
