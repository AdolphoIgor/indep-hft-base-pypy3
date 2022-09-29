import time

import schedule

from api.jobs.job import Job
from api.logger import logger


class SchedulerJob(Job):

    def __init__(self, dict_configs, lst_config_pool):
        super().__init__(dict_configs, lst_config_pool)

    def run(self) -> None:
        logger.info("Initializing the Scheduler...")
        while True:
            lst_scheduling = self._dict_configs.get("scheduling")

            if lst_scheduling is None:
                time.sleep(0.1)
                continue

            for shc in lst_scheduling:
                if shc.get("enabled") and not shc.get("running", False):
                    for thr in shc.get("threads"):
                        if thr.get("enabled"):
                            cls_str = f"{thr.get('target')}(" \
                                      f"self._dict_configs, " \
                                      f"self._lst_config_pool, " \
                                      f"**{thr.get('config')} " \
                                      f")"

                            prt_cls = eval(cls_str)
                            prt_cls.setDaemon(thr.get("daemon"))
                            thr_name = thr.get("thread_name")
                            prt_cls.name = thr_name
                            level = float(f"{shc.get('order')}.{thr.get('order')}")
                            self._lst_thread_pool.append({"name": thr_name, "level": level, "pointer": prt_cls})

                            schedule.every().monday.at(shc.get("dateteime")).do(prt_cls.start)
                            schedule.every().tuesday.at(shc.get("dateteime")).do(prt_cls.start)
                            schedule.every().wednesday.at(shc.get("dateteime")).do(prt_cls.start)
                            schedule.every().thursday.at(shc.get("dateteime")).do(prt_cls.start)
                            schedule.every().friday.at(shc.get("dateteime")).do(prt_cls.start)

                    shc["running"] = True

            break

        logger.info("Scheduler was finalized.")
