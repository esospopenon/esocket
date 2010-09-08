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

from esocket.baseconnection import BaseConnection


class PeerConnection(BaseConnection):
    """
    When a Listener socket accepts a new connection, it creates
    a new PeerConnection object.
    """

    def __init__(self, eloop, listener, sock, connhandler,
                 timeout, maxsend, maxrecv):

        super().__init__(eloop, sock, connhandler,
                         timeout, maxsend, maxrecv)

        self._listener = listener
        self._dispatchconnected()
        self._erecv.start()

    @property
    def listener(self):
        return self._listener

    def close(self):
        super().close()
        self._listener = None

class PeerFactory(object):

    def __init__(self, eloop, handler,
                 timeout=None,
                 maxsend=sys.maxsize,
                 maxrecv=sys.maxsize):

        self._eloop = eloop
        self._handler = handler

        self._timeout = timeout
        self._maxsend = maxsend
        self._maxrecv = maxrecv

    def build(self, listener, sock):
        ch = self._handler()
        p = PeerConnection(self._eloop,
                           listener, sock, ch,
                           self._timeout,
                           self._maxsend,
                           self._maxrecv)
        return p
