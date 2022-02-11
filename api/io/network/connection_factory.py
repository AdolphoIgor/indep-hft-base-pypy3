from api.io.network.connection import Connection
from api.io.network.connection_quickfix import ConnectionQuickFix
from api.io.network.connection_telnet import ConnectionTelnetCedro


class ConnectionFactory:
    CONNECTION_TYPE = {
        "TELNET": 1,
        "QUICKFIX": 2
    }

    @staticmethod
    def get_connection(**kwargs) -> Connection:
        conn_type = int(kwargs.get("conn_type", -1))

        conn = None
        if conn_type == ConnectionFactory.CONNECTION_TYPE.get("TELNET"):
            conn = ConnectionTelnetCedro(**kwargs)

        if conn_type == ConnectionFactory.CONNECTION_TYPE.get("QUICKFIX"):
            conn = ConnectionQuickFix(**kwargs)

        return conn
