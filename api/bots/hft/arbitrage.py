from api.bots.hft.bot import Bot
from api.indep import InternalConfigProviders


class Arbitrage(Bot):

    def __init__(self, name, daemon, algo: dict, config_prov: InternalConfigProviders):
        super().__init__(name, daemon, algo, Bot.TWO_ARM, config_prov)

    def execute(self):
        """
            For asset state check out the ProfitDLL's member _dct_asset_state.
        """

        # entry point
        if self._get_spread() != 0 and self._is_asset_state(["opened"]) and \
                self._algo.get("threads")[0].get("has_ord_rem") and self._algo.get("threads")[1].get("has_ord_rem"):

            lst_sides = None
            lst_prices = None

            # Sell the first asset and buy the second asset, both at market order.
            if self._get_spread() > 0:
                lst_sides = [self._algo.get("threads")[0], self._algo.get("threads")[1]]
                lst_prices = [self._dct_inst.get("spread")[0][0], self._dct_inst.get("spread")[1][1]]

            # Sell the second asset and buy the first asset, both at market order.
            if self._get_spread() < 0:
                lst_sides = [self._algo.get("threads")[1], self._algo.get("threads")[0]]

            self._lst_orders_sent.append(self._profitdll.send_buy_order(
                conta=lst_sides[0].get("broker").get("account"), broker=lst_sides[0].get("broker").get("id"),
                senha=lst_sides[0].get("broker").get("password"),
                ativo=lst_sides[0].get("symbol"), bolsa=lst_sides[0].get("stock_market"),
                preco=lst_prices[0], qtd=lst_sides[0].get("start_param").get("order_op_qty")
            ))
            self._lst_orders_sent.append(self._profitdll.send_sell_order(
                conta=lst_sides[1].get("broker").get("account"), broker=lst_sides[1].get("broker").get("id"),
                senha=lst_sides[1].get("broker").get("password"),
                ativo=lst_sides[1].get("symbol"), bolsa=lst_sides[1].get("stock_market"),
                preco=lst_prices[1], qtd=lst_sides[1].get("start_param").get("order_op_qty")
            ))

        # exit point
        lst_orders = [ordr for ordr in self._position.get_filtered_orders(["bstNewbstFilled"])
                      if len(ordr.get("lst_closed_pos", [])) == 0]
        if len(lst_orders) > 0 and self._get_spread() != 0:
            for ordr in lst_orders:
                '''
                order = {
                    "corretora": corretora, "qtd": qtd, "traded_qtd": traded_qtd, "leaves_qtd": leaves_qtd,
                    "side": side, "price": price, "stop_price": stop_price, "avg_price": avg_price, 
                    "profit_id": profit_id, "tipo_ordem": tipo_ordem, "conta": conta, "titular": titular, 
                    "cl_ord_id": cl_ord_id, "status": status, "date": date, "symbol": asset_id.ticker,
                }
                '''

                thr_sel = None
                for thr in self._algo.get("threads"):
                    if thr.ge("symbol") == ordr.get("symbol"):
                        thr_sel = thr
                        break

                if ordr.get("side") == "S":
                    self._lst_orders_sent.append(self._profitdll.send_buy_order(
                        conta=thr_sel.get("broker").get("account"), broker=thr_sel.get("broker").get("id"),
                        senha=thr_sel.get("broker").get("password"),
                        ativo=thr_sel.get("symbol"), bolsa=thr_sel.get("stock_market"),
                        preco=self._dct_inst.get("spread")[0][1], qtd=thr_sel.get("qtd")

                    ))
                else:
                    self._lst_orders_sent.append(self._profitdll.send_sell_order(
                        conta=thr_sel.get("broker").get("account"), broker=thr_sel.get("broker").get("id"),
                        senha=thr_sel.get("broker").get("password"),
                        ativo=thr_sel.get("symbol"), bolsa=thr_sel.get("stock_market"),
                        preco=self._dct_inst.get("spread")[1][0], qtd=thr_sel.get("qtd")
                    ))

    def _get_spread(self):
        lst_spread = self._dct_inst.get("spread")
        return lst_spread[1][0] - lst_spread[0][1]
