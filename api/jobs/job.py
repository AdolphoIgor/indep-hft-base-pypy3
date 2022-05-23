from threading import Thread, Lock


class Job(Thread):

    def __init__(self, logger, dict_configs=None, lst_config_pool=None, lst_thread_pool=None):
        super().__init__()
        self._logger = logger
        self._dict_configs = dict_configs
        self._lst_config_pool = lst_config_pool
        self._lst_thread_pool = lst_thread_pool
        self._keep_running = True
        self._lock = Lock()

    def stop(self):
        self._keep_running = False

    def _get_internal_provider_data(self, provider, provider_id="", provider_algo_name=""):
        """Selects from the provider's internal list of instances... """
        lst_providers = None
        for tprvd in self._lst_config_pool:
            if tprvd.get("type") == provider:
                lst_providers = tprvd.get("providers", [])
                break

        lst_sel_prvd = []
        for prvd in lst_providers:
            if prvd.get("id") == provider_id or prvd.get("algo_name", "") == provider_algo_name:
                lst_sel_prvd.append(prvd)

        dct_prvd = {}
        for prvd in lst_sel_prvd:
            if prvd.get("id") == provider_id or prvd.get("algo_name", "") == provider_algo_name:
                dct_prvd = prvd
                break

        return lst_providers, lst_sel_prvd, dct_prvd
