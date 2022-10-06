import time

import schedule

from api.jobs.configurator_job import ConfiguratorJob
from api.jobs.executor_job import ExecutorJob
from api.jobs.pre_configurator import PreConfiguratorJob
from api.jobs.scheduler_job import SchedulerJob
from api.logger import logger

__used_classes = [PreConfiguratorJob, ConfiguratorJob, ExecutorJob, SchedulerJob]


class InternalConfigProviders:
    # keeps track of the config.json content on dict format.
    _dict_configs = {}

    # creates a custom space for any other configurarion needed.
    _lst_config_pool = [
        {
            "type": "config",
            "value": {
                "connected": False,
                "provider_connection": None,
                "provider_name": ""
            }
        },
        {
            "type": "instruments",
            "value": {}
        }
    ]

    def __init__(self):
        self._dct_sys_cfg = self.get_internal_provider_data("config")
        self._dct_pre_conf = None

    def is_running(self) -> bool:
        if self._dct_pre_conf is None:
            for dct in self.get_dict_configs().get("scheduling", []):
                if dct.get("order", -1) == 0:
                    self._dct_pre_conf = dct
                    break

        return self._dct_pre_conf is not None and self._dct_pre_conf.get("run_app", False)

    def get_internal_provider_data(self, provider) -> dict:
        ret_prov = None
        for dct_prov in self._lst_config_pool:
            if dct_prov.get("type") == provider:
                ret_prov = dct_prov.get("value")
                break

        return ret_prov

    def get_dict_configs(self):
        return self._dict_configs

    def get_lst_config_pool(self):
        return self._lst_config_pool


class IndepBase:
    # keeps track of any thread created during execution.
    _lst_thread_pool = []

    # keeps track of the configurations
    _config_prov = InternalConfigProviders()

    def __init__(self, **kwargs):
        self._test_mode = bool(kwargs.get("test_mode", False))
        self._config = kwargs.get("config", None)
        self.__start_pre_configurator()
        self.__start_scheduler()

    def __del__(self):
        while True:
            lst_thr = self.__get_alive_threads()

            if not lst_thr:
                break

            for thr in lst_thr:
                thr.get("pointer", None).join()
                logger.info(f"The thread named: {thr.get('name')} was finalized.")

    def __get_alive_threads(self):
        return list(filter(lambda x: x.get("pointer").is_alive(), self._lst_thread_pool))

    def __start_pre_configurator(self):
        prt_cls = eval(f"PreConfiguratorJob(self._config_prov, **self._config)")
        prt_cls.setDaemon(True)
        prt_cls.name = "thr_pre_configurator"
        self._lst_thread_pool.append({"group": 0, "order": 0, "name": prt_cls.name, "pointer": prt_cls})
        prt_cls.start()

    def __start_scheduler(self):
        prt_cls = eval(f"SchedulerJob(self._config_prov, order=1)")
        prt_cls.setDaemon(True)
        prt_cls.name = "thr_scheduler"
        self._lst_thread_pool.append({"group": 1, "order": 0, "name": prt_cls.name, "pointer": prt_cls})
        prt_cls.start()

    def is_all_done(self) -> bool:
        return len(self.__get_alive_threads()) > 0


class Indep(IndepBase):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def start(self):
        if self._test_mode:
            schedule.run_all()

        while self._config_prov.is_running():
            schedule.run_pending()
            time.sleep(1)

    def stop(self):
        schedule.clear()

        while not self.is_all_done():
            time.sleep(0.1)
