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


"""
    esocket is an eventdriven socket library for Python 3.

    TODO: Write a description.
"""

import _socket as socket

import pyev

class BaseEsocket(object):
    """
    An abstract wrapper class for Python sockets.

    The following events are common to all esockets:
    * Connected - Called when the socket is ready for actions
    * Disconnected - Fired when socket can not perform any more actions
    * Error - Fired when an error occured while performing actions
    """

    def __init__(self, eloop, sock):
        """
        Socket can eighter be an already created socket, or a 3-item
        tuple consisting of the sockets family, type and protocol
        """
        self._socket = sock
        self._socket.setblocking(False)

        self._eloop = eloop
        self._active = False

        self._eventmap = {}

#-----------------------------------------------------------------------
# Private Methods
#-----------------------------------------------------------------------

    def _close(self):
        """
        Do the real socket close, for use by subclasses.
        """
        try:
            self.shutdown(True, True)
        except Exception as e:
            pass
        finally:
            self._socket.close()
            self._active = False

            # After a close, dispatch the disconnected event
            self._dispatchdisconnected()

    # Callhandler for events
    def _ecall(self, event, data):
        try:
            return bool(self._eventmap.get(event)(self, data))
        except:
            return False

    def _dispatchconnected(self, data=None):
        return self._ecall('connected', data)

    def _dispatcherror(self, data=None):
        return self._ecall('error', data)

    def _dispatchdisconnected(self, data=None):
        return self._ecall('disconnected', data)

#-----------------------------------------------------------------------
# Public Properties
#-----------------------------------------------------------------------

    @property
    def family(self):
        """ Returns the Esocket address family """
        return self._socket.family

    @property
    def type(self):
        """ Returns the Esocket type """
        return self._socket.type

    @property
    def proto(self):
        """ Returns the Esocket protocol"""
        return self._socket.proto

    @property
    def isactive(self):
        """
        Returns True if the socket is active, False otherwise.

        A socket is deemed active if it is connected to something
        or if it is listening for someone to connect.
        """
        return self._active

#-----------------------------------------------------------------------
# Public methods
#-----------------------------------------------------------------------

    # Subclasses must provide their own implementation of close()
    def close(self):
        raise NotImplementedError

    def shutdown(send=True, recv=True):
        if send and recv:
            self._socket.shutdown(socket.SHUT_RDWR)
        elif send and not recv:
            self._socket.shutdown(socket.SHUT_RD)
        elif recv and not send:
            self._socket.shutdown(socket.SHUT_WR)

#-----------------------------------------------------------------------
# Public Events
#-----------------------------------------------------------------------

    @property
    def onconnected(self):
        return self._eventmap.get('connected')

    @onconnected.setter
    def onconnected(self, fn):
        self._eventmap['connected'] = fn

    @property
    def ondisconnected(self):
        return self._eventmap.get('disconnected')

    @ondisconnected.setter
    def ondisconnected(self, fn):
        self._eventmap['disconnected'] = fn

    @property
    def onerror(self):
        return self._eventmap.get('error')

    @onerror.setter
    def onerror(self, fn):
        self._eventmap['error'] = fn
