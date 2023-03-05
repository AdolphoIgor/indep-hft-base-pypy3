from datetime import datetime, timedelta

from api.bots.bot import Bot
from api.jobs.internal_config_provider import InternalConfigProviders


class Directional(Bot):

    def __init__(self, name, daemon, algo: dict, config_prov: InternalConfigProviders):
        super().__init__(name, daemon, algo, Bot.ARM_ONE, config_prov)

        opening_delay = self._algo.get("start_param").get("threshold")["opening_delay"]
        self._start_time_limit = datetime.now() + timedelta(minutes=opening_delay)

    def _initilize(self):
        self._test_qtd_assets()

    def _execute(self):
        """
            {"date": date, "open_val": open_val, "high": high, "low": low, "close": close, "vol": vol,
              "ajuste": ajuste, "max_limit": max_limit, "min_limit": min_limit, "vol_buyer": vol_buyer,
              "vol_seller": vol_seller, "qtd": qtd, "negocios": negocios, "contratos_open": contratos_open,
              "qtd_buyer": qtd_buyer, "qtd_seller": qtd_seller, "neg_buyer": neg_buyer,
              "neg_seller": neg_seller
              }
        """

        dct_quote = self._dct_inst.get("quote").get(self._lst_sbl[0], None)
        dct_ranking = self._dct_inst.get("ranking").get(self._lst_sbl[0], None)

        if datetime.now().time() < self._start_time_limit.time():
            return
