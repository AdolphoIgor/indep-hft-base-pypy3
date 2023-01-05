from api.bots.tr.bot import Bot
from api.bots.tr.bot_momentum import BotMomentum
from api.jobs.internal_config_provider import InternalConfigProviders


class Ladder(BotMomentum):

    def __init__(self, name, daemon, algo: dict, config_prov: InternalConfigProviders):
        super().__init__(name, daemon, algo, Bot.ONE_ARM, config_prov)

    def _execute(self):
        pass
