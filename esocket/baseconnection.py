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

import pyev

import esocket.error
from esocket.baseesocket import BaseEsocket

class BaseConnection(BaseEsocket):
    """
    A basic connection socket.

    All connections supports the following events:
    * Connected - Dispatched when the connection has a peer
    * Disconnected - Dispatched when the peer is lost
    * Error - Dispatched when an error occured

    In addition, it will call the connectionhandler object with
    the following events:
    * Connected - Dispatched when the connection has a peer
    * Disconnected - Dispatched when the peer is lost
    * Error - Dispatched when an error occured
    * Timeout - Dispatched if a timeout occured
    * Data - Dispatched when new data has arrived
    """

    def __init__(self, eloop, sock, connhandler,
                 timeout, maxsend, maxrecv):

        super().__init__(eloop, sock)
        self._handler = connhandler

        self._esend = pyev.Io(self._socket, pyev.EV_WRITE,
                              self._eloop, self._sendhandler)

        self._erecv = pyev.Io(self._socket, pyev.EV_READ,
                              self._eloop, self._recvhandler)

        self._etimeout = None
        self.timeout = timeout

        self._sendbuf = bytearray()
        self._sendsize = 0
        self._maxsend = maxsend
        self._recvbuf = bytearray()
        self._recvsize = 0
        self._maxrecv = maxrecv

#-----------------------------------------------------------------------
# Private Methods
#-----------------------------------------------------------------------

    def _hcall(self, event, data):
        # hcall invokes the specified event method in the
        # connectionhandler, supplies it with the caller (self)
        # and data and returns a boolean value.
        try:
            return bool(getattr(self._handler, event)(self, data))
        except:
            return False

#-----------------------------------------------------------------------
# Private Event handlers and dispatchers
#-----------------------------------------------------------------------

    def _sendhandler(self, watcher, event):
        # Sendhandler tries to send as much of the sendbuffer to the
        # socket as possible. If unable to send or there is still data
        # left after the send, start the sending event and continue
        # sending at the next opportunity.
        # When there is nothing left, stop the event

        try:
            # Send as much of the sendbuffer as possible
            sent = self._socket.send(self._sendbuf)
        except socket.error as e:
            # An error means we sent nothing.
            sent = 0
        finally:
            assert(not sent < 0)
            if sent:
                self._sendbuf = self._sendbuf[sent:]
                self._sendsize -= sent

            if not self._sendsize and watcher is not None:
                # We sent everything, stop the event for now
                self._esend.stop()
            elif self._sendsize and watcher is None:
                # Data left, start the send event
                self._esend.start()

    def _recvhandler(self, watcher, event):
        # Recvhandler reads in any data available from the socket
        # and stores it in the recvbuffer. Then it signals the
        # ConnectionHandlers 'data' event, passing a copy of the
        # sendbuffer. The handler can view the data, but must call
        # recv() to remove the data. If the peer closes the socket,
        # recvhandler will close this end of the socket and
        # dispatching disconnected events.

        data = bytes()

        try:
            data = self._socket.recv(4096)
            if data:
                self._recvsize += len(data)
                if self._recvsize > self._maxrecv:
                    raise error.ReceiveOverflowError
                else:
                    self._recvbuf.extend(data)

        except error.ReceiveOverflowError as e:
            self._dispatcherror(e)

        finally:
            if not data:
                # data available but no data means peer closed socket.
                if self._recvsize:
                    # Trigger dataevent if there is anything in the
                    # receive buffer
                    self._dispatchdata(bytes(self._recvbuf))
                self.close()
            else:
                self._dispatchdata(bytes(self._recvbuf))

    def _timeouthandler(self, watcher, event):
        self._dispatchtimeout(None)

    # Event dispatchers
    def _dispatchconnected(self, data=None):
        self._ecall('connected', data)
        self._hcall('connected', data)

    def _dispatcherror(self, data=None):
        self._hcall('error', data)
        self._ecall('error', data)

    def _dispatchdisconnected(self, data=None):
        self._hcall('disconnected', data)
        self._ecall('disconnected', data)

    def _dispatchtimeout(self, data=None):
        self._hcall('timeout', data)

    def _dispatchdata(self, data=None):
        self._hcall('data', data)

#-----------------------------------------------------------------------
# Public Properties
#-----------------------------------------------------------------------

    @property
    def timeout(self):
        """
        Setting a socket timeout will trigger a timeout event every
        specified seconds. Set to None to disable.
        """
        if self._etimeout is not None:
            return self._etimeout.repeat
        else:
            return None

    @timeout.setter
    def timeout(self, seconds):
        if self._etimeout is not None:
            self._etimeout.stop()
            self._etimeout = None

        if seconds is not None:
            self._etimeout = pyev.Timer(seconds, seconds,
                                        self._eloop,
                                        self._timeoutevent)
            self._etimeout.start()

#-----------------------------------------------------------------------
# Public Methods
#-----------------------------------------------------------------------

    def close(self):
        if self._active:
            self._close()

            # Stop and release the event objects
            self._esend.stop()
            self._erecv.stop()
            self._esend = None
            self._erecv = None

            # Release the connectionhandler
            self._handler = None

            # After a close, set as inactive and
            # dispatch the disconnected event
            self._active = False
            self._dispatchdisconnected()

    def send(self, data):
        """
        Send data to the connected peer. Will raise an error if the
        amount of data exceeds the size of the sendbuffer.
        """
        try:
            self._sendsize += len(data)
            if self._sendsize > self._maxsend:
                raise error.SendOverflowError()
            self._sendbuf.extend(data)

            # Call the sendhandler and attempt to send the
            # data immediately.
            self._sendhandler(None, None)

        except error.SendOverflowError as e:
            self._dispatcherror(e)

    def recv(self, count):
        """
        Get <count> bytes from the sockets receivebuffer.
        """
        if count > self._recvsize or count < 0:
            count = self._recvsize

        recved = self._recvbuf[:count]
        self._recvbuf = self._recvbuf[count:]
        self._recvsize -= count

        return recved
