import socket
import time
from random import random
from random import seed

from api.jobs.job import Job


class FakeProviderJob(Job):

    def __init__(self, logger, dict_configs, lst_config_pool, lst_thread_pool, **kwargs):
        super().__init__(logger, dict_configs, lst_config_pool, lst_thread_pool)
        self._destination_path = kwargs.get("destination_path")
        self._encoder = kwargs.get("encoder")
        self._sleep_when_done = kwargs.get("sleep_when_done")
        self._connections = []
        self._server = None
        
    def __del__(self):
        for connection in self._connections:
            connection.close()

        self._server.close()
        
    def run(self) -> None:
        self._logger.info("Initializing the Fake Provider...")
        self._server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server.setblocking(False)
        self._server.bind(('127.0.0.1', 51234))
        self._server.listen(5)
        seed(0.5)

        user, pwd, cmd = "", "", ""
        try:
            while self._keep_running:
                try:
                    connection, address = self._server.accept()
                    connection.setblocking(False)
                    self._connections.append(connection)
                except BlockingIOError:
                    pass

                for connection in self._connections:
                    connection.send(b'\r\nUsername:')

                    while len(user) == 0:
                        try:
                            user = connection.recv(1024)
                            if len(user) > 0:
                                break

                        except BlockingIOError:
                            continue

                    connection.send(b'\r\nPassword:')

                    while len(pwd) == 0:
                        try:
                            pwd = connection.recv(1024)
                            if len(pwd) > 0:
                                break

                        except BlockingIOError:
                            continue

                    if len(user) > 0 and len(pwd):
                        connection.send(b'\r\nYou are connected')
                    else:
                        continue

                    while len(cmd) == 0:
                        try:
                            cmd = connection.recv(1024)
                            if str(cmd).find("sqt") < 0:
                                break

                        except BlockingIOError:
                            continue

                    try:
                        with open(self._destination_path, 'r', encoding=self._encoder) as f:

                            for line in f.readlines():
                                if not self._keep_running:
                                    break

                                connection.send(bytes(line, self._encoder))
                                time.sleep(random())

                    except BrokenPipeError:
                        user, pwd, cmd = "", "", ""
                        continue

        except BrokenPipeError:
            pass

        for connection in self._connections:
            connection.close()

        self._server.close()

        time.sleep(self._sleep_when_done)

        self._logger.info("Fake Provider was finalized.")
