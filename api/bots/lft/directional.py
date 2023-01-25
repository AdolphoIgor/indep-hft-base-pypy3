from datetime import datetime, timedelta

from api.bots.bot import Bot
from api.jobs.internal_config_provider import InternalConfigProviders


class Directional(Bot):

    def __init__(self, name, daemon, algo: dict, config_prov: InternalConfigProviders):
        super().__init__(name, daemon, algo, Bot.ARM_ONE, config_prov)

        self._start_time_limit = datetime.now() + timedelta(minutes=self._thrshld_opening_delay)

    def _initilize(self):
        self._test_qtd_assets()

    def _execute(self):

        dct_quote = self._dct_inst.get("quote").get(self._lst_sbl[0], None)
        dct_ranking = self._dct_inst.get("ranking").get(self._lst_sbl[0], None)

        if datetime.now().time() < self._start_time_limit.time():
            return

