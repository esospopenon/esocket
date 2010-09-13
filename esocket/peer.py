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

    def __init__(self, eloop, listener, sock, connhandler):

        super().__init__(eloop, sock, connhandler)

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

    def __init__(self, eloop, handler):

        self._eloop = eloop
        self._handler = handler

        self._timeout = None
        self._maxsend = None
        self._maxrecv = None

    def build(self, listener, sock):
        p = PeerConnection(self._eloop, listener, sock, self._handler())

        if self._timeout is not None:
            p.timeout = self._timeout
        if self._maxsend is not None:
            p.maxsend = self._maxsend
        if self._maxrecv is not None:
            p.maxrecv = self._maxrecv

        return p

    @property
    def timeout(self):
        """
        Specifies the amount of time before triggering a new peers
        timeout event. Defaults to None.
        """

        return self._timeout

    @timeout.setter
    def timeout(self, seconds):
        self._timeout = seconds

    @property
    def maxsend(self):
        """
        Specifies the maximum size of the peers sendqueue.
        """

        return self._maxsend

    @maxsend.setter
    def maxsend(self, maxvalue):
        self._maxsend = maxvalue

    @property
    def maxrecv(self):
        """
        Specifies the maximum size of the peers receivequeue.
        """

        return self._maxrecv

    @maxrecv.setter
    def maxrecv(self, maxvalue):
        self._maxrecv = maxvalue
