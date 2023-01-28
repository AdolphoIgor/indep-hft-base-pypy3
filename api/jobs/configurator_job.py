import time

import api.utils.network.profit_dll
from api.jobs.internal_config_provider import InternalConfigProviders
from api.jobs.job import Job
from api.logger import logger
from api.utils.network.profit_dll import ProfitDLL


class ConfiguratorJob(Job):

    def __init__(self, config_prov: InternalConfigProviders, order):
        super().__init__(config_prov, order)
        self._sleep_when_done = self._config.get("sleep_when_done")

    def run(self) -> None:

        dct_sys_cfg = self._config_prov.get_internal_provider_data("config")
        dct_sys_cfg["provider_name"] = self._config.get("provider_name")

        while self._config_prov.get_keep_running():

            if dct_sys_cfg.get("conn_broken_rep"):
                conn = dct_sys_cfg.get("prov_conn", None)
                if conn and conn.is_connected():
                    dct_sys_cfg["prov_conn"].disconnect()
                    dct_sys_cfg["connected"] = False

            if not dct_sys_cfg.get("connected"):
                try:
                    if not dct_sys_cfg["prov_conn"]:
                        dct_sys_cfg["prov_conn"] = ProfitDLL(self._config_prov)
                        api.utils.network.profit_dll.prov_conn = dct_sys_cfg["prov_conn"]

                    dct_sys_cfg["prov_conn"].connect(
                        soft_key=self._config.get("soft_key", ""),
                        username=self._config.get("username", ""),
                        password=self._config.get("password", ""),
                    )

                    if dct_sys_cfg["prov_conn"].is_connected():
                        dct_sys_cfg["connected"] = True
                        dct_sys_cfg["conn_broken_rep"] = False
                        self._set_started()
                        logger.info(f"The connection to {dct_sys_cfg.get('provider_name')} was established.")

                except Exception:
                    dct_sys_cfg["connected"] = False

            time.sleep(self._sleep_when_done)

        conn = dct_sys_cfg.get("prov_conn", None)
        if conn and conn.is_connected():
            dct_sys_cfg["prov_conn"].disconnect()

        dct_sys_cfg["connected"] = False
        dct_sys_cfg["prov_conn"] = None
        dct_sys_cfg["provider_queue"] = None
        self._set_done()
        logger.info(f"The connection to {dct_sys_cfg.get('provider_name')} was terminated.")
