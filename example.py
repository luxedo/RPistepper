#!/usr/bin/env python2
# -*- coding: utf-8 -*-
'''
An example application using RPistepper
'''
import RPistepper as stp

if __name__ == '__main__':
    # Motor Pins: BCM
    M1_pins = [17, 27, 10, 9]
    M2_pins = [14, 15, 23, 24]
    with stp.RPiStepper(M1_pins) as M1, stp.RPiStepper(M2_pins) as M2:
        M1.VERBOSE = True
        M2.VERBOSE = True
        stp.zig_zag(M1, M2, (5, 10), (5, 10))   # execute zig-zag
        stp.square_spiral(M1, M2, (5, 10))      # execute square_spiral
        for i in range(10):               # repeat 10 times
            print(M1)                     # show M1 data
            M1.move(20)                   # move 20 steps
            print(M1)                     # show M1 data
            M1.steps = -20                # move to position -40
            print(M1)                     # show M1 data
            M1.steps = 0                  # move to position 0
        M1.reset()
        M2.reset()
