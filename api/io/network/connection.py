class Connection:

    def __init__(self, **kwargs):
        self._host = str(kwargs.get("host", ""))
        self._port = int(kwargs.get("port", -1))
        self._user = str(kwargs.get("user", ""))
        self._pwd = str(kwargs.get("pwd", ""))
        self._conn = None
        self._connected = False
        self.connect()

    def __del__(self):
        if self.is_connected:
            self.disconnect()

    def get_connection(self):
        """ Return the current connection."""
        if not self.is_connected:
            self.connect()

        return self._conn

    def set_connection(self, conn):
        """ Return the current connection."""
        if self.is_connected:
            self._conn = conn

    def is_connected(self):
        """ Verifies if the client is connected. """
        return self._connected

    def connect(self, **kwargs):
        """ Every subclass must provide its own way to connect to. """

    def disconnect(self):
        """ Every subclass must provide its own way to disconnect itself from. """

    def execute(self, msg):
        """ Every subclass must provide its own way to execute a command in the server. """
