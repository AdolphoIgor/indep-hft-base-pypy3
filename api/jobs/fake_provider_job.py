import socket
import time
from random import random
from random import seed

from api.jobs.job import Job


class FakeProviderJob(Job):

    def __init__(self, logger, dict_configs, lst_config_pool, lst_thread_pool, **kwargs):
        super().__init__(logger, dict_configs, lst_config_pool, lst_thread_pool)
        self.__destination_path = kwargs.get("destination_path")
        self.__encoder = kwargs.get("encoder")
        self.__sleep_when_done = kwargs.get("sleep_when_done")

    def run(self) -> None:
        self._logger.info("Initializing the Fake Provider...")

        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setblocking(False)
        server.bind(('127.0.0.1', 51234))
        server.listen(5)
        seed(0.5)

        user, pwd, cmd = "", "", ""
        connections = []
        try:
            while self._keep_running:
                try:
                    connection, address = server.accept()
                    connection.setblocking(False)
                    connections.append(connection)
                except BlockingIOError:
                    pass

                for connection in connections:
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
                        with open(self.__destination_path, 'r', encoding=self.__encoder) as f:

                            for line in f.readlines():
                                if not self._keep_running:
                                    break

                                connection.send(bytes(line, self.__encoder))
                                time.sleep(random())

                    except BrokenPipeError:
                        user, pwd, cmd = "", "", ""
                        continue

        except BrokenPipeError:
            pass

        for connection in connections:
            connection.close()

        server.close()

        time.sleep(self.__sleep_when_done)

        self._logger.info("Fake Provider was finalized.")
