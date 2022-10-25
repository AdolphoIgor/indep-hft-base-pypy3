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

        def send_buy_order(self, conta: str, broker: str, senha: str, ativo: str, bolsa: str, preco: float, qtd: int):
        def send_sell_order(self, conta: str, broker: str, senha: str, ativo: str, bolsa: str, preco: float, qtd: int):

        """
        # entry point
        if self._get_spread() != 0 and self._is_asset_state(["opened"]) and \
                self._lst_sbl_conf[0][-1] and self._lst_sbl_conf[1][-1]:

            # Sell the first asset and buy the second asset, both at market order.
            if self._get_spread() > 0:
                self._lst_orders_sent.append(self._profitdll.send_buy_order())
                self._lst_orders_sent.append(self._profitdll.send_sell_order())

            # Sell the second asset and buy the first asset, both at market order.
            if self._get_spread() < 0:
                self._lst_orders_sent.append(self._profitdll.send_buy_order())
                self._lst_orders_sent.append(self._profitdll.send_sell_order())

        # exit point
        lst_orders = self._get_lst_ord_cfg()
        if len(lst_orders) > 0 and self._is_asset_state(["opened", "preclosing"]):

            for ordr in lst_orders:
                if self._get_spread() != 0:
                    break

                # TODO: ZERAR TODOS
                self._lst_orders_sent.append(self._profitdll.send_buy_order())
                self._lst_orders_sent.append(self._profitdll.send_sell_order())
                # self._lst_orders_sent.append(self._profitdll.send_stop_buy_order())
                # self._lst_orders_sent.append(self._profitdll.send_stop_sell_order())
                # self._lst_orders_sent.append(self._profitdll.send_zero_position())
                pass

    def _get_spread(self):
        lst_spread = self._dct_inst.get("spread")
        return lst_spread[1][0] - lst_spread[0][1]

    def _is_asset_state(self, lst_states: list) -> bool:
        for quote in self._dct_inst.get("quote"):
            for state in lst_states:
                if quote.get("state", -1) == self._dct_asset_state.get(state):
                    return True

        return False

    def _get_lst_ord_cfg(self):
        # TODO: Pedir a lista de constantes do status das ordens.
        lst_orders = []
        for order in self._dct_inst.get("orders"):
            if order.get("cl_ord_id") in self._lst_orders_sent and order.get("status") != "exec":
                lst_orders.append(order)

                for thr in self._lst_sbl_conf:
                    if thr.get("symbol") == order.get("symbol"):
                        thr[-2] += order.get("traded_qtd")
                        thr[-1] = thr[2] - thr[-2] >= thr[1]

                    break

        return lst_orders
