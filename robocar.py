#!/usr/bin/env python3
#
#
import os
import sys
import pigpio
import readchar
import time

MYNAME = sys.argv[0].split('/').pop()

CONF_FILE = os.environ["HOME"]+'/robot_car.conf'
print('CONF_FILE='+CONF_FILE)

PIN_LEFT = 13
PIN_RIGHT = 12

PULSE_OFF = 0
PULSE_MIN = 1000
PULSE_MAX = 2000

pi = None
Cur_Pulse = [0, 0]
Pulse_Left = 0
Pulse_Right = 0

Pulse_Stop = [ 1480, 1480 ]
Pulse_Forward = [Pulse_Stop[0] + 145, Pulse_Stop[1] - 145]
Pulse_Backward = [Pulse_Stop[0] - 90, Pulse_Stop[1] + 95]
Pulse_Left = [Pulse_Stop[0] - 45, Pulse_Stop[1]  - 45]
Pulse_Right = [Pulse_Stop[0] + 60, Pulse_Stop[1]  + 50]

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
    global Pulse_Stop
    global Pulse_Forward
    global Pulse_Backward
    global Pulse_Left
    global Pulse_Right

    if stat == None:
        Pulse_Stop = Cur_Pulse
    if stat == 'forward':
        Pulse_Forward = Cur_Pulse
    if stat == 'backward':
        Pulse_Backward = Cur_Pulse
    if stat == 'left':
        Pulse_Left = Cur_Pulse
    if stat == 'right':
        Pulse_Right = Cur_Pulse

def conf_load():
    global Pulse_Forward, Pulse_Stop
    global Pulse_Backward
    global Pulse_Left
    global Pulse_Right

    try:
      with open(CONF_FILE, 'r', encoding='utf-8') as f:
        line = f.readline().strip('\n\r')
        Pulse_Stop = list(map(int,line.split(' ')))

        line = f.readline().strip('\n\r')
        Pulse_Forward = list(map(int,line.split(' ')))

        line = f.readline().strip('\n\r')
        Pulse_Backward = list(map(int,line.split(' ')))

        line = f.readline().strip('\n\r')
        Pulse_Left = list(map(int,line.split(' ')))

        line = f.readline().strip('\n\r')
        Pulse_Right = list(map(int,line.split(' ')))

    except(FileNotFoundError):
        print('!! ' + CONF_FILE + ': not found ... use default value')

    print(Pulse_Stop)
    print(Pulse_Forward)
    print(Pulse_Backward)
    print(Pulse_Left)
    print(Pulse_Right)

def conf_save():
    with open(CONF_FILE, 'w', encoding='utf-8') as f:
        f.write(' '.join(map(str, Pulse_Stop))+'\n')
        f.write(' '.join(map(str, Pulse_Forward))+'\n')
        f.write(' '.join(map(str, Pulse_Backward))+'\n')
        f.write(' '.join(map(str, Pulse_Left))+'\n')
        f.write(' '.join(map(str, Pulse_Right))+'\n')

#
# main
#
def main():
    global pi
    global Cur_Pulse

    # init
    pi = pigpio.pi()
    pi.set_mode(17, pigpio.OUTPUT)
    pi.write(17, 1)
    pi.set_mode(PIN_LEFT, pigpio.OUTPUT)
    pi.set_mode(PIN_RIGHT, pigpio.OUTPUT)


    Cur_Pulse = Pulse_Stop
    stat_move = None

    # Ready
    print('Ready')

    while True:
        print(Cur_Pulse[0] - Pulse_Stop[0], Cur_Pulse[1] - Pulse_Stop[1])

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
            stat_move = None
            Cur_Pulse = Pulse_Stop

        if ch == ' ':
            break


    mtr(PULSE_OFF, PULSE_OFF)


if __name__ == "__main__":
    try:
        conf_load()
        main()
    finally:
        print('stop!')
        mtr(PULSE_OFF, PULSE_OFF)
        pi.stop()
        conf_save()
