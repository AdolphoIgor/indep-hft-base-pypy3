import time

import schedule

from api.jobs.bkp_job import BackupJob
from api.jobs.configurator_job import ConfiguratorJob
from api.jobs.distributor_job import DistributorJob
from api.jobs.executor_job import ExecutorJob
from api.jobs.pre_configurator import PreConfiguratorJob
from api.jobs.producer_job import ProducerJob
from api.jobs.scheduler_job import SchedulerJob
from api.jobs.subscriber_job import SubscriberJob
from api.logger import logger

__used_classes = [PreConfiguratorJob, ConfiguratorJob, DistributorJob, ExecutorJob, ProducerJob, SchedulerJob,
                  SubscriberJob, BackupJob]


class IndepBase:
    # keeps track of any thread created during execution.
    _lst_thread_pool = []

    # keeps track of the config.json content on dict format.
    _dict_configs = {}

    # creates a custom space for any other configurarion needed.
    _lst_config_pool = [
        {"config": {}}
    ]

    def __init__(self, **kwargs):
        self._keep_running = True
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
        return list(filter(lambda x: x.get("pointer").isAlive(), self._lst_thread_pool))

    def __start_pre_configurator(self):
        prt_cls = eval(f'PreConfiguratorJob(self._dict_configs, self._lst_config_pool, **self._config)')
        prt_cls.setDaemon(True)
        prt_cls.name = "thr_pre_configurator"
        self._lst_thread_pool.append({"group": "PRECONF", "order": 1, "name": prt_cls.name, "pointer": prt_cls})
        prt_cls.start()

    def __start_scheduler(self):
        prt_cls = eval(f'SchedulerJob(self._dict_configs, self._lst_config_pool)')
        prt_cls.setDaemon(True)
        prt_cls.name = "thr_scheduler"
        self._lst_thread_pool.append({"group": "PRECONF", "order": 2, "name": prt_cls.name, "pointer": prt_cls})
        prt_cls.start()

    def is_all_done(self) -> bool:
        return not self._keep_running and len(self.__get_alive_threads()) > 0


class Indep(IndepBase):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def start(self):
        if self._test_mode:
            schedule.run_all()

        while self._keep_running:
            schedule.run_pending()
            time.sleep(1)

    def stop(self):
        self._keep_running = False
        schedule.clear()

        lst_sorted = list(filter(lambda x: x.get("group") == 'PRECONF', self._lst_thread_pool))
        lst_sorted = sorted(lst_sorted, key=lambda x: x.get("order"), reverse=True)
        for thr in lst_sorted:
            pointer = thr.get("pointer")
            if 'stop' in dir(pointer):
                pointer.stop()
