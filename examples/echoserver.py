#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       echoserver.py
#
#       Copyright 2010 Espen Rønnevik <brightside@quasinet.org>
#
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.

import pyev

from esocket.ipv4 import TCPListener
from esocket.connectionhandler import ConnectionHandler


class EchoServer(ConnectionHandler):

    def connected(self, caller, data):
        pass

    def data(self, caller, data):
        term = data.index(b'\n')
        line = caller.recv(term+1)
        caller.send(line)

    def disconnected(self, caller, data):
        pass

    def error(self, caller, data):
        print('Peer event: Error {}'.format(data))

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
