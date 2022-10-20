from api.bots.hft.bot import Bot
from api.indep import InternalConfigProviders


class Arbitrage(Bot):

    def __init__(self, name, daemon, algo: dict, config_prov: InternalConfigProviders):
        super().__init__(name, daemon, algo, 2, config_prov)

    def execute(self):

        # For asset state check out the ProfitDLL's member _dct_asset_state.
        # {0: "opened", 2: "frozen", 3: "inhibited", 4: "auctioned", 6: "closed", 10: "preclosing", 13: "preopening"}
        lst_bad_states = [2, 4, 6]
        for quote in self._dct_inst.get("quote"):
            if quote.get("state", -1) in lst_bad_states:
                return
