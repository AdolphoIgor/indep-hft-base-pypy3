from threading import Thread

from api.bots.hft.exceptions import BotInitializationException
from api.indep import InternalConfigProviders
from api.logger import logger


class Bot(Thread):
    _lst_quote = []
    _lst_tt = []
    _lst_lp = []
    _lst_lo = []
    _lst_account = []
    _lst_orders = []
    _lst_progress = []
    _lst_spread = []

    def __init__(self, name, daemon, algo: dict, qtd_exp: int, config_prov: InternalConfigProviders):
        super().__init__(name=name, daemon=daemon)
        self._algo = algo
        self._qtd_exp = qtd_exp
        self._config_prov = config_prov
        self._profitdll = self._config_prov.get_internal_provider_data("config").get("value").get("prov_conn")

        lst_inst = self._config_prov.get_internal_provider_data("instruments")
        self._lst_sbl = [algo.get("symbol") for algo in self._algo.get("threads")]
        for sbl in self._lst_sbl:
            self._lst_quote.append(
                self._config_prov.get_internal_provider_data("quote", sublist=lst_inst).get("value").get(sbl))
            self._lst_tt.append(
                self._config_prov.get_internal_provider_data("tt", sublist=lst_inst).get("value").get(sbl))
            self._lst_lp.append(
                self._config_prov.get_internal_provider_data("lp", sublist=lst_inst).get("value").get(sbl))
            self._lst_lo.append(
                self._config_prov.get_internal_provider_data("lo", sublist=lst_inst).get("value").get(sbl))
            self._lst_account.append(
                self._config_prov.get_internal_provider_data("account", sublist=lst_inst).get("value").get(sbl))
            self._lst_orders.append(
                self._config_prov.get_internal_provider_data("orders", sublist=lst_inst).get("value").get(sbl))
            self._lst_progress.append(
                self._config_prov.get_internal_provider_data("progress", sublist=lst_inst).get("value").get(sbl))
            self._lst_spread.append(
                self._config_prov.get_internal_provider_data("spread", sublist=lst_inst).get("value").get(sbl))

    def execute(self):
        pass

    def run(self):
        logger.info(f"Initializing the algo name: {self.name}...")
        self.__test_qtd_assets()
        self.execute()
        logger.info(f"The algo name: {self.name} was finalized.")

    def __test_qtd_assets(self):
        qtd_ast = len(set(self._lst_sbl))

        if qtd_ast == 0:
            raise BotInitializationException(f"The algo: {self.name} requires at least 1 asset but 0 was given.")

        if qtd_ast != self._qtd_exp:
            str_cpl = f"{qtd_ast} was given" if qtd_ast == 1 else f"{qtd_ast} were given"
            raise BotInitializationException(f"The algo: {self.name} requires {self._qtd_exp} asset(s) but {str_cpl}.")
