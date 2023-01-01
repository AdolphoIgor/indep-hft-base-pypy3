from api.bots.hft.Momentum import Momentum
from api.bots.hft.bot import Bot
from api.jobs.internal_config_provider import InternalConfigProviders


class Iceberg(Bot):

    def __init__(self, name, daemon, algo: dict, config_prov: InternalConfigProviders):
        super().__init__(name, daemon, algo, Bot.ONE_ARM, config_prov)
        self._momentum = Momentum()

    def execute(self):
        pass
