#!/usr/bin/env python3
# -*- coding:utf-8 -*-
#

import socketserver
import os
import sys
import pigpio
import readchar
import time
import VL53L0X
import threading

MY_PORT = 12340

MYNAME = sys.argv[0].split('/').pop()

CONF_FILE = os.environ["HOME"]+'/robot_car.conf'
print('CONF_FILE='+CONF_FILE)

MY_PORT = 12340

PIN_LEFT = 13
PIN_RIGHT = 12

PULSE_OFF = 0
PULSE_MIN = 1000
PULSE_MAX = 2000

DISTANCE_NEAR = 250     # mm
#
pi = None
Cur_Pulse = [0, 0]
Pulse_Left = 0
Pulse_Right = 0

Pulse_Off = [PULSE_OFF, PULSE_OFF]
Pulse_Stop = [ 1480, 1480 ]
Pulse_Forward = [Pulse_Stop[0] + 145, Pulse_Stop[1] - 145]
Pulse_Backward = [Pulse_Stop[0] - 90, Pulse_Stop[1] + 95]
Pulse_Left = [Pulse_Stop[0] - 45, Pulse_Stop[1]  - 45]
Pulse_Right = [Pulse_Stop[0] + 60, Pulse_Stop[1]  + 50]

Move_Stat = None
STEP_MOVE_SEC = 1.0
AUTO_MOVE_SEC = 5.0

Tof = None
Tof_Timing = None

InChar = ''

#####
def set_stop():
    global Cur_Pulse
    global Pulse_Stop

    Cur_Pulse = Pulse_Stop

def set_forward():
    global Cur_Pulse
    global Pulse_Forward

    Cur_Pulse = Pulse_Forward

def set_backward():
    global Cur_Pulse
    global Pulse_Backward

    Cur_Pulse = Pulse_Backward

def set_left():
    global Cur_Pulse
    global Pulse_Left

    Cur_Pulse = Pulse_Left

def set_right():
    global Cur_Pulse
    global Pulse_Right

    Cur_Pulse = Pulse_Right

#
def mtr(pulse):
    mtr1(PIN_LEFT, pulse[0])
    mtr1(PIN_RIGHT, pulse[1])

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

# Auto Mode
def auto_mode():
    global Cur_Pulse
    global Tof
    global Tof_Timing
    global InChar

    stat_move = None

    last_turn = None
    sleep_unit = 0.5
    SLEEP_COUNT_MAX = 7

    sleep_count = 1
    while True:
        distance = Tof.get_distance()
        print("distance = %d cm" % (distance/10))

        if distance > DISTANCE_NEAR:
            stat_move = 'forward'
            set_forward()
            sleep_count = 1

        else:
            if last_turn != 'left':
                set_left()
                last_turn = 'left'
            else:
                set_right()
                last_turn = 'right'

            mtr(Cur_Pulse)
            for i in range(sleep_count):
                time.sleep(sleep_unit)

                set_stop()
                mtr(Cur_Pulse)
                time.sleep(Tof_Timing/1000000.00)

                distance = Tof.get_distance()
                print("i=%d " % i, "distance = %d cm" % (distance/10))
                if distance > DISTANCE_NEAR:
                    break
                if last_turn == 'left':
                    set_left()
                else:
                    set_right()
                mtr(Cur_Pulse)

            sleep_count += 1
            if sleep_count > SLEEP_COUNT_MAX:
                sleep_count = 1

            set_stop()

        mtr(Cur_Pulse)

        if InChar != '':
#            InChar = ''
            break

        time.sleep(Tof_Timing/1000000.00)

#####
def charReader():
    global InChar

    print('charReader()')

    InChar = ''
    while True:
        InChar = readchar.readchar()
        print('InChar =', InChar, ord(InChar))

        if ord(InChar) <= 0x20:
            break

    print('charReader():end')

#
# main
#
def robocar():
    global pi
    global Cur_Pulse
    global Tof
    global Tof_Timing
    global InChar

    # init
    pi = pigpio.pi()
    pi.set_mode(17, pigpio.OUTPUT)
    pi.write(17, 1)
    pi.set_mode(PIN_LEFT, pigpio.OUTPUT)
    pi.set_mode(PIN_RIGHT, pigpio.OUTPUT)


    Tof = VL53L0X.VL53L0X()
    Tof.start_ranging(VL53L0X.VL53L0X_BEST_ACCURACY_MODE)
    Tof.start_ranging(VL53L0X.VL53L0X_BETTER_ACCURACY_MODE)
    Tof_Timing = Tof.get_timing()
    if Tof_Timing < 20000:
        Tof_Timing = 20000
    print("Tof_Timing = %d ms" % (Tof_Timing/1000))

