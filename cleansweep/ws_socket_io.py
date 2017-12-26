"""Monkeypatched socketio_client.SocketIO to handle WS first connection"""
from socketIO_client import SocketIO

class WebSocketSocketIO(SocketIO):
    """Monkeypatched socketio_client.SocketIO to handle web socket first connection"""
    def _negotiate_transport(self):
        """Skip this for now - we set the internal `self._transport_instance` in `_get_engineIO_session`"""
        self._debug('[engine.io transport selected] %s', self.transport_name)

    def _get_engineIO_session(self):
        """Immediately connect to websocket - the http endpoint is blocked by CloudFlare

        Copied from https://github.com/invisibleroads/socketIO-client/pull/142/files
        """
        # this variable is called by `_get_transport`, set to None
        self._engineIO_session = None
        warning_screen = self._yield_warning_screen()
        for elapsed_time in warning_screen:
            try:
                self._transport_instance = self._get_transport('websocket')
                self.transport_name = transport_name

                engineIO_packet_type, engineIO_packet_data = next(
                    self._transport_instance.recv_packet())
                break
            except (TimeoutError, ConnectionError) as e:
                if not self._wait_for_connection:
                    raise
                warning = Exception(
                    '[engine.io waiting for connection] %s' % e)
                warning_screen.throw(warning)

        assert engineIO_packet_type == 0  # engineIO_packet_type == open
        session = parse_engineIO_session(engineIO_packet_data)
        # Set the timeout on the WebSocket transport if needed, since we didn't
        # have it earlier.
        self._transport_instance.set_timeout(session.ping_timeout)
        return session(self)
