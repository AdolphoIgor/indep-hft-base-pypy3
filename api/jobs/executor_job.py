import time

from api.indep import InternalConfigProviders
from api.jobs.job import Job
from api.logger import logger


class ExecutorJob(Job):
    __lst_cls = []

    def __init__(self, config_prov: InternalConfigProviders, order, lst_thread_pool, **kwargs):
        super().__init__(config_prov, order, lst_thread_pool)
        self._config = kwargs.get("config", None)
        self._sleep_when_done = self._config.get("sleep_when_done")

    def _execute(self) -> None:
        while not self._is_last_job_done():
            time.sleep(0.5)

        while self._config_prov.is_running():

            lst_algos = [algo for algo in self._config_prov.get_dict_configs().get("algos", [])
                         if not algo.get("running", False) and algo.get("enabled", False)]

            # Prevents two opposed operations (Buy and Sell) for the same symbol in a particular broker.
            lst_thr = [(thr.get("symbol"), thr.get("start_param").get("side")) for thr in lst_algos]
            if len(set(lst_thr)) != len(lst_thr):
                raise Exception("It's not possible to sell and buy the same symbol in a particular broker.")

            # processing...
            for algo in lst_algos:
                if not algo.get('running', False):
                    for thr in algo.get("threads"):
                        for brkr in self._config_prov.get_dict_configs().get("brokers", []):
                            if thr.get("broker_id") == brkr.get("id"):
                                thr["broker"] = brkr
                                break

                    thr_name = f'thr_executor_{algo.get("name", "")}'
                    target = eval(f'{algo.get("algo_class")}(name={thr_name}, daemon=True, algo=algo, '
                                  f'config_prov=self._config_prov')
                    self._lst_thread_pool.append({"group": self._config.get("order"), "order": algo.get('id'),
                                                  "name": thr_name, "pointer": target})
                    target.start()
                    algo['running'] = True

            # clearing finalized threads
            lst_thr = list(filter(
                lambda x: x.get("group") == self._config.get("group") and x.get("order") == self._config.get("order")
                          and not x.get("pointer").isAlive(), self._lst_thread_pool))

            for thr in lst_thr:
                self._lst_thread_pool.remove(thr)

            time.sleep(self._sleep_when_done)

        logger.info("Executor was finalized.")
