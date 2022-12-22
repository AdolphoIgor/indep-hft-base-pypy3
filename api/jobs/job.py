from threading import Thread

from api.jobs.internal_config_provider import InternalConfigProviders
from api.logger import logger


class Job(Thread):

    def __init__(self, config_prov: InternalConfigProviders, order=None):
        super().__init__()
        self._config_prov = config_prov
        self._order = order
        self._dct_sch = self._get_schedule(order=self._order)
        self._config = self._dct_sch.get("config", None)
        self._job_name = self._dct_sch.get("job", None)

    def _get_schedule(self, order=None, job=None):
        lst_sch = self._config_prov.get_dict_configs().get("scheduling", None)

        if order is None and job is None:
            return lst_sch

        dct_ret = None
        for sch in lst_sch:
            if sch.get("order", None) == order or sch.get("job", None) == job:
                dct_ret = sch
                break

        return dct_ret

    def _execute(self):
        pass

    def run(self):
        self._set_started()
        self._execute()
        self._set_done()

    def _set_started(self):
        if not self.__is_started():
            self._dct_sch["started"] = True
            self._dct_sch["done"] = False
            logger.info(f"Initializing the {self._job_name}...")

    def _set_done(self):
        if self.__is_started():
            self._dct_sch["started"] = True
            self._dct_sch["done"] = True
            logger.info(f"{self._job_name} was finalized.")

    def _is_last_job_done(self):
        dct_last_job = self._get_schedule(order=self._order - 1)
        return dct_last_job is not None and dct_last_job.get("done")

    def __is_started(self):
        return self._dct_sch.get("started", False)
