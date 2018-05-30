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
pulse_left = 0
pulse_right = 0

def move_forward():
    set_pulse(PULSE_STOP + 115, PULSE_STOP - 110)

def move_backward():
    set_pulse(PULSE_STOP - 90, PULSE_STOP + 95)

def move_left():
    set_pulse(PULSE_STOP - 45, PULSE_STOP - 45)

def move_right():
    set_pulse(PULSE_STOP + 50, PULSE_STOP + 50)

def set_pulse(left, right):
    global pulse_left
    global pulse_right

    pulse_left = left
    pulse_right = right

def mtr(pin, pulse_width):
    global pi

    pi.set_servo_pulsewidth(pin, pulse_width)

def main():
    global pi
    global pulse_left
    global pulse_right

    print('.', end='')

    pi = pigpio.pi()
    pi.set_mode(PIN_LEFT, pigpio.OUTPUT)
    pi.set_mode(PIN_RIGHT, pigpio.OUTPUT)

    print('Ready')

    pulse_left = PULSE_STOP
    pulse_right = PULSE_STOP

    while True:
        print(pulse_left - PULSE_STOP, pulse_right - PULSE_STOP)
        mtr(PIN_LEFT, pulse_left)
        mtr(PIN_RIGHT, pulse_right)

        ch = readchar.readkey()
        print(ch)

        if ch == 'w':
            move_forward()

        if ch == 'x':
            move_backward()

        if ch == 'a':
            move_left()

        if ch == 'd':
            move_right()

        if ch == 'q':
            pulse_left += 5

        if ch == 'z':
            pulse_left -= 5

        if ch == 'e':
            pulse_right -= 5

        if ch == 'c':
            pulse_right += 5

        if ch == 's':
            pulse_left = PULSE_STOP
            pulse_right = PULSE_STOP

        if ch == ' ':
            break

        if pulse_left < PULSE_MIN:
            pulse_left = PULSE_MIN
        if pulse_left > PULSE_MAX:
            pulse_right = PULSE_MAX
        if pulse_right < PULSE_MIN:
            pulse_right = PULSE_MIN
        if pulse_right > PULSE_MAX:
            pulse_right = PULSE_MAX


    mtr(PIN_LEFT, PULSE_OFF)
    mtr(PIN_RIGHT, PULSE_OFF)


if __name__ == "__main__":
    try:
        main()
    finally:
        print('stop!')
        mtr(PIN_LEFT, PULSE_OFF)
        mtr(PIN_RIGHT, PULSE_OFF)
        pi.stop()

