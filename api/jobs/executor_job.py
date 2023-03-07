import time

from api.bots.hft.arbitrage import Arbitrage
from api.bots.tr.auction import Auction
from api.bots.tr.recorder import Recorder
from api.jobs.internal_config_provider import InternalConfigProviders
from api.jobs.job import Job


class ExecutorJob(Job):
    __lst_used_classes = [Arbitrage, Auction, Recorder]

    def __init__(self, config_prov: InternalConfigProviders, order):
        super().__init__(config_prov, order)
        self._sleep_when_done = self._config.get("sleep_when_done")

    def _execute(self) -> None:
        while not (self._is_last_job_started() and not self._is_last_job_done()):
            time.sleep(0.5)

        while self._config_prov.get_keep_running():

            lst_algos = [algo for algo in self._config_prov.get_dict_configs().get("algos", [])
                         if not algo.get("running", False) and algo.get("enabled", False)]

            lst_thread_pool = self._config_prov.get_lst_thread_pool()

            # processing...
            for algo in lst_algos:
                if not algo.get('running', False):
                    for thr in algo.get("threads"):
                        for brkr in self._config_prov.get_dict_configs().get("brokers", []):
                            if thr.get("broker_id") == brkr.get("id"):
                                thr["broker"] = brkr
                                break

                    thr_name = f'thr_executor_{algo.get("name").lower().replace(" ", "_")}'
                    target = eval(f'{algo.get("algo_class")}(name="{thr_name}", daemon=True, algo=algo, '
                                  f'config_prov=self._config_prov)')
                    lst_thread_pool.append({"name": thr_name, "pointer": target})
                    target.start()
                    algo['running'] = True

            # clearing finalized threads
            lst_thr = list(filter(
                lambda x: x.get("group") == self._config.get("group") and x.get("order") == self._config.get("order")
                          and not x.get("pointer").is_alive(), lst_thread_pool))

            for thr in lst_thr:
                lst_thread_pool.remove(thr)

            time.sleep(self._sleep_when_done)
