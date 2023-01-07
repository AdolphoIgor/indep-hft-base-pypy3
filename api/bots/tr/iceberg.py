from api.bots.tr.tr_bot import TRBot
from api.bots.tr.bot_momentum import BotMomentum
from api.jobs.internal_config_provider import InternalConfigProviders


class Iceberg(BotMomentum):

    def __init__(self, name, daemon, algo: dict, config_prov: InternalConfigProviders):
        super().__init__(name, daemon, algo, TRBot.ONE_ARM, config_prov)

    def _execute(self):
        pass
