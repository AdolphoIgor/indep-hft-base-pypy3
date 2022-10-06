from threading import Thread

from api.indep import InternalConfigProviders
from api.logger import logger


class Job(Thread):

    def __init__(self, config_prov: InternalConfigProviders, order=None, lst_thread_pool=None):
        super().__init__()
        self._config_prov = config_prov
        self._order = order
        self._lst_thread_pool = lst_thread_pool

    def _get_shcedule(self, order=None, job=None):
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
        dct_sch = self._get_shcedule(order=self._order)
        dct_sch["started"] = True
        dct_sch["done"] = False
        logger.info(f"Initializing the {dct_sch.get('Job')}...")

    def _set_done(self):
        dct_sch = self._get_shcedule(order=self._order)
        dct_sch["started"] = True
        dct_sch["done"] = True
        logger.info(f"{dct_sch.get('Job')} was finalized.")

    def _is_last_job_done(self):
        dct_last_job = self._get_shcedule(order=self._order - 1)
        return dct_last_job is not None and dct_last_job.get("done")
