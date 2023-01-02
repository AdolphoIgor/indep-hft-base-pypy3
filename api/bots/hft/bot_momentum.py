from api.bots.hft.Momentum import Momentum
from api.bots.hft.bot import Bot
from api.jobs.internal_config_provider import InternalConfigProviders


class BotMomentum(Bot):

    def __init__(self, name, daemon, algo: dict, qtd_exp: int, config_prov: InternalConfigProviders):
        super().__init__(name, daemon, algo, qtd_exp, config_prov)
        self._momentum = Momentum()

