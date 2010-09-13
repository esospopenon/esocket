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

import pyev

from esocket.baseesocket import BaseEsocket
from esocket.peer import PeerConnection

class Listener(BaseEsocket):
    """
    An basic listener socket, capable of listening
    for new connections.

    A listening socket produces new connections of the PeerConnection
    type, which differs from a normal Connection in that the connection
    must already exist when it is created. The listener also needs to
    hook a few events from peers in order to do some housekeeping.

    The listener supports the following events:
    * Connected - Fired when the listener is ready for connections
    * Disconnected - Fired when the listener is closed for business
    * Error - Fired when an error occured on the listener
    * Peer - Fired when a new peer tries to connect
    """

    def __init__(self, eloop, family, type, proto, peerfactory):

        super().__init__(eloop, socket.socket(family, type, proto))

        self._peers = set()
        self._peercount = 0
        self._maxpeers = sys.maxsize
        self._peerfactory = peerfactory
        self._accepting = False

        self._eaccept = pyev.Io(self._socket, pyev.EV_READ,
                                self._eloop, self._accepthandler)

#-----------------------------------------------------------------------
# Private Methods
#-----------------------------------------------------------------------

    # Handler for a peers disconnect event, the connection was
    # terminated so remove it from the set of connections
    def _disconnecthandler(self, caller, data):
        self._peers.remove(caller)
        self._peercount -= 1
        assert(self.peers == len(self._peers))

    def _listen(self, address, backlog):
        # self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._socket.bind(address)
        self._socket.listen(backlog)
        self._eaccept.start()
        self._active = True
        self._accepting = True

        self._dispatchconnected()

    def _dispatchpeer(self, data=None):
        return self._ecall('peer', data)

#-----------------------------------------------------------------------
# Event handlers
#-----------------------------------------------------------------------

    def _accepthandler(self, watcher, event):
        # There might be more that one connection waiting, so
        # loop until accept() returns an error or until listener
        # is no longer accepting connections.
        while self._accepting and not self._peercount > self._maxpeers:
            try:
                fd, addr = self._socket._accept()
                sock = socket.socket(self.family, self.type,
                                     self.proto, fileno=fd)

                # Ask the peerhandler if its okay to accept connection
                if self._dispatchpeer(addr):
                    peer = self._peerfactory.build(self, sock)

                    # The listener wants to be notified when a peer
                    # disconnects, so cleanup can be performed
                    peer.ondisconnected = self._disconnecthandler

                    # Add the peer connection to the listeners set
                    # of connections.
                    self._peers.add(peer)
                    self._peercount += 1

                    assert(self._peercount == len(self._peers))
                else:
                    # Accepthandler indicated that the connection
                    # is not wanted, close the socket.
                    sock.shutdown(socket.SHUT_RDWR)
                    sock.close()

            except socket.error:
                break

    # Delayed disconnected handler, does not signal the listener
    # is disconnected until no more peers are connected.
    def _delayhandler(self):
        if not self.peers:
            assert(len(self._peers) == 0)
            self._edelay.stop()
            self._edelay = None
            self._dispatchdisconnected

#-----------------------------------------------------------------------
# Public Properties
#-----------------------------------------------------------------------

    @property
    def isaccepting(self):
        """
        Returns True if the socket is accepting connections,
        False otherwise.
        """

        return self._accepting

    @property
    def peers(self):
        """
        Returns the number of peers connected through this
        listener
        """

        return self._peercount

    @property
    def maxpeers(self):
        """
        Return the maximum number of peers allowed to connect
        to this listener.
        """

        return self._maxpeers

    @maxpeers.setter
    def maxpeers(self, peernum):
        self._maxpeers = peernum

#-----------------------------------------------------------------------
# Public Events
#-----------------------------------------------------------------------

    @property
    def onpeer(self):
        return self._eventmap.get('peer')

    @onpeer.setter
    def onpeer(self, fn):
        self._eventmap['peer'] = fn

#-----------------------------------------------------------------------
# Public Methods
#-----------------------------------------------------------------------

    def listen(self, address, backlog=5):
        """
        Start listening on the given address.
        Backlog specifies how many connections to keep in queue
        before starting to reject peers with a 'full' message.
        """

        try:
            self._listen(address, backlog)
        except:
            self._dispatcherror()
            self._dispatchdisconnected()

    def close(self, delay=False):
        """
        Closes the listening socket.

        If kill is False, peers already connected through the
        listener will be allowed to remain connected. They can be
        forcibly removed later with the closepeers() method.
        """

        if self._active:
            self._accepting = False
            self._eaccept.stop()
            self._eaccept = None
            self._close()

        # If the listener is closed with delay as true, the
        # listener will close its own socket and stop accepting
        # new connections, but will allow peers already connected
        # to remain connected. In this case, the "disconnected" event
        # will not be dispatched until all peers have closed their
        # connection or they are forcibly removed with closepeers()

            if delay:
                self._edelay = pyev.Idle(self._eloop, self._delayhandler)
                self._edelay.start()
            else:
                self.closepeers()
                self._active = False
                self._dispatchdisconnected()

    def closepeers(self):
        """
        Disconnects all peers who connected through this listener.
        """

        for peer in self._peers:
            peer.close()

        self._peercount = 0

        if self._edelay.active:
            self._delayhandler()
