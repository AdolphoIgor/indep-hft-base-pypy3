import time

from api.jobs.job import Job
from api.lft.algo.lft import LFT


class ExecutorJob(Job):
    __lst_cls = [LFT]

    def __init__(self, logger, dict_configs, lst_config_pool, lst_thread_pool, **kwargs):
        super().__init__(logger, dict_configs, lst_config_pool, lst_thread_pool)
        self.__sleep_when_done = kwargs.get("sleep_when_done")
        self.__backtest_filename = kwargs.get("backtest_filename")
        self.__encoder = kwargs.get("encoder")

    def run(self) -> None:
        """
            The executor builds a pool of the negotiation algorithms which is used to start the tradings.
        """
        self._logger.info("Initializing the Executor...")

        while self._keep_running:

            configs = self._dict_configs.get("configs", {})
            if len(configs) == 0:
                time.sleep(1)
                continue

            if configs.get("online", False):
                lst_algos = self._dict_configs.get("algos", [])

                # Prevents two opposed operations (Buy and Sell) for the same symbol in a partiicular broker.
                lst_sbl_side_bkr = []
                for algo in lst_algos:
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
                for algo in lst_algos:

                    algo_id = algo.get("id", -1)
                    lst_algos_prv, lst_algos_sel_prv, dct_algo_prv = \
                        self._get_internal_provider_data("algo_providers", algo_id)

                    '''
                    ----------------------------------------------------------------------------------------------------
                    System Recovery:
                    ----------------------------------------------------------------------------------------------------
                    For situarions when the system is restarted (and the content of 'oms_providers' and 'algo' is 
                    recovered by the OMS_MGR thread from the propper log file, since the thread was running, it is
                    absolutelly necessary to restart it. This approach has been verified here.
                    
                    algo_name = f'thr_executor_{algo.get("name", "")}'
                    algo_running = False
                    if len(dct_algo_prv) > 0 and dct_algo_prv.get("running", False):
                        lst_thr = list(filter(lambda x: x.get("level") == 5.1, self._lst_thread_pool))
                        for thr in lst_thr:
                            if thr.get("name") == algo_name and thr.get("pointer").is_alive():
                                algo_running = True
                                break
                    '''

                    # Starts the algorithm.
                    # copy of the algo dictionary
                    algo_name = f'thr_executor_{algo.get("name", "")}'
                    if algo.get("enabled", False) and not dct_algo_prv.get('running', False):
                        dct_algo_prv = eval(str(algo))

                        # TODO: AJUSTAR PARA PEGAR O ARQUIVO DE BACKTEST DO PROJETO DE TREINAMENTO.
                        '''
                        dct_backtest_file = {}
                        with open(self.__backtest_filename, mode='r', encoding=self.__encoder) as json_file:
                            dct_backtest_file.update(json.load(json_file))

                        for bcktst in dct_backtest_file.get("backtests", []):
                            if bcktst.get("algo_name") == algo.get("name", ""):
                                dct_algo_prv.get("stop_parameters")["perc_trailing"] = bcktst.get("per_trl")
                                break
                        '''

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

                            complement = {
                                "orders": [
                                    {
                                        "algo_id": algo_id,
                                        "algo_name": algo.get("name", ""),
                                        "thread_symbol": thread.get("symbol", ""),
                                        "thread_oms_id": thread.get("oms_id", ""),
                                        "thread_broker_id": thread.get("broker_id", ""),
                                        "status": None,
                                        "orders": {
                                            "sent": [],
                                            "received": []
                                        }
                                    }
                                ],
                                "positions": [
                                    {
                                        "algo_id": algo_id,
                                        "algo_name": algo.get("name", ""),
                                        "thread_symbol": thread.get("symbol", ""),
                                        "thread_oms_id": thread.get("oms_id", ""),
                                        "thread_broker_id": thread.get("broker_id", ""),
                                        "order_id": -1
                                    }
                                ]
                            }
                            dct_oms_prvd.update(complement)
                            thread["oms_instance"] = dct_oms_prvd

                        # Each algorithm will receive its own context to pe and check its orders:
                        # Orders must take place in lst_oms_sel_prov->(oms)->orders->orders->send and every provider's
                        # message received will be placed at sel_prov->(oms)->orders->orders->received.
                        target = eval(f'{algo.get("algo_class")}('
                                      f'name=algo_name, '
                                      f'daemon=True, '
                                      f'keep_running=self._keep_running, '
                                      f'algo_cfg=dct_algo_prv)'
                                      )
                        self._lst_thread_pool.append({"name": algo_name, "level": 5.1, "pointer": target})

                        target.start()
                        dct_algo_prv['running'] = True
                        lst_algos_prv.append(dct_algo_prv)
                        self._logger.info(f"Initializing the algo name: {algo_name}...")

                    # Stops the running algoritm.
                    elif algo.get("running", False) and not algo.get("enabled", False):
                        thr = list(filter(lambda x: x.get("name") == algo_name, self._lst_thread_pool))[0]
                        if len(thr) > 0:
                            thr.get("pointer", None).join()
                            dct_algo_prv['running'] = False
                            self._logger.info(f"The algo name: {thr.get('name')} was finalized.")

                time.sleep(self.__sleep_when_done)

            else:
                lst_thr = list(filter(lambda x: x.get("level") == 5.1, self._lst_thread_pool))
                for thr in lst_thr:
                    thr.get("pointer", None).join()
                    self._logger.info(f"The algo name: {thr.get('name')} was finalized.")

                prdr_name = "algo_providers"
                lst_algos_prv, lst_algos_sel_prv, dct_algo_prv = self._get_internal_provider_data(prdr_name, -1)
                lst_algos_prv.clear()

        self._logger.info("Executor was finalized.")
