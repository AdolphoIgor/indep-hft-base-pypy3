import os
import time

import api.utils.network.profit_dll
from api.jobs.internal_config_provider import InternalConfigProviders
from api.jobs.job import Job
from api.logger import logger
from api.utils.network.profit_dll_sim import ProfitDLLSim

if os.name == "nt":
    from api.utils.network.profit_dll_win import ProfitDLLWin
    from api.utils.network.profit_dll_recorder import ProfitDLLRecorder


class ConfiguratorJob(Job):

    def __init__(self, config_prov: InternalConfigProviders, order):
        super().__init__(config_prov, order)
        self._sleep_when_done = self._config.get("sleep_when_done")
        self._dct_debug_mode = self._config.get("debug_mode")

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
                        if not self._dct_debug_mode.get("enabled"):
                            dct_sys_cfg["prov_conn"] = ProfitDLLWin(
                                self._config_prov,
                                soft_key=self._config.get("soft_key"),
                                username=self._config.get("username"),
                                password=self._config.get("password")
                            )
                            api.utils.network.profit_dll_win.prov_conn = dct_sys_cfg["prov_conn"]
                            dct_sys_cfg["prov_conn"].connect()

                        elif self._dct_debug_mode.get("record"):
                            dct_sys_cfg["prov_conn"] = ProfitDLLRecorder(
                                self._config_prov,
                                soft_key=self._config.get("soft_key"),
                                username=self._config.get("username"),
                                password=self._config.get("password")
                            )
                            api.utils.network.profit_dll_win.prov_conn = dct_sys_cfg["prov_conn"]
                            dct_sys_cfg["prov_conn"].connect()

                        elif self._dct_debug_mode.get("replay"):
                            dct_sys_cfg["prov_conn"] = ProfitDLLSim(self._config_prov,
                                                                    self._dct_debug_mode.get("simulator"))

                            dct_sys_cfg["prov_conn"].play_log(
                                self._dct_debug_mode.get("replay_conf").get("date"),
                                self._dct_debug_mode.get("replay_conf").get("loop_init"),
                                self._dct_debug_mode.get("replay_conf").get("loop_end"),
                                self._dct_debug_mode.get("replay_conf").get("speed"),
                                self._dct_debug_mode.get("replay_conf").get("no_wait"),
                            )

                    if dct_sys_cfg["prov_conn"].is_connected():
                        dct_sys_cfg["connected"] = True
                        dct_sys_cfg["conn_broken_rep"] = False
                        self._set_started()
                        logger.info(f"The connection to {dct_sys_cfg.get('provider_name')} was established.")

                except Exception as e:
                    logger.error(e)
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
