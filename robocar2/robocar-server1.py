#!/usr/bin/env python3
# -*- coding:utf-8 -*-
#

import sys
import socketserver
import time
import threading

MY_PORT = 12340

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

    server = socketserver.TCPServer(('', MY_PORT), MyHandler)
    print('listening ...', server.socket.getsockname())
    server.serve_forever()


#####
if __name__ == '__main__':
    try:
        main()
    finally:
        print('stop!')
