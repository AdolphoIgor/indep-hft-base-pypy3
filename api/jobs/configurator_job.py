import time

from api.indep import InternalConfigProviders
from api.io.network.profit_dll import ProfitDLL
from api.jobs.job import Job
from api.logger import logger


class ConfiguratorJob(Job):

    def __init__(self, config_prov: InternalConfigProviders, order, lst_thread_pool, **kwargs):
        super().__init__(config_prov, order, lst_thread_pool)
        self._config = kwargs.get("config", None)

    def _execute(self) -> None:
        while not self._is_last_job_done():
            time.sleep(0.5)

        while self._config_prov.is_running():
            dct_sys_cfg = self._config_prov.get_internal_provider_data("config")

            if not self._config.get("connect", False) and dct_sys_cfg.get("connected", False):
                dct_sys_cfg["connected"] = False

                conn = dct_sys_cfg.get("prov_conn", None)
                if conn and conn.is_connected():
                    dct_sys_cfg["prov_conn"].disconnect()

                dct_sys_cfg["prov_conn"] = None
                dct_sys_cfg["provider_queue"] = None
                logger.info(f"The connection to MD {dct_sys_cfg.get('provider_name')} was terminated.")

            if self._config.get("connect", False) and not dct_sys_cfg.get("connected", False):
                try:
                    dct_sys_cfg["prov_conn"] = ProfitDLL(self._config_prov).connect(
                        soft_key=self._config.get("soft_key", ""),
                        username=self._config.get("username", ""),
                        password=self._config.get("password", ""),
                    )
                    dct_sys_cfg["provider_name"] = self._config.get("provider_name")
                    dct_sys_cfg["username"] = self._config.get("username", "")
                    dct_sys_cfg["password"] = self._config.get("password", "")
                    dct_sys_cfg["connected"] = True

                    logger.info(f"The connection to MD {dct_sys_cfg.get('provider_name')} was established.")

                except Exception:
                    dct_sys_cfg["connected"] = False

            time.sleep(0.5)
