#!/usr/bin/env python2
# -*- coding: utf-8 -*-
'''
An example application using RPistepper
'''
import RPistepper as stp

M1_pins = [17, 27, 10, 9]
M2_pins = [14, 15, 23, 24]
with stp.RPistepper(M1_pins) as M1, stp.RPistepper(M2_pins) as M2:
    for i in range(10): # moves M1 20 steps, M2 5 steps, release and wait
        print M1
        M1.move(20)
        M2.move(5)
        M1.release()
        M2.release()
        raw_input('enter to execute next step')
