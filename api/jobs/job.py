from threading import Thread


class Job(Thread):

    def __init__(self, dict_configs=None, lst_config_pool=None, lst_thread_pool=None):
        super().__init__()
        self._dict_configs = dict_configs
        self._lst_config_pool = lst_config_pool
        self._lst_thread_pool = lst_thread_pool
        self._keep_running = True

    def stop(self):
        self._keep_running = False

    def _get_internal_provider_data(self, provider):
        return self._lst_config_pool.get(provider, None)
