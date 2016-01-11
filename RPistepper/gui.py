#!/usr/bin/env python
# -*- coding: utf-8 -*-
#______________________________________________________________________
# imports
import RPistepper as stp
from sys import version_info
from collections import OrderedDict

if version_info[0] == 3:
    import tkinter as tk
    from tkinter import ttk
else:
    import Tkinter as tk
    from Tkinter import ttk

#______________________________________________________________________
# classes
class GUI(tk.Tk):
    PINS = OrderedDict()
    PINS['m0'] = stp.m0
    PINS['m1'] = stp.m1
    PINS['m2'] = stp.m2
    PINS['m3'] = stp.m3
    PINS['m4'] = stp.m4
    PINS['m5'] = stp.m5
    PINS['m6'] = stp.m6

    B_WIDTH = 15

    def __init__(self, *args, **kwargs):
        super(GUI, self).__init__(*args, **kwargs)
        self.title('RPiStepper GUI')

        self.mainframe = ttk.Frame(self, padding=3)
        self.mainframe.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))
        self.mainframe.rowconfigure(0, weight=1)
        self.mainframe.columnconfigure(0, weight=1)

        self.menubar = tk.Menu()

        self.filemenu = tk.Menu(self.menubar, tearoff=0)
        self.filemenu.add_command(label='Exit', command=lambda: self.quit())
        self.menubar.add_cascade(label='File', menu=self.filemenu)

        self.modemenu = tk.Menu(self.menubar, tearoff=0)
        self.modemenu.add_command(label='Control Motors',
            command=self.switch_control_motors_view)
        self.modemenu.add_command(label='2D Movements',
            command=self.switch_movements_2d_view)
        self.menubar.add_cascade(label='Mode', menu=self.modemenu)

        self.helpmenu = tk.Menu(self.menubar, tearoff=0)
        self.helpmenu.add_command(label='About', command=self.about_message)
        self.menubar.add_cascade(label='Help', menu=self.helpmenu)

        self.config(menu=self.menubar)

        self.motor_block = OrderedDict()
        self.motor_object = OrderedDict()

        self.motor_label = OrderedDict()
        self.move_entry = OrderedDict()
        self.motor_button = OrderedDict()
        self.motor_status = OrderedDict()
        self.motor_status_var = OrderedDict()
        self.motor_on = OrderedDict()

        self.on_off_button = ttk.Frame(self.mainframe, border=1, relief=tk.SUNKEN)
        self.on_off_button.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S),
            padx=3)
        self.motor_view = ttk.Frame(self.mainframe, border=1, relief=tk.SUNKEN)
        self.motor_view.grid(column=0, row=1, sticky=(tk.N, tk.W, tk.E, tk.S),
            padx=3)
        self.movements_2d_view = ttk.Frame(self.mainframe, border=1, relief=tk.SUNKEN)
        self.movements_2d_view.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S),
            padx=3)

        for column, motor in enumerate(self.PINS):
            self.create_motor_block(motor, column)

        self.create_2d_movement_view()

        self.switch_movements_2d_view()
        # self.switch_control_motors_view()

    def about_message(self):
        top = tk.Toplevel()
        top.title('About RPistepper')

        msg = tk.Message(top, text='RPistepper is an application to control steper motors with a Raspberry Pi')
        msg.grid()

        button = tk.Button(top, text='Dismiss', command=top.destroy)
        button.grid()

    def update_message(self, motor):
        steps = self.motor_object[motor].steps
        if self.motor_object[motor].locked:
            status = 'locked'
        else:
            status = 'released'
        self.motor_status_var[motor].set('Motor {0}\nsteps: {1}'.format(
            status, steps))

    def switch_control_motors_view(self):
        self.movements_2d_view.grid_remove()
        self.on_off_button.grid()
        self.motor_view.grid()

    def switch_movements_2d_view(self):
        self.movements_2d_view.grid()
        self.on_off_button.grid_remove()
        self.motor_view.grid_remove()

    def create_2d_movement_view(self):
        self.zig_zag_frame = ttk.Frame(self.movements_2d_view, relief=tk.SUNKEN)

        self.zig_zag_label_0 = tk.Label(self.zig_zag_frame, text='Zig-Zag:\nChoose 2 motors')
        self.zig_zag_label_0.grid()

        self.zig_zag_checkbox_frame = ttk.Frame(self.zig_zag_frame,
            relief=tk.SUNKEN)
        self.zig_zag_checkbox_frame.grid()
        self.zig_zag_checkbox = {}

        self.zig_zag_label_x = tk.Label(self.zig_zag_checkbox_frame, text='x axis')
        self.zig_zag_label_x.grid(row=0, column=0)
        self.zig_zag_label_y = tk.Label(self.zig_zag_checkbox_frame, text='y axis')
        self.zig_zag_label_y.grid(row=0, column=1)
        for row, motor in enumerate(self.PINS):
            self.zig_zag_checkbox[motor+'_var_0'] = tk.IntVar()
            self.zig_zag_checkbox[motor+'_0'] = ttk.Checkbutton(self.zig_zag_checkbox_frame, text='motor '+motor, variable=self.zig_zag_checkbox[motor+'_var_0'])
            self.zig_zag_checkbox[motor+'_0'].grid(row=row+1, column=0)
            self.zig_zag_checkbox[motor+'_var_1'] = tk.IntVar()
            self.zig_zag_checkbox[motor+'_1'] = ttk.Checkbutton(self.zig_zag_checkbox_frame, text='motor '+motor, variable=self.zig_zag_checkbox[motor+'_var_1'])
            self.zig_zag_checkbox[motor+'_1'].grid(row=row+1, column = 1)

        self.zig_zag_label_1 = tk.Label(self.zig_zag_frame, text='Choose movement amplitude')
        self.zig_zag_label_1.grid()

        self.zig_zag_amplitude = ttk.Entry(self.zig_zag_frame, width=10)
        self.zig_zag_amplitude.insert(0, '10')
        self.zig_zag_amplitude.grid()

        self.zig_zag_label_2 = tk.Label(self.zig_zag_frame, text='Choose repetitions')
        self.zig_zag_label_2.grid()

        self.zig_zag_repetitions = ttk.Entry(self.zig_zag_frame, width=10)
        self.zig_zag_repetitions.insert(0, '10')
        self.zig_zag_repetitions.grid()

        self.zig_zag_button = ttk.Button(self.zig_zag_frame, text='Execute zig zag!',
        command=self.zig_zag_cmd)
        self.zig_zag_button.grid(pady=5)

        self.zig_zag_frame.grid()

    def create_motor_block(self, motor, column):
        '''
        Creates a motor gui element with it's buttons and status
        '''
        # setup variables
        self.motor_status_var[motor] = tk.StringVar()

        self.motor_button[motor] = OrderedDict()

        self.motor_on[motor] = True

        self.motor_button[motor]['on'] = ttk.Button(self.on_off_button,
            text='Motor '+motor, command=lambda: self.motor_button_cmd(motor))
        self.motor_button[motor]['on'].grid(column=column, row=0)

        # setup widgets
        self.motor_block[motor] = ttk.Frame(self.motor_view,
            relief=tk.SUNKEN)
        self.motor_block[motor].grid(column=column, row=1)

        self.motor_label[motor] = tk.Label(self.motor_block[motor],
            text='Motor '+motor)
        self.motor_label[motor].grid()

        self.move_entry[motor] = ttk.Entry(self.motor_block[motor], width=10)
        self.move_entry[motor].grid()

        self.motor_button[motor]['move'] = ttk.Button(self.motor_block[motor],
            text='move', command=lambda: self.move_button_cmd(motor))
        self.motor_button[motor]['move'].grid()

        self.motor_button[motor]['release'] = ttk.Button(self.motor_block[motor],
            text='release', command=lambda: self.release_button_cmd(motor))
        self.motor_button[motor]['release'].grid()

        self.motor_button[motor]['lock'] = ttk.Button(self.motor_block[motor],
            text='lock', command=lambda: self.lock_button_cmd(motor))
        self.motor_button[motor]['lock'].grid()

        self.motor_button[motor]['reset'] = ttk.Button(self.motor_block[motor],
            text='reset', command=lambda: self.reset_button_cmd(motor))
        self.motor_button[motor]['reset'].grid()

        self.motor_button[motor]['zero'] = ttk.Button(self.motor_block[motor],
            text='zero', command=lambda: self.zero_button_cmd(motor))
        self.motor_button[motor]['zero'].grid()

        self.motor_status[motor] = tk.Label(self.motor_block[motor],
            textvariable=self.motor_status_var[motor], width=self.B_WIDTH)
        self.motor_status[motor].grid()

        for child in self.motor_block[motor].winfo_children():
            child.grid_configure(padx=5, pady=5)

        self.motor_button_cmd(motor)

    def motor_button_cmd(self, motor):
        '''
        Action for the move button
        '''
        if self.motor_on[motor]:
            self.motor_block[motor].grid_remove()
            if motor in self.motor_object:
                self.motor_object[motor].cleanup()
                del self.motor_object[motor]
        else:
            self.motor_block[motor].grid()
            self.motor_object[motor] = stp.Motor(self.PINS[motor])
            self.update_message(motor)

        self.motor_on[motor] = not self.motor_on[motor]

    def move_button_cmd(self, motor):
        '''
        Action for the move button
        '''
        steps = self.move_entry[motor].get()
        try:
            steps = int(steps)
        except:
            return
        self.motor_object[motor].move(steps)
        self.update_message(motor)

    def release_button_cmd(self, motor):
        '''
        Action for the move button
        '''
        self.motor_object[motor].release()
        self.update_message(motor)

    def lock_button_cmd(self, motor):
        '''
        Action for the move button
        '''
        self.motor_object[motor].lock()
        self.update_message(motor)

    def reset_button_cmd(self, motor):
        '''
        Action for the move button
        '''
        self.motor_object[motor].reset()
        self.update_message(motor)

    def zero_button_cmd(self, motor):
        '''
        Action for the move button
        '''
        self.motor_object[motor].zero()
        self.update_message(motor)

    def zig_zag_cmd(self):
        pass
