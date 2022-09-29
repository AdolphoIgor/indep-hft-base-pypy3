from threading import Thread

from api.indep import InternalConfigProviders


class Job(Thread):

    def __init__(self, config_prov: InternalConfigProviders, lst_thread_pool=None):
        super().__init__()
        self._config_prov = config_prov
        self._lst_thread_pool = lst_thread_pool
