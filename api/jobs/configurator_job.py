import time
from queue import Queue

from api.indep import InternalConfigProviders
from api.io.network.profit_dll import ProfitDLL
from api.jobs.job import Job
from api.logger import logger


class ConfiguratorJob(Job):

    def __init__(self, config_prov: InternalConfigProviders, **kwargs):
        super().__init__(config_prov)
        self._config = kwargs.get("config", None)

    def run(self) -> None:
        logger.info("Initializing the Configurator...")

        while self._config_prov.is_running():
            dct_sys_cfg = self._config_prov.get_internal_provider_data("config")

            if not self._config.get("connect", False) and dct_sys_cfg.get("connected", False):
                dct_sys_cfg["connected"] = False

                conn = dct_sys_cfg.get("provider_connection", None)
                if conn and conn.is_connected():
                    dct_sys_cfg["provider_connection"].disconnect()

                dct_sys_cfg["provider_connection"] = None
                dct_sys_cfg["provider_queue"] = None
                logger.info(f"The connection to MD {dct_sys_cfg.get('provider_name', '')} was terminated.")

            if self._config.get("connect", False) and not dct_sys_cfg.get("connected", False):

                try:
                    dct_sys_cfg["provider_connection"] = ProfitDLL(self._config_prov).connect(
                        soft_key=self._config.get("soft_key", ""),
                        username=self._config.get("username", ""),
                        password=self._config.get("password", ""),
                    )
                    dct_sys_cfg["provider_queue"] = Queue()
                    dct_sys_cfg["connected"] = True

                    logger.info(f"The connection to MD {dct_sys_cfg.get('provider_name', '')} was established.")

                except Exception:
                    dct_sys_cfg["connected"] = False

            time.sleep(0.01)

        logger.info("Configurator was finalized.")
