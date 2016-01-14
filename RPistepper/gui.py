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
        self.helpmenu.add_command(label='About', command=lambda:
            self.dialog_window('About RPistepper', 'RPistepper is an application to control steper motors with a Raspberry Pi'))
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

        self.zig_zag_frame = {}
        self.zig_zag_frame['frame'] = ttk.Frame(self.movements_2d_view, relief=tk.SUNKEN, padding=10)
        self.create_function_frame(self.zig_zag_frame, 'Zig-Zag:\nChoose 2 motors')
        self.zig_zag_frame['frame'].grid(row=0, column=0)
        self.zig_zag_frame['button']['command'] = self.execute_zig_zag_cmd

        self.s_spiral_frame = {}
        self.s_spiral_frame['frame'] = ttk.Frame(self.movements_2d_view, relief=tk.SUNKEN, padding=10)
        self.create_function_frame(self.s_spiral_frame, 'Square-Spiral:\nChoose 2 motors')
        self.s_spiral_frame['frame'].grid(row=0, column=1, sticky=(tk.N, tk.S, tk.E, tk.W))
        self.s_spiral_frame['button']['command'] = self.execute_s_spiral_cmd
        self.s_spiral_frame['amp_y'].grid_remove()
        self.s_spiral_frame['rep_y'].grid_remove()
        self.s_spiral_frame['label_1y'].grid_remove()
        self.s_spiral_frame['label_2y'].grid_remove()
        self.s_spiral_frame['label_2x'].grid(row=8, column=1)
        self.s_spiral_frame['rep_x'].grid(row=9, column=1)
        self.s_spiral_frame['label_1x']['text'] = 'Amplitude'
        self.s_spiral_frame['label_2x']['text'] = 'Repetitions'

        self.switch_movements_2d_view()
        # self.switch_control_motors_view()

    def dialog_window(self, title, text):
        top = tk.Toplevel()
        top.title(title)

        msg = tk.Message(top, text=text)
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

    def create_function_frame(self, frame_dict, title):
        frame_dict['label_0'] = tk.Label(frame_dict['frame'], text=title)
        frame_dict['label_0'].grid()

        frame_dict['checkbox_frame'] = ttk.Frame(frame_dict['frame'],
            relief=tk.SUNKEN)
        frame_dict['checkbox_frame'].grid()
        frame_dict['checkbox'] = {}

        frame_dict['label_x'] = tk.Label(frame_dict['checkbox_frame'], text='x axis')
        frame_dict['label_x'].grid(row=0, column=0)
        frame_dict['label_y'] = tk.Label(frame_dict['checkbox_frame'], text='y axis')
        frame_dict['label_y'].grid(row=0, column=1)
        frame_dict['checkbox']['var_x'] = tk.IntVar()
        frame_dict['checkbox']['var_y'] = tk.IntVar()
        frame_dict['checkbox']['var_x'].set(0)
        frame_dict['checkbox']['var_y'].set(1)
        for row, motor in enumerate(self.PINS):
            frame_dict['checkbox'][motor+'_x'] = ttk.Radiobutton(
                frame_dict['checkbox_frame'], text='motor '+motor, variable=frame_dict['checkbox']['var_x'], value=row)
            frame_dict['checkbox'][motor+'_x'].grid(row=row+1, column=0)
            frame_dict['checkbox'][motor+'_y'] = ttk.Radiobutton(
                frame_dict['checkbox_frame'], text='motor '+motor, variable=frame_dict['checkbox']['var_y'], value=row)
            frame_dict['checkbox'][motor+'_y'].grid(row=row+1, column = 1)

        frame_dict['label_1x'] = tk.Label(frame_dict['checkbox_frame'], text='Amp x')
        frame_dict['label_1x'].grid(row=row+2, column=0)

        frame_dict['label_1y'] = tk.Label(frame_dict['checkbox_frame'], text='Amp y')
        frame_dict['label_1y'].grid(row=row+2, column=1)

        frame_dict['va_x'] =tk.StringVar()
        frame_dict['amp_x'] = ttk.Entry(frame_dict['checkbox_frame'], width=7, textvariable=frame_dict['va_x'])
        frame_dict['amp_x'].insert(0, '10')
        frame_dict['amp_x'].grid(row=row+3, column=0)

        frame_dict['va_y'] =tk.StringVar()
        frame_dict['amp_y'] = ttk.Entry(frame_dict['checkbox_frame'], width=7, textvariable=frame_dict['va_y'])
        frame_dict['amp_y'].insert(0, '10')
        frame_dict['amp_y'].grid(row=row+3, column=1)

        frame_dict['label_2x'] = tk.Label(frame_dict['checkbox_frame'], text='Rep x')
        frame_dict['label_2x'].grid(row=row+4, column=0)

        frame_dict['label_2y'] = tk.Label(frame_dict['checkbox_frame'], text='Rep y')
        frame_dict['label_2y'].grid(row=row+4, column=1)

        frame_dict['vr_x'] =tk.StringVar()
        frame_dict['rep_x'] = ttk.Entry(frame_dict['checkbox_frame'], width=7, textvariable=frame_dict['vr_x'])
        frame_dict['rep_x'].insert(0, '10')
        frame_dict['rep_x'].grid(row=row+5, column=0)

        frame_dict['vr_y'] =tk.StringVar()
        frame_dict['rep_y'] = ttk.Entry(frame_dict['checkbox_frame'], width=7, textvariable=frame_dict['vr_y'])
        frame_dict['rep_y'].insert(0, '10')
        frame_dict['rep_y'].grid(row=row+5, column=1)

        frame_dict['button'] = ttk.Button(frame_dict['frame'], text='Execute!')
        frame_dict['button'].grid(pady=5)

        for child in frame_dict.values():
            if hasattr(child, 'grid_configure'):
                child.grid_configure(padx=10, pady=5)

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

    def execute_zig_zag_cmd(self):
        mx = 'm'+str(self.zig_zag_frame['checkbox']['var_x'].get())
        my = 'm'+str(self.zig_zag_frame['checkbox']['var_y'].get())
        ax = int(self.zig_zag_frame['amp_x'].get())
        ay = int(self.zig_zag_frame['amp_y'].get())
        rx = int(self.zig_zag_frame['rep_x'].get())
        ry = int(self.zig_zag_frame['rep_y'].get())
        if mx == my :
            self.dialog_window('error', 'You can\'t control two motors in the same port')
            return
        else:
            motors = (stp.Motor(self.PINS[mx]), stp.Motor(self.PINS[my]))
            stp.zig_zag(*motors, (ax, rx), (ay, ry))
            for motor in motors:
                motor.cleanup()
                del motor

    def execute_s_spiral_cmd(self):
        mx = 'm'+str(self.s_spiral_frame['checkbox']['var_x'].get())
        my = 'm'+str(self.s_spiral_frame['checkbox']['var_y'].get())
        ax = int(self.s_spiral_frame['amp_x'].get())
        rx = int(self.s_spiral_frame['rep_x'].get())
        if mx == my :
            self.dialog_window('error', 'You can\'t control two motors in the same port')
            return
        else:
            motors = (stp.Motor(self.PINS[mx]), stp.Motor(self.PINS[my]))
            stp.square_spiral(*motors, (ax, rx))
            for motor in motors:
                motor.cleanup()
                del motor
