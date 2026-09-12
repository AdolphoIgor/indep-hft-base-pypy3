import json
import time

import schedule

from api.jobs.configurator_job import ConfiguratorJob
from api.jobs.executor_job import ExecutorJob
from api.jobs.internal_config_provider import InternalConfigProviders
from api.logger import logger


class IndepBase:
    __lst_used_classes = [ConfiguratorJob, ExecutorJob]

    # keeps track of the configurations
    _config_prov = InternalConfigProviders()

    def __init__(self, **kwargs):
        self._test_mode = bool(kwargs.get("test_mode", False))
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
        return list(filter(lambda x: x.get("pointer").is_alive(), self._config_prov.get_lst_thread_pool()))

    def __start_pre_configurator(self):
        logger.info("Initializing the Pre-Configurator...")
        dict_configs = self._config_prov.get_dict_configs()
        if len(dict_configs) == 0:
            with open("api/config/config.json", mode="r", encoding="UTF-8") as json_file:
                dict_configs.update(json.load(json_file))

        logger.info("Pre-Configurator was finalized.")

    def __start_scheduler(self):
        logger.info("Initializing the Pre-Scheduler...")

        lst_scheduling = self._config_prov.get_dict_configs().get("scheduling", None)
        for shc in lst_scheduling:
            if shc.get("enabled", False):
                cls_str = f"{shc.get('target')}(self._config_prov, order={shc.get('order')})"
                prt_cls = eval(cls_str)
                prt_cls.setDaemon(shc.get("daemon"))
                prt_cls.name = shc.get("thread_name")
                self._config_prov.get_lst_thread_pool().append({"name": prt_cls.name, "pointer": prt_cls})

                if self._test_mode:
                    prt_cls.start()

                else:
                    schedule.every().monday.at(shc.get("date_time")).do(prt_cls.start)
                    schedule.every().tuesday.at(shc.get("date_time")).do(prt_cls.start)
                    schedule.every().wednesday.at(shc.get("date_time")).do(prt_cls.start)
                    schedule.every().thursday.at(shc.get("date_time")).do(prt_cls.start)
                    schedule.every().friday.at(shc.get("date_time")).do(prt_cls.start)

        logger.info("Pre-Scheduler was finalized.")

    def is_all_done(self) -> bool:
        return len(self.__get_alive_threads()) == 0


class Indep(IndepBase):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def start(self):
        if self._test_mode:
            return

        while self._config_prov.get_keep_running():
            schedule.run_pending()
            time.sleep(1)

    def stop(self):
        self._config_prov.set_keep_running(False)
        schedule.clear()

        while not self.is_all_done():
            time.sleep(0.1)
