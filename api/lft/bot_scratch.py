from api.io.network.profit_dll import ProfitDLL


class BotScratch:
    _profitdll: ProfitDLL

    def process(self):
        self._profitdll.get_server_clock()
