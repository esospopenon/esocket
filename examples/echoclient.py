#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Copyright 2010 Espen Rønnevik <brightside@quasinet.org>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.


import pyev

from esocket.ipv4 import TCPConnection
from esocket.connectionhandler import ConnectionHandler


class EchoClient(ConnectionHandler):

    def __init__(self):
        with open('ipsum.txt') as f:
            text = f.read()
            self.lines = text.splitlines(True)

    def sendline(self, caller):
        try:
            self.currline = self.lines.pop(0)
            caller.send(self.currline.encode('utf-8'))
        except:
            print('Done!')

            # Send server shutdown command
            caller.send('!SHUTDOWN\n'.encode('utf-8'))

            # Close our own socket
            caller.close()

    def connected(self, caller, data):
        self.sendline(caller)

    def data(self, caller, data):
        # Receive a \n terminated chunk from the socket
        # and decode the bytes into a string.
        line = caller.recvchunk(b'\n').decode('utf-8')

        # Check that the line received from the server
        # is the same as the current line just sent.
        if line != self.currline:
            print('received line - verification failed')

        self.sendline(caller)

    def disconnected(self, caller, data):
        pass

    def error(self, caller, data):
        print('Client Error: {}'.format(data))

    def timeout(self, caller, data):
        pass

def sockdisconnected(caller, data):
    loop.unloop()

if __name__ == '__main__':

    loop = pyev.default_loop()

    c = TCPConnection(loop, EchoClient(),
        {'ondisconnected': sockdisconnected})

    print('connecting')
    c.connect('localhost', 9000)
    loop.loop()
