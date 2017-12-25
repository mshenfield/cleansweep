"""`websockets` and `socket.io` compatibility layer"""
import asyncio
import json

import websockets

class SocketIOClient(websockets.WebSocketClientProtocol):
    """WebSocketsClientProtocol implementation that automatically encodes/decodes for socket.io.

    `socket.io` expects a JSON encoded list, prefixed by a constant.  The first element is the
    name of the "event", the second (optional) is a list of arguments.  Because this is specific
    to the etherdelta api. only keyword arguments are supported for now.

    The implementation is backwards compatible. `send` automatically implements json encoding
    and the constant prefixing, and `recv` automatically json decodes and strips the prefix.
    Interfaces are compatible with `WebSocketsClientProtocol`.
    """
    SOCKET_IO_CONSTANT = '42'

    @asyncio.coroutine
    def send(self, data, **event_params):
        """Automatically prepend the socket.io constant and encode data appropriately

        Extends `send` to accept keyword arguments, which are JSON encoded.
        """
        socket_io_payload = [data, event_params]
        socket_io_data = "{constant}{payload}".format(
            constant=self.SOCKET_IO_CONSTANT,
            payload=json.dumps(socket_io_payload),
        )
        yield from super(SocketIOClient, self).send(data=socket_io_data)

    @asyncio.coroutine
    def recv(self, json_loads_kwargs=None):
        """Automatically strip the SOCKET_IO_CONSTANT and parse returned message to a python object"""
        message = ''
        while self.SOCKET_IO_CONSTANT not in message:
            message = yield from super(SocketIOClient, self).recv()

        socket_io_message = message[len(self.SOCKET_IO_CONSTANT):]
        return json.loads(socket_io_message, **json_loads_kwargs)
