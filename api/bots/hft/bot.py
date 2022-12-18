from threading import Thread

from api.bots.hft.exceptions import BotInitializationException
from api.bots.hft.position import PositionMgr
from api.indep import InternalConfigProviders
from api.logger import logger


class Bot(Thread):
    ONE_ARM = 1
    TWO_ARM = 2
    TREE_ARM = 3
    FOUR_ARM = 4

    _dct_inst = {}
    _lst_orders_sent = []

    def __init__(self, name, daemon, algo: dict, qtd_exp: int, config_prov: InternalConfigProviders):
        super().__init__(name=name, daemon=daemon)
        self._algo = algo
        self._qtd_exp = qtd_exp
        self._config_prov = config_prov

        self._profitdll = self._config_prov.get_internal_provider_data("config").get("value").get("prov_conn")
        self._dct_asset_state = self._profitdll.get_asset_state()
        self._dct_ord_status = self._profitdll.get_dct_order_status()

        self._lst_sbl = [(alg.get("symbol"), alg.get("stock_market")) for alg in algo.get("threads")]
        self._position_mgr = PositionMgr(self._dct_inst.get("orders"), self._lst_orders_sent, algo.get("threads"),
                                         self._dct_ord_status)

    def execute(self):
        pass

    def run(self):
        logger.info(f"Initializing the algo name: {self.name}...")
        self.__test_qtd_assets()

        self._profitdll.set_day_trade(self._algo.get("is_day_trade", False))
        self._profitdll.set_enabled_log_to_debug(self._algo.get("debug_mode", False))

        self.__subscribe()

        while self._config_prov.is_running() and self._algo.get("enabled"):
            self.execute()

        self.__unsubscribe()
        logger.info(f"The algo name: {self.name} was finalized.")

    def __test_qtd_assets(self):
        qtd_ast = len(set(self._lst_sbl))

        if qtd_ast == 0:
            raise BotInitializationException(f"The algo: {self.name} requires at least 1 asset but 0 was given.")

        if qtd_ast != self._qtd_exp:
            str_cpl = f"{qtd_ast} was given" if qtd_ast == 1 else f"{qtd_ast} were given"
            raise BotInitializationException(f"The algo: {self.name} requires {self._qtd_exp} asset(s) but {str_cpl}.")

    def __subscribe(self):
        # Restricts to only the assets managed by the current instance.
        lst_subs = self._config_prov.get_internal_provider_data("subscriptions")
        lst_inst = self._config_prov.get_internal_provider_data("instruments")
        for sbl in self._lst_sbl:
            for inst in lst_inst:
                # Gets a copy of every instrument's memory pointer to the dict.
                self._dct_inst.get(inst.get("type"), []).append(
                    self._config_prov.get_internal_provider_data(inst.get("type"), sublist=lst_inst).
                    get("value").get(sbl[0]))

                lst_inst_subscrbd = self._config_prov.get_internal_provider_data(
                    inst.get("type"), sublist=lst_subs).get("value")

                for req_inst in self._algo.get("req_instruments"):
                    if sbl[0] not in lst_inst_subscrbd:
                        if req_inst == "quote":
                            self._profitdll.subscribe_ticker(ticker=sbl[0], bolsa=sbl[1])
                            self._profitdll.get_last_daily_close(ticker=sbl[0], bolsa=sbl[1])

                        elif req_inst == "lp":
                            self._profitdll.subscribe_price_book(ticker=sbl[0], bolsa=sbl[1])

                        elif req_inst == "lo":
                            self._profitdll.subscribe_offer_book(ticker=sbl[0], bolsa=sbl[1])

                lst_inst_subscrbd.append(sbl[0])

    def __unsubscribe(self):
        lst_subs = self._config_prov.get_internal_provider_data("subscriptions")
        for sbs in lst_subs:
            for sbl in self._lst_sbl:
                for inst in sbs.get("value"):
                    if inst.count(sbl) == 1:
                        if inst == "quote":
                            self._profitdll.unsubscribe_ticker(ticker=sbl[0], bolsa=sbl[1])

                        elif inst == "lp":
                            self._profitdll.unsubscribe_price_book(ticker=sbl[0], bolsa=sbl[1])

                        elif inst == "lo":
                            self._profitdll.unsubscribe_offer_book(ticker=sbl[0], bolsa=sbl[1])

                    inst.remove(sbl)

    def _is_asset_state(self, lst_states: list) -> bool:
        """
            At this point, for every asset configurated for the bot its quotes will be availiable here at
            self._dct_inst.get("quote") dict.

        See :param lst_states: For valid states, please, see ProfitDLL().get_asset_state()
        :return:
        """
        ret_bol = True
        for quote in self._dct_inst.get("quote"):
            if self._dct_asset_state.get(quote.get("state", -1)) not in lst_states:
                ret_bol = False
                break

        return ret_bol
