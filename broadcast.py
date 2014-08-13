
import logging
import asyncio
from autobahn.asyncio.websocket import WebSocketServerProtocol
from autobahn.asyncio.websocket import WebSocketServerFactory
from datetime import datetime


logger = logging.getLogger(__name__)


def log(msg):
    log_msg = '{0} broadcast | {1}'.format(datetime.utcnow().strftime('%X'), msg)
    logger.info(log_msg)
    print(log_msg)


class BroadcastProtocol(WebSocketServerProtocol):
    """Client protocol - there is an instance per client connection."""

    def onOpen(self):
        """Register"""
        self.factory.register(self)

    def onMessage(self, payload, isBinary):
        """Broadcast msg from a client"""
        self.factory.broadcast(payload, self.peer)

    def connectionLost(self, reason):
        """Unregister on connection drop"""
        WebSocketServerProtocol.connectionLost(self, reason)
        self.factory.unregister(self)


class BroadcastServerFactory(WebSocketServerFactory):
    """Server handling client registrations and broadcasting"""

    def __init__(self, *args):
        WebSocketServerFactory.__init__(self, *args)
        self.clients = []

    def register(self, client):
        """Register a client"""
        if client not in self.clients:
            log('registered client {}'.format(client.peer))
            self.clients.append(client)

    def unregister(self, client):
        """Unregister a client"""
        if client in self.clients:
            log('unregister client {}'.format(client.peer))
            self.clients.remove(client)

    def broadcast(self, msg, author):
        """Broadcast msg to all clients but author."""
        log('broadcasting "{}"'.format(msg.decode('utf8')))
        for c in self.clients:
            if c.peer is not author:
                c.sendMessage(msg)
        log('msg sent to {0} client(s)'.format(len(self.clients) - 1))


if __name__ == '__main__':

    factory = BroadcastServerFactory()
    factory.protocol = BroadcastProtocol

    host = 'localhost'
    port = 5050
    loop = asyncio.get_event_loop()
    coro = loop.create_server(factory, host, port)
    server = loop.run_until_complete(coro)

    try:
        log('listening on {0}:{1}'.format(host, port))
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.close()
        loop.close()
