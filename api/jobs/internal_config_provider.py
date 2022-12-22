class InternalConfigProviders:
    # keeps track of any thread created during execution.
    _lst_thread_pool = []

    # keeps track of the config.json content on dict format.
    _dict_configs = {}

    # creates a custom space for any other configuration needed.
    _lst_config_pool = [
        {
            "type": "config",
            "value": {
                "keep_running": True,
                "connected": False,
                "prov_conn": None,
                "provider_name": "",
                "conn_broken_rep": False
            }
        },
        {
            "type": "instruments",
            "value": [
                {"type": "quote", "value": {}},
                {"type": "tt", "value": {}},
                {"type": "lp", "value": {}},
                {"type": "lo", "value": {}},
                {"type": "spread", "value": {}},
                {"type": "account", "value": {}},
                {"type": "orders", "value": {}},
                {"type": "progress", "value": {}}
            ]
        },
        {
            "type": "subscriptions",
            "value": [
                {"type": "quote", "value": []},
                {"type": "tt", "value": []},
                {"type": "lp", "value": []},
                {"type": "lo", "value": []},
                {"type": "spread", "value": []},
                {"type": "orders", "value": []}
            ]
        }
    ]

    def __init__(self):
        self._dct_sys_cfg = self.get_internal_provider_data("config")

    def set_keep_running(self, status: bool):
        self._dct_sys_cfg["keep_running"] = status

    def get_keep_running(self) -> bool:
        return self._dct_sys_cfg.get("keep_running")

    def get_internal_provider_data(self, provider, sublist=None):
        ret_prov = None
        for dct_prov in sublist if sublist is not None and type(sublist) is list else self._lst_config_pool:
            if dct_prov.get("type") == provider:
                ret_prov = dct_prov.get("value")
                break

        return ret_prov

    def get_dict_configs(self):
        return self._dict_configs

    def get_lst_config_pool(self):
        return self._lst_config_pool

    def get_lst_thread_pool(self):
        return self._lst_thread_pool
