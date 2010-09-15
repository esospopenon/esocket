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

from esocket.baseconnection import BaseConnection

class Connection(BaseConnection):

    def __init__(self, eloop, family, type, proto, connhandler):

        super().__init__(eloop, socket.socket(family, type, proto),
                         connhandler)

    def _connect(self, address, timeout):
        try:
            self._socket.settimeout(timeout)
            self._socket.connect(address)
            self._socket.settimeout(None)
            self._erecv.start()
            self._active = True
            self._dispatchconnected()
        except socket.error as e:
            self._dispatcherror(e)

    def connect(self, address, timeout=1):
        """
        Connects to the given address. Timeout specifies how
        long the connection attempt should last before giving up.
        """
        self._connect(address, timeout)


class PeerConnection(BaseConnection):
    """
    When a Listener socket accepts a new connection, it creates
    a new PeerConnection object.
    """

    def __init__(self, eloop, sock, connhandler):

        super().__init__(eloop, sock, connhandler)

        self._active = True
        self._dispatchconnected()
        self._erecv.start()
