import time
from datetime import datetime
from threading import Thread

from api.bots.tr.exceptions import BotInitializationException
from api.jobs.internal_config_provider import InternalConfigProviders
from api.logger import logger


class Bot(Thread):
    ONE_ARM = 1
    TWO_ARM = 2

    _dct_inst = {}

    def __init__(self, name, daemon, algo: dict, qtd_exp: int, config_prov: InternalConfigProviders):
        super().__init__(name=name, daemon=daemon)

        self._algo = algo
        self._qtd_exp = qtd_exp
        self._config_prov = config_prov

        self._config = self._config_prov.get_internal_provider_data("config")
        self._profit_dll = self._config.get("prov_conn")
        self._profit_dll.set_day_trade(self._algo.get("is_day_trade", False))
        self._profit_dll.set_enabled_log_to_debug(self._algo.get("debug_mode", False))
        self._dct_asset_state = self._profit_dll.get_asset_state()
        self._dct_ord_status = self._profit_dll.get_dct_order_status()

        self._lst_sbl_mkt = [(alg.get("symbol"), alg.get("stock_market")) for alg in algo.get("threads")]
        self._lst_sbl = [sbl[0] for sbl in self._lst_sbl_mkt]

        if self._algo["agr_adj_type"] == "tick":
            self._agr_adj = self._algo["tick_value"] * self._algo["agr_adj_value"]
        elif self._algo["agr_adj_type"] == "perc":
            self._agr_adj = round(self._algo["agr_adj_value"] / 100, 2)

        self._time_limit = datetime.strptime(self._algo.get("time_limit"), "%H:%M:%S")

        # "orders", "tt" are some instruments already avaliable after the ticker subscribing (so their derivatives).
        lst_req = self._algo.get("req_instruments", [])
        if "spread_rt" in lst_req:
            lst_req.append("lp")

        if "ranking" in lst_req:
            lst_req.append("tt")

        # we will always have to need orders, and quotes for every bot created.
        lst_req.extend(["orders", "quote"])
        self._algo["req_instruments"] = list(set(lst_req))

        # Restricts to only the assets managed by the current instance.
        self.__lst_inst = [inst for inst in self._config_prov.get_internal_provider_data("instruments")
                           if inst.get("type") in self._algo.get("req_instruments")]

        self.__lst_subs = [sub for sub in self._config_prov.get_internal_provider_data("subscriptions")
                           if sub.get("type") in self._algo.get("req_instruments")]

        self.__missing_lst_ordrs = True

    def _execute(self):
        pass

    def _initilize(self):
        """
            Just use it inhe subclass to implement required-once initialization for the bots.
        :return:
        """
        pass

    def run(self):
        logger.info(f"Initializing the algo name: {self.name}...")
        self.__test_qtd_assets()
        self.__subscribe()
        self.__init_instruments()
        self._initilize()

        while self._config_prov.get_keep_running() and self._algo.get("enabled"):
            try:
                self._execute()

            except Exception:
                self.__init_orders_instruments()

                if self._profit_dll and not self._profit_dll.is_connected():
                    if not self._config.get("conn_broken_rep"):
                        self._config["conn_broken_rep"] = True

                    time.sleep(0.2)

        self.__unsubscribe()
        logger.info(f"The algo name: {self.name} was finalized.")

    def _print_positions(self):
        dct_ret = {}
        for sbl in self._algo.get("threads"):
            dct_brkr = sbl.get("broker")
            _, ret = self._profit_dll.get_position(conta=dct_brkr.get("account"), broker=dct_brkr.get("id"),
                                                   ativo=sbl.get("symbol"), bolsa=sbl.get("stock_market"))
            dct_ret.update(ret)

        if dct_ret:
            logger.info(f"Algo {self.name} Actual position: {dct_ret}")

    def __test_qtd_assets(self):
        qtd_ast = len(set(self._lst_sbl_mkt))

        if qtd_ast == 0:
            raise BotInitializationException(f"The algo: {self.name} requires at least 1 asset but 0 was given.")

        if qtd_ast != self._qtd_exp:
            str_cpl = f"{qtd_ast} was given" if qtd_ast == 1 else f"{qtd_ast} were given"
            raise BotInitializationException(f"The algo: {self.name} requires {self._qtd_exp} asset(s) but {str_cpl}.")

    def __init_instruments(self):
        logger.info(f"Waiting for instruments for the algo: {self.name}...")

        while True:
            dct_res = {}
            lst_found = []
            for inst in self.__lst_inst:
                # if inst.get("type") == "orders":
                #    continue

                dct_val = {}
                for sbl in self._lst_sbl:
                    b_found = False
                    value = inst.get("value").get(sbl)
                    if value:
                        dct_val[sbl] = value
                        b_found = True

                    if not inst.get("type") == "orders":
                        lst_found.append(b_found)

                dct_res[inst.get("type")] = dct_val

            if all(lst_found):
                self._dct_inst.update(dct_res)
                break

        logger.info(f"All de instruments for the algo: {self.name} has been received.")

    def _get_missing_lst_ordrs(self):
        return self.__missing_lst_ordrs

    def __init_orders_instruments(self):
        """
            It were made protected, so it can be called whenever you want besides being called at the end
            of self._execute() method.
        """
        if self.__missing_lst_ordrs:
            for inst in self.__lst_inst:
                if inst.get("type") == "orders":
                    dct_order = {}
                    for sbl in self._lst_sbl:
                        if not self._dct_inst.get("orders", {}).get(sbl):
                            lst_ordrs = inst.get("value").get(sbl, [])
                            if lst_ordrs:
                                dct_order[sbl] = lst_ordrs

                    self._dct_inst.update({inst.get("type"): dct_order})
                    break

            if len(self._dct_inst.get("orders", {})) == len(self._lst_sbl):
                self.__missing_lst_ordrs = False
                logger.info(f"All of the  symbol's list of orders for the algo: {self.name} were recovered.")

    def __subscribe(self):
        logger.info(f"Subscribing instruments for the algo: {self.name}...")

        for sbs in self.__lst_subs:
            for sbl in self._lst_sbl_mkt:
                inst = sbs.get("value")
                if inst.count(sbl[0]) == 0:
                    if sbs.get("type") == "quote":
                        self._profit_dll.subscribe_ticker(ticker=sbl[0], bolsa=sbl[1])
                        self._profit_dll.get_last_daily_close(ticker=sbl[0], bolsa=sbl[1])

                    elif sbs.get("type") == "lp":
                        self._profit_dll.subscribe_price_book(ticker=sbl[0], bolsa=sbl[1])

                    elif sbs.get("type") == "lo":
                        self._profit_dll.subscribe_offer_book(ticker=sbl[0], bolsa=sbl[1])

                    inst.append(sbl[0])

        time.sleep(1)
        logger.info(f"Instruments subscription for the algo: {self.name} done.")

    def __unsubscribe(self):
        logger.info(f"Unsubscribing instruments for the algo: {self.name}...")

        for sbs in self.__lst_subs:
            for sbl in self._lst_sbl_mkt:
                inst = sbs.get("value")
                if sbs.get("type") == "quote":
                    self._profit_dll.unsubscribe_ticker(ticker=sbl[0], bolsa=sbl[1])

                elif sbs.get("type") == "lp":
                    self._profit_dll.unsubscribe_price_book(ticker=sbl[0], bolsa=sbl[1])

                elif sbs.get("type") == "lo":
                    self._profit_dll.unsubscribe_offer_book(ticker=sbl[0], bolsa=sbl[1])

                inst.remove(sbl[0])
                self._dct_inst.get(sbs.get("type"), {}).pop(sbl[0])

        logger.info(f"Instruments unsubscription for the algo: {self.name} done.")

    def _is_asset_state(self, lst_states: list) -> bool:
        """
            At this point, for every asset configurated for the bot its quotes will be availiable here at
            self._dct_inst.get("quote") dict.

        See :param lst_states: For valid states, please, see ProfitDLL().get_asset_state()
        :return:
        """
        ret_bol = True
        for _, quote in self._dct_inst.get("quote", {}).items():
            if self._dct_asset_state.get(quote.get("state", -1)) not in lst_states:
                ret_bol = False
                break

        return ret_bol

    @staticmethod
    def _get_order_w_status(lst_orders: list, status: str):
        dct_ordr = None
        for ordr in lst_orders[::-1]:
            if ordr.get("status") == status:
                dct_ordr = ordr
                break

        return dct_ordr
