from api.bots.hft.bot import Bot
from api.indep import InternalConfigProviders


class Arbitrage(Bot):

    def __init__(self, name, daemon, algo: dict, config_prov: InternalConfigProviders):
        super().__init__(name, daemon, algo, 2, config_prov)
        self._dct_asset_state = self._profitdll.get_asset_state()

    def execute(self):
        """
            For asset state check out the ProfitDLL's member _dct_asset_state.
            {0: "opened", 2: "frozen", 3: "inhibited", 4: "auctioned", 6: "closed", 10: "preclosing", 13: "preopening"}
        :return:
        """

        # Just suitable for the opened state
        for quote in self._dct_inst.get("quote"):
            if quote.get("state", -1) != self._dct_asset_state.get("opened"):
                return

        lst_spread = self._dct_inst.get("spread")
        spread = lst_spread[1][0] - lst_spread[0][1]

        # Sell the first asset and buy the second asset, both at market order.
        if spread > 0:
            pass

        # Sell the second asset and buy the first asset, both at market order.
        if spread < 0:
            pass
