import time

from api.indep import InternalConfigProviders
from api.jobs.job import Job
from api.lft.algo.lft import LFT
from api.logger import logger


class ExecutorJob(Job):
    __lst_cls = [LFT]

    def __init__(self, config_prov: InternalConfigProviders, order, **kwargs):
        super().__init__(config_prov, order)
        self._config = kwargs.get("config", None)
        self._sleep_when_done = self._config.get("sleep_when_done")

    def _execute(self) -> None:
        while not self._is_last_job_done():
            time.sleep(0.5)

        while self._config_prov.is_running():
            lst_enabled_algos = [algo for algo in self._config_prov.get_dict_configs().get("algos", [])
                                 if algo.get("enabled", False)]

            # Prevents two opposed operations (Buy and Sell) for the same symbol in a particular broker.
            lst_sbl_side_bkr = []
            for algo in lst_enabled_algos:

                for thr in algo.get("threads", []):

                    dct_sbl_side_bkr = None
                    for lssb in lst_sbl_side_bkr:
                        if lssb.get("broker_id") == thr.get("broker_id"):
                            dct_sbl_side_bkr = lssb
                            break

                    if dct_sbl_side_bkr is None:
                        dct_sbl_side_bkr = {"broker_id": thr.get("broker_id"), "symbols": []}
                        lst_sbl_side_bkr.append(dct_sbl_side_bkr)

                    dct_sbl = None
                    for sbl in dct_sbl_side_bkr.get("symbols"):
                        if sbl.get("symbol") == thr.get("symbol"):
                            dct_sbl = sbl
                            break

                    if dct_sbl is None:
                        dct_sbl = {"symbol": thr.get("symbol"), "sides": []}
                        dct_sbl_side_bkr.get("symbols").append(dct_sbl)

                    side = thr.get("start_parameters").get("side")
                    lst_sides = dct_sbl.get("sides", [])
                    if side not in lst_sides:
                        lst_sides.append(side)

                    if len(set(lst_sides)) > 1:
                        raise Exception(
                            "It's not possible to sell and buy the same symbol in the particular ORM->broker.")

            # processing...
            for algo in lst_enabled_algos:

                algo_id = algo.get("id", -1)
                lst_algos_prv, lst_algos_sel_prv, dct_algo_prv = \
                    self._get_internal_provider_data("algo_providers", algo_id)

                # Starts the algorithm.
                # copy of the algo dictionary
                algo_name = f'thr_executor_{algo.get("name", "")}'
                if not dct_algo_prv.get('running', False):
                    dct_algo_prv = eval(str(algo))

                    for thread in dct_algo_prv.get("threads"):
                        # It gets the marketdata required for the algorithm.
                        bl_found = False
                        for provider in configs.get("market_data_providers", []):
                            lst_md_providers, lst_md_sel_providers, dct_md_prvd = \
                                self._get_internal_provider_data("market_data_providers", provider.get("id"))

                            for dct_md_sbl in dct_md_prvd.get('symbols'):
                                if dct_md_sbl.get('symbol').upper() == thread.get('symbol').upper():
                                    thread["market_data_instance"] = dct_md_sbl
                                    bl_found = True
                                    break

                            if bl_found:
                                break

                        lst_oms_prov, lst_oms_sel_prov, dct_oms_prvd = \
                            self._get_internal_provider_data("oms_providers", thread.get("oms_id", -1))

                        if len(dct_oms_prvd) == 0:
                            break

                        thread["oms_instance"] = dct_oms_prvd

                    dct_algo_prv['algo_name'] = algo_name
                    target = eval(f'{algo.get("algo_class")}('
                                  f'name=algo_name, '
                                  f'daemon=True, '
                                  f'keep_running=self._keep_running, '
                                  f'algo_cfg=dct_algo_prv)'
                                  )
                    self._lst_thread_pool.append({"name": algo_name, "level": level + 0.1, "pointer": target})

                    target.start()
                    dct_algo_prv['running'] = True
                    lst_algos_prv.append(dct_algo_prv)
                    logger.info(f"Initializing the algo name: {algo_name}...")

                    time.sleep(self._sleep_when_done)

            lst_disabl_algos = [algo for algo in self._config_prov.get_dict_configs().get("algos", [])
                                if algo.get("running", False) and not algo.get("enabled", False)]

            # Stops the running algoritm by a change in config.json.
            for algo in lst_disabl_algos:
                lst_algos_prv, lst_algos_sel_prv, dct_algo_prv = \
                    self._get_internal_provider_data("algo_providers", algo.get("id", -1))

                algo_name = f'thr_executor_{algo.get("name", "")}'
                thr = list(filter(lambda x: x.get("name") == algo_name, self._lst_thread_pool))[0]
                if len(thr) > 0:
                    thr.get("pointer", None).join()
                    dct_algo_prv['running'] = False
                    logger.info(f"The algo name: {thr.get('name')} was finalized.")

                time.sleep(self._sleep_when_done)

            # Cheching upon finalized threads
            lst_thr = list(filter(lambda x: x.get("level") == 5.1 and not x.get("pointer").isAlive(),
                                  self._lst_thread_pool))
            for thr in lst_thr:
                thr.get("pointer", None).join()
                prv_name = "algo_providers"
                thr_name = thr.get("name")
                lst_algos_prv, _, dct_algo_prv = self._get_internal_provider_data(prv_name, provider_algo_name=thr_name)

                if dct_algo_prv is None:
                    break

                for algo in self._config_prov.get_dict_configs().get("algos", []):
                    if algo.get('name') == dct_algo_prv.get('name'):
                        algo['enabled'] = False
                        break

                lst_algos_prv.remove(dct_algo_prv)
                self._lst_thread_pool.remove(thr)

                logger.info(f"The algo name: {thr_name} was finalized.")

                time.sleep(self._sleep_when_done)

        logger.info("Executor was finalized.")
