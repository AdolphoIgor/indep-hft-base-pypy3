import time
import traceback
from threading import Thread

from api.bots.bot import Bot
from api.jobs.internal_config_provider import InternalConfigProviders
from api.logger import logger


class AuctionBot(Bot):

    def __init__(self, name, daemon, algo: dict, qtd_exp: int, config_prov: InternalConfigProviders):
        super().__init__(name, daemon, algo, qtd_exp, config_prov)

        # When running bots which requires a scan of an entire stockmarket that method should take care of it.
        self.__run_entire_market()

        self._lst_sbl_mkt = [(alg.get("symbol"), alg.get("stock_market")) for alg in self._algo.get("threads")]
        self._lst_sbl = [sbl[0] for sbl in self._lst_sbl_mkt]

    def __run_entire_market(self):
        lst_threads = [thr for thr in self._algo.get("threads") if not thr.get("symbol")]
        if not lst_threads:
            return

        for thr in lst_threads:
            self._profit_dll.get_all_ticker(thr.get("stock_market"))

        dct_prog = self._config_prov.get_internal_provider_data(
            "progress", sublist=self._config_prov.get_internal_provider_data("instruments"))

        while dct_prog:
            stop = all([prog.get("progress") == 100 for _, prog in dct_prog.items()])
            if stop:
                break

        # Filters
        lst_quotes = [
            (k, v.get("security_type"), v.get("lote"))
            for k, v in self._config_prov.get_internal_provider_data(
                "quote", sublist=self._config_prov.get_internal_provider_data("instruments")).items()
            if ((v.get("security_type") == 14 and v.get("security_sub_type") == 25 and v.get("lote") == 100) or
                (v.get("security_type") == 15 and v.get("security_sub_type") == 26 and v.get("lote") == 100) or
                (v.get("security_type") == 0 and v.get("security_sub_type") in [2, 4, 13]))
        ]

        # Configures
        lst_return = []
        for quote in lst_quotes:
            thr_sel = None
            stock_market = "F" if quote[1] == 0 else "B"
            for thr in lst_threads:
                if thr.get("stock_market") == stock_market:
                    thr_sel = thr
                    break

            if not thr_sel:
                continue

            dct_thr_cpy = eval(str(thr_sel))
            dct_thr_cpy["symbol"] = quote[0]
            dct_thr_cpy["stock_market"] = stock_market
            dct_thr_cpy.get("start_param")["order_op_qty"] *= quote[2]
            lst_return.append(dct_thr_cpy)

        lst_threads = [thr for thr in self._algo.get("threads") if thr.get("symbol")]
        self._algo.get("threads").clear()
        self._algo.get("threads").extend(lst_threads)
        self._algo.get("threads").extend(lst_return)

    def _load_symbol(self, symbol, dct_inst: dict):
        # The subscription step consists in put the symbols found in the file (and present in self._dct_inst) into the
        # self.self._lst_subs list and into the self._algo.get("threads") as has been done in __run_entire_market()

        dct_sbl = None
        for thr in self._algo.get("threads"):
            if thr.get("symbol") == symbol:
                dct_sbl = thr
                break

        if dct_sbl:
            return

        quote = dct_inst.get('quote')
        stock_market = "F" if quote[1] == 0 else "B"
        thr = {
          "symbol": symbol,
          "stock_market": stock_market,
          "broker_id": "15002",
          "tick_value": 0.01,
          "lote": 1,
          "start_param": {
            "order_op_qty": 100
          }
        }

        # Get the multiplier in order to simulate an order at market. BM&F increase 30 ticks, Bovespa increase 15%.
        if quote.get("security_type") == 0:
            thr["agr_adj"] = thr.get("tick_value") * self.AGR_BMF

        elif quote.get("security_type") in [14, 15]:
            thr["agr_adj"] = self.AGR_BOV

        self._algo["threads"] = thr

    def __init_instruments(self):
        def init_progressivelly():
            logger.info(f"Waiting for instruments for the algo: {self.name}...")

            qtt_to_proc = len(self._lst_sbl)
            while True:
                qtt_proc = 0
                for sbl in self._lst_sbl:

                    if self._dct_inst and all([sbl in v for _, v in self._dct_inst.items()]):
                        qtt_proc += 1
                        continue

                    lst_res = []
                    dct_res = {}

                    for inst in self._lst_inst:
                        value = inst.get("value").get(sbl, {})

                        if value:
                            dct_res[inst.get("type")] = {sbl: value}
                            lst_res.append(True)

                        elif inst.get("type") == "orders":
                            lst_res.append(True)

                        else:
                            lst_res.append(False)

                    if all(lst_res):
                        for k, v in dct_res.items():
                            dct_inst = self._dct_inst.get(k, {})
                            if not dct_inst:
                                self._dct_inst[k] = dct_inst

                            dct_inst.update(v)
                            self._load_symbol(sbl, v)

                time.sleep(0.0001)

                if qtt_proc == qtt_to_proc:
                    break

            logger.info(f"All de instruments for the algo: {self.name} has been received.")

        init_progr = Thread(target=init_progressivelly, name="init_progressivelly")
        init_progr.start()

    def run(self):
        logger.info(f"Initializing the algo name: {self.name}...")
        # As symbols the instruments are being recovered, the symbol is released to be processed.
        self.__init_instruments()
        self._recover_shutdownd_state()

        while self._config_prov.get_keep_running() and self._algo.get("enabled"):
            try:
                self._calc_session_time()
                self._execute()

            except Exception as e:
                logger.error(traceback.format_exc())

                self._init_orders_instruments()

                if self._profit_dll and not self._profit_dll.is_connected():
                    if not self._config.get("conn_broken_rep"):
                        self._config["conn_broken_rep"] = True

                    time.sleep(0.2)

        self._unsubscribe()
        logger.info(f"The algo name: {self.name} was finalized.")
