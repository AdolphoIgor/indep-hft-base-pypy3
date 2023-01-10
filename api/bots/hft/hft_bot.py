import time
from threading import Thread

from api.bots.tr.exceptions import BotInitializationException
from api.jobs.internal_config_provider import InternalConfigProviders
from api.logger import logger


class HFTBot(Thread):
    ONE_ARM = 1
    TWO_ARM = 2

    # Adjust to make an order start to act as a Market one.
    AGR_DOL_ADJ = 8
    AGR_IND_ADJ = 16

    _dct_inst = {}

    def __init__(self, name, daemon, algo: dict, qtd_exp: int, config_prov: InternalConfigProviders):
        super().__init__(name=name, daemon=daemon)
        self._algo = algo
        self._qtd_exp = qtd_exp
        self._config_prov = config_prov

        self._config = self._config_prov.get_internal_provider_data("config")
        self._profit_dll = self._config.get("prov_conn")
        self._dct_asset_state = self._profit_dll.get_asset_state()
        self._dct_ord_status = self._profit_dll.get_dct_order_status()

        self._lst_sbl = [(alg.get("symbol"), alg.get("stock_market")) for alg in algo.get("threads")]

        # we will always have to be quotes for every bot created.
        lst_req = self._algo.get("req_instruments", [])
        lst_req.extend(["quote", "orders"])
        self._algo["req_instruments"] = list(set(lst_req))

    def _execute(self):
        pass

    def run(self):
        logger.info(f"Initializing the algo name: {self.name}...")
        self.__test_qtd_assets()

        self._profit_dll.set_day_trade(self._algo.get("is_day_trade", False))
        self._profit_dll.set_enabled_log_to_debug(self._algo.get("debug_mode", False))

        self.__subscribe()
        self._get_instruments()

        while self._config_prov.get_keep_running() and self._algo.get("enabled"):
            try:
                self._execute()

            except Exception:
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
        qtd_ast = len(set(self._lst_sbl))

        if qtd_ast == 0:
            raise BotInitializationException(f"The algo: {self.name} requires at least 1 asset but 0 was given.")

        if qtd_ast != self._qtd_exp:
            str_cpl = f"{qtd_ast} was given" if qtd_ast == 1 else f"{qtd_ast} were given"
            raise BotInitializationException(f"The algo: {self.name} requires {self._qtd_exp} asset(s) but {str_cpl}.")

    def _get_instruments(self):
        logger.info(f"Waiting for instruments for the algo: {self.name}...")

        while True:
            dct_res = {}
            lst_sbl_f = [sbl[0] for sbl in self._lst_sbl]
            lst_subs = [subs for subs in self._config_prov.get_internal_provider_data("instruments")
                        if subs.get("type") in self._algo.get("req_instruments")]
            lst_found = []
            for inst in lst_subs:
                dct_val = {}
                for sbl in lst_sbl_f:
                    value = inst.get("value").get(sbl)
                    if value:
                        dct_val[sbl] = value
                        lst_found.append(True)
                    else:
                        if not inst.get("type") == "orders":
                            lst_found.append(False)

                dct_res[inst.get("type")] = dct_val

            if all(lst_found):
                self._dct_inst.update(dct_res)
                break

        logger.info(f"All de instruments for the algo: {self.name} has been received.")

    def __subscribe(self):
        logger.info(f"Subscribing instruments for the algo: {self.name}...")

        # Restricts to only the assets managed by the current instance.
        lst_subs = [subs for subs in self._config_prov.get_internal_provider_data("subscriptions")
                    if subs.get("type") in self._algo.get("req_instruments")]

        for sbs in lst_subs:
            for sbl in self._lst_sbl:
                inst = sbs.get("value")
                if inst.count(sbl[0]) == 0:
                    if sbs.get("type") == "quote":
                        self._profit_dll.subscribe_ticker(ticker=sbl[0], bolsa=sbl[1])
                        self._profit_dll.get_last_daily_close(ticker=sbl[0], bolsa=sbl[1])
                        inst.append(sbl[0])

                    elif sbs.get("type") == "lp":
                        self._profit_dll.subscribe_price_book(ticker=sbl[0], bolsa=sbl[1])
                        inst.append(sbl[0])

                    elif sbs.get("type") == "lo":
                        self._profit_dll.subscribe_offer_book(ticker=sbl[0], bolsa=sbl[1])
                        inst.append(sbl[0])

        logger.info(f"Instruments subscription for the algo: {self.name} done.")

    def __unsubscribe(self):
        logger.info(f"Unsubscribing instruments for the algo: {self.name}...")

        lst_subs = [subs for subs in self._config_prov.get_internal_provider_data("subscriptions")
                    if subs.get("type") in self._algo.get("req_instruments")]

        for sbs in lst_subs:
            for sbl in self._lst_sbl:
                inst = sbs.get("value")
                if inst.count(sbl[0]) == 1:
                    if sbs.get("type") == "quote":
                        self._profit_dll.unsubscribe_ticker(ticker=sbl[0], bolsa=sbl[1])
                        inst.remove(sbl[0])

                    elif sbs.get("type") == "lp":
                        self._profit_dll.unsubscribe_price_book(ticker=sbl[0], bolsa=sbl[1])
                        inst.remove(sbl[0])

                    elif sbs.get("type") == "lo":
                        self._profit_dll.unsubscribe_offer_book(ticker=sbl[0], bolsa=sbl[1])
                        inst.remove(sbl[0])

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
