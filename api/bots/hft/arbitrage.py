from api.bots.hft.bot import Bot
from api.indep import InternalConfigProviders


class Arbitrage(Bot):

    def __init__(self, name, daemon, algo: dict, config_prov: InternalConfigProviders):
        super().__init__(name, daemon, algo, 2, config_prov)

    def execute(self):
        pass