# XXX
#    t = threading.Thread(target = charReader)
#    t.daemon = True
#    t.start()

    Cur_Pulse = Pulse_Stop
    stat_move = None

    # Ready
    print('Ready')

    while True:
        print(Cur_Pulse[0] - Pulse_Stop[0], Cur_Pulse[1] - Pulse_Stop[1])
        distance = Tof.get_distance()
        if distance > 0:
            print("distance = %d cm" % (distance/10))

        mtr(Cur_Pulse)

    #    ch = readchar.readkey()
    #    print(ch)
        ch = InChar
        InChar = ''

        if ch == '@':
            auto_mode()

        if ch == 'w':
            stat_move = 'foward'
            set_forward()

        if ch == 'W':
            set_forward()
            mtr(Cur_Pulse)

            time.sleep(STEP_MOVE_SEC)

            stat_move=None
            set_stop()
            mtr(Cur_Pulse)

        if ch == 'x':
            stat_move = 'backward'
            set_backward()

        if ch == 'X':
            set_backward()
            mtr(Cur_Pulse)

            time.sleep(STEP_MOVE_SEC)

            stat_move=None
            set_stop()
            mtr(Cur_Pulse)

        if ch == 'a':
            stat_move = 'left'
            set_left()

        if ch == 'A':
            set_left()
            mtr(Cur_Pulse)

            time.sleep(STEP_MOVE_SEC)

            stat_move = None
            set_stop()
            mtr(Cur_Pulse)

        if ch == 'd':
            stat_move = 'right'
            set_right()

        if ch == 'D':
            set_right()
            mtr(Cur_Pulse)

            time.sleep(STEP_MOVE_SEC)

            stat_move = None
            set_stop()
            mtr(Cur_Pulse)

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
            set_stop()
            mtr(Cur_Pulse)

        if ch == ' ':
            t.join()
            break

        if ch != '' and ord(ch) < 0x20:
            t.join()
            break

    mtr(Pulse_Off)


#####
class MyHandler(socketserver.StreamRequestHandler):
    def __init__(self, request, client_address, server):
        self.net_wfile = None
        self.net_wfile_lock = threading.Lock()
        return socketserver.StreamRequestHandler.__init__(self, request, client_address, server)

    def setup(self):
        return socketserver.StreamRequestHandler.setup(self)

    def net_write(self, msg):
        self.net_wfile_lock.acquire()
        try:
            self.net_wfile.write(msg)
        except:
            print('net_write(): Error!')
            pass
        self.net_wfile_lock.release()

    def handle(self):
        global InChar

        self.net_wfile = self.wfile
        self.net_write('#OK\r\n'.encode('utf-8'))

        # Telnet Protocol
        #
        # mode character
        # 0xff IAC
        # 0xfd DO
        # 0x22 LINEMODE
        self.net_write(b'\xff\xfd\x22')

        while True:
            net_data = self.request.recv(1024)
            if len(net_data) == 0:
                break

            print('net_data =', net_data)

            try:
                for ch in net_data.decode('utf-8'):
                    last_chr = ch
                    InChar = ch
                    self.net_write('\r\n'.encode('utf-8'))

            except UnicodeDecodeError:
                pass

        self.net_wfile = None

    def finish(self):
        return socketserver.StreamRequestHandler.finish(self)

#####
def main():
    global MY_PORT

    if len(sys.argv) > 1:
        MY_PORT = int(sys.argv[1])

    thr_robocar = threading.Thread(target = robocar)
    thr_robocar.daemon = True
    thr_robocar.start()

    server = socketserver.TCPServer(('', MY_PORT), MyHandler)
    print('listening ...', server.socket.getsockname())
    server.serve_forever()


#####
if __name__ == "__main__":
    try:
        conf_load()
        main()
    finally:
        print('stop', end='')
        mtr(Pulse_Off)
        Tof.stop_ranging()
        pi.stop()
        conf_save()
        print('!')
