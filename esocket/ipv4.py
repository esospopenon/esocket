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


import sys
import _socket as socket

from esocket.connection import Connection
from esocket.listener import Listener


class TCPConnection(Connection):

    def __init__(self, eloop, connhandler, events=None,
                timeout=None, maxsend=sys.maxsize, maxrecv=sys.maxsize):

        super().__init__(eloop, socket.AF_INET, socket.SOCK_STREAM, 0,
                         connhandler, timeout, maxsend, maxrecv)

        if events is not None:
            try:
                for e, f in events.items():
                    if e == 'onconnected':
                        self.onconnected = f
                    elif e == 'ondisconnected':
                        self.ondisconnected = f
                    elif e == 'onerror':
                        self.onerror = f
            except:
                raise ValueError

class TCPListener(Listener):

    def __init__(self, eloop, peerfactory, events=None,
                 maxpeers=sys.maxsize):

        super().__init__(eloop, socket.AF_INET, socket.SOCK_STREAM, 0,
                         peerfactory, maxpeers)

        if events is not None:
            try:
                for e, f in events.items():
                    if e == 'onconnected':
                        self.onconnected = f
                    elif e == 'ondisconnected':
                        self.ondisconnected = f
                    elif e == 'onerror':
                        self.onerror = f
                    elif e == 'onpeer':
                        self.onpeer = f
            except:
                raise ValueError
