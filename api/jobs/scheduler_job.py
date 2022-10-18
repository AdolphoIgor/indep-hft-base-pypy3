import time

import schedule

from api.indep import InternalConfigProviders
from api.jobs.job import Job


class SchedulerJob(Job):

    def __init__(self, config_prov: InternalConfigProviders, order, lst_thread_pool):
        super().__init__(config_prov, order, lst_thread_pool)

    def _execute(self) -> None:
        while not self._config_prov.is_running():
            time.sleep(0.1)
            continue

        lst_scheduling = self._get_shcedule()
        for shc in lst_scheduling:
            if shc.get("enabled", False):
                for thr in shc.get("threads", []):
                    if thr.get("enabled"):
                        cls_str = f"{thr.get('target')}(self._config_prov, order={shc.get('order')}, " \
                                  f"lst_thread_pool=self._lst_thread_pool, **{thr.get('config')})"
                        prt_cls = eval(cls_str)
                        prt_cls.setDaemon(thr.get("daemon"))
                        prt_cls.name = thr.get("thread_name")
                        self._lst_thread_pool.append(
                            {"group": shc.get('order'), "order": thr.get('order'), "name": prt_cls.name,
                             "pointer": prt_cls})

                        schedule.every().monday.at(shc.get("dateteime")).do(prt_cls.start)
                        schedule.every().tuesday.at(shc.get("dateteime")).do(prt_cls.start)
                        schedule.every().wednesday.at(shc.get("dateteime")).do(prt_cls.start)
                        schedule.every().thursday.at(shc.get("dateteime")).do(prt_cls.start)
                        schedule.every().friday.at(shc.get("dateteime")).do(prt_cls.start)
