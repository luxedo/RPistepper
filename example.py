#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
RPistepper example
'''
#______________________________________________________________________
# imports
import RPistepper as stp

#______________________________________________________________________
# main test
# Motor Pins: BCM
M1_pins = [17, 27, 10, 9]
M2_pins = [14, 15, 23, 24]
with stp.Motor(M1_pins) as M1, stp.Motor(M2_pins) as M2:
    M1.VERBOSE = True
    M2.VERBOSE = True
    #__________________________________________________________________
    # zig_zag
    stp.zig_zag(M1, M2, (5, 10), (5, 10))
    #__________________________________________________________________
    # square_spiral
    stp.square_spiral(M1, M2, (5, 10))
    #__________________________________________________________________
    # some movement
    for i in range(10): # repeat 10 times
        print(M1)       # show M1 data
        M1.move(20)     # move 20 steps
        print(M1)       # show M1 data
        M1.steps = -20  # move to position -40
        M1.zero()       # recalibrates the reference position
        print(M1)       # show M1 data
        M1.steps = 0    # move to position
    #__________________________________________________________________
    # reset motors to original position
    M1.reset()
    M2.reset()
