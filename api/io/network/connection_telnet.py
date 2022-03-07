import telnetlib

from api.io.network.connection import Connection
from api.logger import logger


class ConnectionTelnetCedro(Connection):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def disconnect(self):
        if self._conn is not None:
            self._conn.get_socket().shutdown(1)
            self._conn.close()

    def connect(self):
        self._connected = False

        try:
            if self._conn is None:
                self._conn = telnetlib.Telnet(host=self._host, port=self._port)
            else:
                self.disconnect()
                self._conn.open(host=self._host, port=self._port)

            # self._conn.set_debuglevel(5)
            self._conn.write(self.to_bytes("\r\n"))
            self._conn.read_until(self.to_bytes('Username:'))
            self._conn.write(self.to_bytes(f"{self._user}\r\n"))
            self._conn.read_until(self.to_bytes("Password:"))
            self._conn.write(self.to_bytes(f"{self._pwd}\r\n"))

            self._connected = len(self._conn.read_until(self.to_bytes('You are connected'))) > 0

        except Exception as e:
            logger.error(f"ConnectionTelnetCedro to host={self._host}, port={self._port} -> error={e}")
            self._conn = None

    def execute(self, msg: bytes):
        if not self.is_connected:
            self.connect()

        self._conn.write(msg)

    @staticmethod
    def to_bytes(msg) -> bytes:
        return bytes(msg, 'UTF-8')
