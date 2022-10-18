from api.bots.hft.bot import Bot
from api.indep import InternalConfigProviders


class Auction(Bot):

    def __init__(self, name, daemon, algo: dict, config_prov: InternalConfigProviders):
        super().__init__(name, daemon, algo, config_prov)
