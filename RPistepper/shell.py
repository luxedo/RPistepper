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
from collections import OrderedDict

#______________________________________________________________________
# classes
class Shell(cmd.Cmd, object):
    '''RPiStepper-Shell Interpreter Class'''
    #__________________________________________________________________
    # attributes
    PINS = OrderedDict()
    PINS['m0'] = stp.m0
    PINS['m1'] = stp.m1
    PINS['m2'] = stp.m2
    PINS['m3'] = stp.m3
    PINS['m4'] = stp.m4
    PINS['m5'] = stp.m5
    PINS['m6'] = stp.m6

    prompt = 'RPiStepper-Shell: '
    intro = 'A Simple shell to control stepper motors with a Raspberry Pi\nMotor codes are: m0, m1, m2, m3, m4, m5, m6'
    motors = OrderedDict()

    #______________________________________________________________________
    # magic methods
    def __enter__(self):
        return self

    def __exit__(self, type, value, tb):
        self.cleanup()

    #______________________________________________________________________
    # commands
    def do_new(self, line):
        args = line.split()
        if not self._avaliable_ports() or not self._motor_arguments(args, listed=True):
            return False
        if not args:
            for i in range(len(self.PINS)):
                motor ='m'+str(i)
                if motor not in self.motors:
                    self.do_new(motor)
                    return
        else:
            for motor in args:
                pins = self.PINS[motor]
                self.motors[motor] = stp.Motor(pins)
                print('New motor {0} at pins {1}'.format(motor, pins))

    def do_remove(self, line):
        args = line.split()
        if self._avaliable_ports(True) and not self._motor_arguments(args):
            return False
        if not args:
            for i in reversed(range(len(self.PINS))):
                motor ='m'+str(i)
                if motor in self.motors:
                    self.do_remove(motor)
                    return
        else:
            for motor in args:
                self.motors[motor].cleanup()
                pins = self.PINS[motor]
                del self.motors[motor]
                print('Removed motor {0}'.format(motor))

    def do_setup(self, line):
        args = line.split()
        if self._number_of_arguments(args, 5):
            motor, pin1, pin2, pin3, pin4 = args
            if not self._motor_arguments([motor], listed=True) or not self._integer_arguments([pin1, pin2, pin3, pin4]):
                return False
            pins = [int(pin1), int(pin2), int(pin3), int(pin4)]
            for pin in pins:
                if pins.count(pin) > 1:
                    print('Can\'t assgign the same pin for two or more coils')
                    return False
                if not (0 <= pin <= 27):
                    print('Value {0} outside the pins rangem, please use an integer between 0-27.'.format(pin))
                    return False
            print('Setting motor {0} to pins {1}'.format(motor, pins))
            self.PINS[motor] = pins

    def do_list(self, line):
        args = line.split()
        if not self.motors:
            print('No motors have been declared.')
            return False
        for key, value in self.motors.items():
            print(key, '-', value)

    def do_move(self, line):
        args = line.split()
        if self._number_of_arguments(args, 2):
            motor, steps = args
            if not self._integer_arguments([steps]) or not self._motor_arguments([motor]):
                return False
            else:
                print('Moving motor {0} {1} steps'.format(motor, steps))
                self.motors[motor].move(int(steps))
                return
        return False

    def do_reset(self, line):
        return self._simple_method(line, 'reset')

    def do_release(self, line):
        return self._simple_method(line, 'release')

    def do_lock(self, line):
        return self._simple_method(line, 'lock')

    def do_zero(self, line):
        return self._simple_method(line, 'zero')

    def do_sleep(self, line):
        args = line.split()
        if not self._number_of_arguments(args, 1) or not self._integer_arguments(args):
            return False
        else:
            print('Waiting {0} miliseconds'.format(args[0]))
            sleep(float(args[0])/1000)

    def do_repeat(self, line):
        args = line.split()
        if self._number_of_arguments(args, 1) and self._integer_arguments(args):
            repeat = Repeat()
            repeat.prompt = self.prompt[:-1]+'repeat: '
            repeat.cmdloop()
            for i in range(int(args[0])):
                for command in repeat.commands:
                    if self.onecmd(command) is False:
                        print('Incorrect commands, aborting loop')
                        return False

    def do_done(self, line):
        pass

    def do_abort(self, line):
        pass

    def do_EOF(self, line):
        print('exitting')
        self.cleanup()
        return True

    #______________________________________________________________________
    # help
    def help_new(self):
        print('Creates a new motor instance. If no arguments is passed, the next motor in motors list is created.\n Usage: new [m0], [m1], [m2], [m3], [m4], [m5], [m6]')

    def help_remove(self):
        print('Removes a motor instance. If no arguments is passed, the last motor in motors list is removed.\n Usage: remove [m0], [m1], [m2], [m3], [m4], [m5], [m6]')

    def help_setup(self):
        print('Configures motors pinout\n Usage: setup <motor> <pin1> <pin2> <pin3> <pin4> where motor is a motor code and pin1, pin2, pin3, pin4 are the connected pins as integers. The motor setup must be done before creating a new motor.')

    def help_list(self):
        print('Lists active motors.')

    def help_move(self):
        print('Moves the motor a number of steps where <steps> is an integer.\n Usage: move <motor> <steps>')

    def help_reset(self):
        print('Resets the motor to it\'s original position.\n Usage: reset <motors>')

    def help_release(self):
        print('Releases the motor to, setting coils to zero.\n Usage: release <motors>')

    def help_lock(self):
        print('Locks the coils to the last known position.\n Usage: lock <motors>')

    def help_zero(self):
        print('Sets the motor to the next position which Coil_A1 and Coil_A2 are on Sets this position as the reference (steps = 0).\n Usage: lock <motors>')

    def help_sleep(self):
        print('Waits for some time in miliseconds.\n Usage: sleep <miliseconds>')

    def help_repeat(self):
        print('Repeats the commands listed, the repeat block ends when the \'done\' command is called.\n Usage: repeat <number of repetitions>')

    def help_done(self):
        print('Concludes a repeat block.')

    def help_abort(self):
        print('Aborts the current repeat block without executing')

    def help_EOF(self):
        print('Quits the shell')

    #______________________________________________________________________
    # complete
    def complete_new(self, text, line, begidx, endidx):
        return [i for i in self.PINS if i not in self.motors]

    def complete_remove(self, text, line, begidx, endidx):
        return [i for i in self.motors]

    def complete_setup(self, text, line, begidx, endidx):
        if begidx <= 6 and endidx <=8:
            return [i for i in self.PINS if i not in self.motors]

    complete_move = complete_remove

    complete_reset = complete_remove

    complete_release = complete_remove

    complete_lock = complete_remove

    complete_zero = complete_remove

    #______________________________________________________________________
    # exit command
    do_exit = do_EOF
    help_exit = help_EOF

    #______________________________________________________________________
    # extra methods/ overrides
    def emptyline(self):
        pass

    def cleanup(self):
        for motor in self.motors:
            self.motors[motor].cleanup()

    def _motor_arguments(self, args, listed=False):
        for motor in args:
            if not motor in self.PINS:
                print('Please use one of the motor codes:\n'\
                '  m0, m1, m2, m3, m4, m5, m6')
                return False
            if motor in self.motors and listed:
                print('Motor {0} is already listed'.format(motor))
                return False
            elif motor not in self.motors and not listed:
                print('Motor {0} is not listed'.format(motor))
                return False
        return True

    def _integer_arguments(self, args):
        for integer in args:
            try:
                integer = int(integer)
                return True
            except ValueError:
                print('Argument must be an integer')
                return False

    def _number_of_arguments(self, args, number):
        if len(args) == number:
            return True
        else:
            print('Incorrect number of arguments')
            return False

    def _simple_method(self, line, method):
        args = line.split()
        if args:
            if not self._motor_arguments(args):
                return False
            for motor in args:
                getattr(self.motors[motor], method)()
                print('{0} motor {1} done'.format(method, motor))
        else:
            print('Please sepcify at least one motor to {0}'.format(method))
            return False

    def _avaliable_ports(self, zero=False):
        if len(self.motors) <= 0 and zero:
            print('No motors listed')
            return False
        elif len(self.motors) >= len(self.PINS) and not zero:
            print('Not enough pins for a new motor')
            return False
        return True

