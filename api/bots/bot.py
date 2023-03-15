import time
from datetime import datetime
from threading import Thread

from api.bots.tr.exceptions import BotInitializationException
from api.jobs.internal_config_provider import InternalConfigProviders
from api.logger import logger


class Bot(Thread):
    # CONSTANTS
    ARM_ONE = 1
    ARM_TWO = 2

    AGR_BMF = 60
    AGR_BOV = 1.30

    _dct_inst = {}

    def __init__(self, name, daemon, algo: dict, qtd_exp: int, config_prov: InternalConfigProviders):
        super().__init__(name=name, daemon=daemon)

        self._algo = algo
        self._qtd_exp = qtd_exp
        self._config_prov = config_prov

        self._config = self._config_prov.get_internal_provider_data("config")
        self._profit_dll = self._config.get("prov_conn")
        self._profit_dll.set_day_trade(self._algo.get("is_day_trade", True))
        self._profit_dll.set_enabled_log_to_debug(self._algo.get("debug_mode", True))

        self._dct_asset_state = self._profit_dll.get_asset_state()
        self._dct_ord_status = self._profit_dll.get_dct_order_status()

        # When running bots which requires a scan of an entire stockmarket that method should take care of it.
        self.__run_entire_market()

        self._lst_sbl_mkt = [(alg.get("symbol"), alg.get("stock_market")) for alg in self._algo.get("threads")]
        self._lst_sbl = [sbl[0] for sbl in self._lst_sbl_mkt]

        self._lst_thrshld_clsg = self._algo.get("stop_param").get("threshold")["closing_config"]
        self._thrshld_time_limit = datetime.strptime(self._lst_thrshld_clsg[0].get("time"), "%H:%M:%S")
        self._thrshld_value_limit = self._lst_thrshld_clsg[0].get("value")

        self._b_in_session = False
        self._pos_opened = False
        self._pos_stopped = False

        # "lp", "tt" are some instruments already avaliable after a derivative ticker subscribing.
        lst_req = self._algo.get("req_instruments", [])
        if "spread_rt" in lst_req:
            lst_req.append("lp")

        if "lp_tr" in lst_req:
            lst_req.append("lo")

        if "ranking" in lst_req:
            lst_req.append("tt")

        if "quote_adtl" in lst_req:
            lst_req.append("quote")

        # we will always have to need orders, and quotes for every bot created.
        lst_req.extend(["orders", "quote"])
        self._algo["req_instruments"] = list(set(lst_req))

        # Restricts to only the assets managed by the current instance.
        self._lst_inst = [inst for inst in self._config_prov.get_internal_provider_data("instruments")
                          if inst.get("type") in self._algo.get("req_instruments")]

        self._lst_subs = [sub for sub in self._config_prov.get_internal_provider_data("subscriptions")
                          if sub.get("type") in self._algo.get("req_instruments")]

        self.__missing_lst_ordrs = True

    def _execute(self):
        """
            This is where the trading algorithm runs.
        """
        pass

    def _initilize(self):
        """
            Just use it in the subclass to implement required-once initialization for the bots.
        """
        pass

    def __run_entire_market(self):
        lst_threads = [thr for thr in self._algo.get("threads") if not thr.get("symbol")]
        if not lst_threads:
            return

        for thr in lst_threads:
            self._profit_dll.get_all_ticker(thr.get("stock_market"))

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

    def __initialize_super(self):
        # Get the multiplier in order to simulate an order at market. BM&F increase 30 ticks, Bovespa increase 15%.
        for thr in self._algo.get("threads"):
            if not thr.get("symbol") == "":
                dct_quote = self._dct_inst.get("quote", {}).get(thr.get("symbol"))

                thr["lote"] = thr.get("lote")
                if dct_quote.get("security_type") == 0:
                    thr["agr_adj"] = thr.get("tick_value") * self.AGR_BMF

                elif dct_quote.get("security_type") in [14, 15]:
                    thr["agr_adj"] = self.AGR_BOV

    def __recover_shutdownd_state(self):
        # when the system were interrupted after opened orders, they must be cleaned.
        for sbl, lst_ordr in self._dct_inst.get("orders", {}).items():

            lst_ordrs = [ordr for ordr in lst_ordr if ordr.get("status") == "Filled"]

            dct_ordr = {"qtd": 0, "last": None}
            for ordr in lst_ordrs:
                if ordr.get("side") == 1:
                    dct_ordr["qtd"] += ordr.get("traded_qtd")
                else:
                    dct_ordr["qtd"] -= ordr.get("traded_qtd")

                dct_ordr["last"] = ordr

            lst_ordr.clear()
            if dct_ordr.get("qtd"):
                lst_ordr.append(dct_ordr.get("last"))

        lst_res = [True for sbl, lst in self._dct_inst.get("orders", {}).items() if lst]
        self._pos_opened = len(lst_res) == self._qtd_exp and all(lst_res)

    def _calc_session_time(self):
        self._b_in_session = datetime.now().time() <= self._thrshld_time_limit.time()
        if self._b_in_session:
            return

        if self._lst_thrshld_clsg[-1].get("value") == self._thrshld_value_limit:
            return

        self._thrshld_value_limit = self._lst_thrshld_clsg[-1].get("value")
        for trhs in self._lst_thrshld_clsg[1:]:
            if datetime.now().time() <= datetime.strptime(trhs.get("time"), "%H:%M:%S").time():
                self._thrshld_value_limit = trhs.get("value")
                break

    def run(self):
        logger.info(f"Initializing the algo name: {self.name}...")
        self.__subscribe()
        self.__init_instruments()
        self.__initialize_super()
        self.__recover_shutdownd_state()
        self._initilize()

        while self._config_prov.get_keep_running() and self._algo.get("enabled"):
            try:
                self._calc_session_time()
                self._execute()

            except Exception:
                self._init_orders_instruments()

                if self._profit_dll and not self._profit_dll.is_connected():
                    if not self._config.get("conn_broken_rep"):
                        self._config["conn_broken_rep"] = True

                    time.sleep(0.2)

        self.__unsubscribe()
        logger.info(f"The algo name: {self.name} was finalized.")

    def _test_qtd_assets(self):
        qtd_ast = len(set(self._lst_sbl))

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
            for inst in self._lst_inst:
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

    def _init_orders_instruments(self):
        """
            It were made protected, so it can be called whenever you want besides being called at the end
            of self._execute() method.
        """
        if self.__missing_lst_ordrs:
            for inst in self._lst_inst:
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

        for sbs in self._lst_subs:
            for sbl in self._lst_sbl_mkt:
                inst = sbs.get("value")
                if inst.count(sbl[0]) == 0:
                    if sbs.get("type") == "quote":
                        self._profit_dll.subscribe_ticker(ticker=sbl[0], bolsa=sbl[1])
                        self._profit_dll.get_last_daily_close(ticker=sbl[0], bolsa=sbl[1])

                    elif sbs.get("type") == "quote_adtl":
                        self._profit_dll.request_ticker_info(ticker=sbl[0], bolsa=sbl[1])

                    elif sbs.get("type") == "lp":
                        self._profit_dll.subscribe_price_book(ticker=sbl[0], bolsa=sbl[1])

                    elif sbs.get("type") == "lo":
                        self._profit_dll.subscribe_offer_book(ticker=sbl[0], bolsa=sbl[1])

                    inst.append(sbl[0])

        time.sleep(1)
        logger.info(f"Instruments subscription for the algo: {self.name} done.")

    def __unsubscribe(self):
        logger.info(f"Unsubscribing instruments for the algo: {self.name}...")

        for sbs in self._lst_subs:
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

    def _get_position(self):
        cons_pos, act_pos, comb_pos = 0, 0, 0
        for thr in self._algo.get("threads"):
            dct_pos = self._profit_dll.get_position(thr.get("broker").get("account"), thr.get("broker").get("id"),
                                                    thr.get("symbol"), thr.get("stock_market"))

            if not dct_pos:
                return [0, 0, 0, False, False, False]

            qtt = [dct_pos.get("sell_qtd"), dct_pos.get("buy_qtd")]
            cons_pos += round((dct_pos.get("avg_sell_price") - dct_pos.get("avg_buy_price")) *
                              (min(qtt) / thr.get("lote")) * thr.get("tick_value_fin"), 2)

            if qtt[0] > qtt[1]:
                act_pos += round(dct_pos.get("avg_sell_price") - dct_pos.get("price") *
                                 (dct_pos.get("intraday_pos") / thr.get("lote")) * thr.get("tick_value_fin"), 2)

            elif qtt[0] < qtt[1]:
                act_pos += round(dct_pos.get("price") - dct_pos.get("avg_buy_price") *
                                 (dct_pos.get("intraday_pos") / thr.get("lote")) * thr.get("tick_value_fin"), 2)

        comb_pos = cons_pos + act_pos

        stp_lmt = self._algo.get("stop_param").get("stop_limit")
        return cons_pos, act_pos, comb_pos, cons_pos < stp_lmt, act_pos < stp_lmt, comb_pos < stp_lmt
