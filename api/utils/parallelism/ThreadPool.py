import threading
from queue import Queue


class ThreadPool:
    __count_id_worker = -1

    def __init__(self, target, max_workers=1, prefixo="Thread", queue_max_size=1):
        self.__queue = Queue(maxsize=queue_max_size)
        self.__lst_workers = []
        self.__lst_retornos = []
        self.__target = target
        self.__max_workers = max_workers
        self.__prefixo = prefixo
        self.__realimenta_lista_workers()

    def __realimenta_lista_workers(self):
        if len(self.__lst_workers) == 0:
            for i in range(self.__max_workers):
                self.__count_id_worker += 1
                name = f'{self.__prefixo}_{self.__count_id_worker}'
                self.__lst_workers.append(
                    threading.Thread(
                        target=self.__target, name=name,
                        args=(self.__queue, self.__lst_retornos, name,)
                    )
                )

        else:
            for worker in self.__lst_workers:
                if worker.ident is not None and not worker.is_alive():
                    self.__lst_workers.remove(worker)
                    self.__count_id_worker += 1
                    name = f'{self.__prefixo}_{self.__count_id_worker}'
                    self.__lst_workers.append(
                        threading.Thread(
                            target=self.__target, name=name,
                            args=(self.__queue, self.__lst_retornos, name,)
                        )
                    )

    def enfilera_job(self, **kwargs):
        if self.__queue.full():
            return False

        job = kwargs.get("job", None)

        if job is not None:
            self.__queue.put_nowait(job)

        self.__realimenta_lista_workers()

        for worker in self.__lst_workers:
            if worker.ident is None:
                worker.daemon = True
                worker.start()
                break

        return True

    def get_retorno(self) -> list:
        self.__queue.join()
        return self.__lst_retornos[:]
