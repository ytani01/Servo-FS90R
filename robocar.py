#!/usr/bin/env python3
#
#
import pigpio
import readchar
import time

PIN_LEFT = 12
PIN_RIGHT = 13

PULSE_OFF = 0
PULSE_STOP = 1480
PULSE_MIN = 1000
PULSE_MAX = 2000

pi = None
Cur_Pulse = [0, 0]
Pulse_Left = 0
Pulse_Right = 0

Pulse_Forward = [PULSE_STOP + 145, PULSE_STOP - 115]
Pulse_Backward = [PULSE_STOP - 90, PULSE_STOP + 95]
Pulse_Left = [PULSE_STOP - 45, PULSE_STOP - 45]
Pulse_Right = [PULSE_STOP + 60, PULSE_STOP + 50]

Move_Stat = None

#
def move_forward():
    global Cur_Pulse
    global Pulse_Forward

    Cur_Pulse = Pulse_Forward

def move_backward():
    global Cur_Pulse
    global Pulse_Backward

    Cur_Pulse = Pulse_Backward

def move_left():
    global Cur_Pulse
    global Pulse_Left

    Cur_Pulse = Pulse_Left

def move_right():
    global Cur_Pulse
    global Pulse_Right

    Cur_Pulse = Pulse_Right

#
def mtr(pulse_left, pulse_right):
    mtr1(PIN_LEFT, pulse_left)
    mtr1(PIN_RIGHT, pulse_right)

def mtr1(pin, pulse_width):
    global pi

    pi.set_servo_pulsewidth(pin, pulse_width)

def update_pulse(stat):
    global Cur_Pulse
    global Pulse_Foward
    global Pulse_Backward
    global Pulse_Left
    global Pulse_Right

    if stat == 'forward':
        Pulse_Foward = Cur_Pulse
    if stat == 'backward':
        Pulse_Backward = Cur_Pulse
    if stat == 'left':
        Pulse_Left = Cur_Pulse
    if stat == 'right':
        Pulse_Right = Cur_Pulse

#
# main
#
def main():
    global pi
    global Cur_Pulse

    # init
    pi = pigpio.pi()
    pi.set_mode(PIN_LEFT, pigpio.OUTPUT)
    pi.set_mode(PIN_RIGHT, pigpio.OUTPUT)

    Cur_Pulse = [PULSE_STOP, PULSE_STOP]
    stat_move = None

    # Ready
    print('Ready')

    while True:
        print(Cur_Pulse[0] - PULSE_STOP, Cur_Pulse[1] - PULSE_STOP)

        mtr(Cur_Pulse[0], Cur_Pulse[1])

        ch = readchar.readkey()
        print(ch)

        if ch == 'w':
            stat_move = 'foward'
            move_forward()

        if ch == 'x':
            stat_move = 'backward'
            move_backward()

        if ch == 'a':
            stat_move = 'left'
            move_left()

        if ch == 'd':
            stat_move = 'right'
            move_right()

        if ch == 'q':
            Cur_Pulse[0] += 5
            if Cur_Pulse[0] > PULSE_MAX:
                Cur_Pulse[0] = PULSE_MAX
            update_pulse(stat_move)

        if ch == 'z':
            Cur_Pulse[0] -= 5
            if Cur_Pulse[0] < PULSE_MIN:
                Cur_Pulse[0] = PULSE_MIN
            update_pulse(stat_move)

        if ch == 'e':
            Cur_Pulse[1] -= 5
            if Cur_Pulse[1] < PULSE_MIN:
                Cur_Pulse[1] = PULSE_MIN
            update_pulse(stat_move)

        if ch == 'c':
            Cur_Pulse[1] += 5
            if Cur_Pulse[1] > PULSE_MAX:
                Cur_Pulse[1] = PULSE_MAX
            update_pulse(stat_move)

        if ch == 's':
            Cur_Pulse = [PULSE_STOP, PULSE_STOP]

        if ch == ' ':
            break


    mtr(PULSE_OFF, PULSE_OFF)


if __name__ == "__main__":
    try:
        main()
    finally:
        print('stop!')
        mtr(PULSE_OFF, PULSE_OFF)
        pi.stop()

