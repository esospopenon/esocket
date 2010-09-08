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


class ConnectionHandler(object):

    def connected(self, sock, data):
        """ Called when the socket is connected to a peer"""
        raise NotImplementedError

    def data(self, sock, data):
        """ Called when new data is available from the socket """
        raise NotImplementedError

    def timeout(self, sock, data):
        """ Called when a timeout occured on the connection """
        raise NotImplementedError

    def error(self, sock, data):
        """ Called when something went wrong """
        raise NotImplementedError

    def disconnected(self, sock, data):
        """ Called when the connection has been lost """
        raise NotImplementedError