class Repeat(Shell):
    '''Repeat Interpreter Class for RPiStepper-Shell'''

    intro = ''

    def __init__(self):
        super(Repeat, self).__init__()
        self.commands = []

    def _add_command(func):
        def wrap(self, line):
            self.commands.append(func.__name__[3:]+' '+line)
        return wrap

    @_add_command
    def do_new(self, line):
        pass

    @_add_command
    def do_remove(self, line):
        pass

    @_add_command
    def do_setup(self, line):
        pass

    @_add_command
    def do_list(self, line):
        pass

    @_add_command
    def do_move(self, line):
        pass

    @_add_command
    def do_reset(self, line):
        pass

    @_add_command
    def do_release(self, line):
        pass

    @_add_command
    def do_lock(self, line):
        pass

    @_add_command
    def do_zero(self, line):
        pass

    @_add_command
    def do_sleep(self, line):
        pass

    def do_repeat(self, line):
        args = line.split()
        if self._number_of_arguments(args, 1) and self._integer_arguments(args):
            repeat_nested = Repeat()
            repeat_nested.prompt = self.prompt[:-1]+'repeat: '
            repeat_nested.cmdloop()
            self.commands += int(args[0])*(repeat_nested.commands)

    def do_abort(self, line):
        self.commands = []
        return True

    def do_EOF(self, line):
        return True

    do_done = do_EOF
