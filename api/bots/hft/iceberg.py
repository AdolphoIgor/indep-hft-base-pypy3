from api.bots.hft.bot import Bot
from api.bots.hft.bot_momentum import BotMomentum
from api.jobs.internal_config_provider import InternalConfigProviders


class Iceberg(BotMomentum):

    def __init__(self, name, daemon, algo: dict, config_prov: InternalConfigProviders):
        super().__init__(name, daemon, algo, Bot.ONE_ARM, config_prov)

    def execute(self):
        pass
