from api.bots.bot import Bot

from api.bots.tr.tr_bot import TRBot
from api.jobs.internal_config_provider import InternalConfigProviders


class Recorder(Bot):

    def __init__(self, name, daemon, algo: dict, config_prov: InternalConfigProviders):
        super().__init__(name, daemon, algo, 8, config_prov)

    def _execute(self):
        pass
