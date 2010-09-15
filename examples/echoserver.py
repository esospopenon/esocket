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

from esocket.ipv4 import TCPListener
from esocket.connectionhandler import ConnectionHandler


class EchoServer(ConnectionHandler):

    def connected(self, caller, data):
        pass

    def data(self, caller, data):
        line = caller.recvchunk(b'\n').decode('utf-8')

        if line == '!SHUTDOWN\n':
            print('Recieved shutdown command, stopping server')
            caller.data.close()
        else:
            caller.send(line.encode('utf-8'))

    def disconnected(self, caller, data):
        pass

    def error(self, caller, data):
        print('Peer Error: {}'.format(data))

    def timeout(self, caller, data):
        pass

def sockpeer(caller, data):
    return True

def sockdisconnected(caller, data):
    loop.unloop()

if __name__ == '__main__':

    loop = pyev.default_loop()

    l = TCPListener(loop, EchoServer,
        {'ondisconnected': sockdisconnected, 'onpeer': sockpeer})

    print('listening')
    l.listen('localhost', 9000)
    loop.loop()
