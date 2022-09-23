import time
from queue import Queue

from api.jobs.job import Job
from api.logger import logger
from api.providers.oms.cedro.src.oms_cedro import CedroOMSProviderBasic, CedroOMSProvider


class ConfiguratorJob(Job):
    _lst_cls = [CedroOMSProviderBasic, CedroOMSProvider]

    def __init__(self, dict_configs, lst_config_pool, **kwargs):
        super().__init__(dict_configs, lst_config_pool)
        self._config = kwargs.get("config", None)

    def run(self) -> None:
        logger.info("Initializing the Configurator...")

        while self._keep_running:
            dct_sys_cfg = self._get_internal_provider_data("config")

            if not self._config.get("connect", False) and dct_sys_cfg.get("connected", False):
                self._keep_running = False
                dct_sys_cfg["connected"] = False
                dct_sys_cfg["provider_connection"] = None
                dct_sys_cfg["provider_queue"] = None
                logger.info(f"The connection to MD {dct_sys_cfg.get('provider_name', '')} was terminated.")

            if self._config.get("connect", False) and not dct_sys_cfg.get("connected", False):

                try:
                    md_prov = Connection(
                        username=self._config.get('username', ''),
                        password=self._config.get('password', ''),
                    )
                    dct_sys_cfg["provider_connection"] = md_prov
                    dct_sys_cfg["provider_queue"] = Queue()
                    dct_sys_cfg["connected"] = True

                    logger.info(f"The connection to MD {dct_sys_cfg.get('provider_name', '')} was established.")

                except Exception:
                    dct_sys_cfg["connected"] = False

                finally:
                    self._keep_running = True

            time.sleep(0.01)

        logger.info("Configurator was finalized.")
