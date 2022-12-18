from datetime import datetime

from api.bots.hft.bot import Bot
from api.bots.hft.position import PositionMgr
from api.indep import InternalConfigProviders


class Arbitrage(Bot):

    def __init__(self, name, daemon, algo: dict, config_prov: InternalConfigProviders):
        super().__init__(name, daemon, algo, Bot.TWO_ARM, config_prov)

    def execute(self):
        """
            For asset state check out the ProfitDLL's member _dct_asset_state.
        """
        # entry point
        arms = self._position_mgr.get_pos_arms()
        if self._get_spread() != 0 and self._is_asset_state(["opened"]) and \
                arms[0].get("has_ord_rem", False) and arms[1].get("has_ord_rem", False):

            lst_sides = None
            lst_prices = None

            # SELL. Sell the first asset and buy the second asset, both at market order.
            lst_spread = self._dct_inst.get("spread")
            if self._get_spread() > 0:
                lst_sides = [arms[0], arms[1]]
                lst_prices = [lst_spread[0][0][0], lst_spread[0][0][1], lst_spread[1][1][0], lst_spread[1][1][1]]

            # BUY. Sell the second asset and buy the first asset, both at market order.
            if self._get_spread() < 0:
                lst_sides = [arms[1], arms[0]]
                lst_prices = [lst_spread[1][1][0], lst_spread[1][1][1], lst_spread[0][0][0], lst_spread[0][0][1]]

            side_0_qty = lst_sides[0].get("start_param").get("order_op_qty")
            side_1_qty = lst_sides[1].get("start_param").get("order_op_qty")

            if self._get_spread() != 0 and lst_prices[0] >= side_0_qty and lst_prices[1] >= side_1_qty:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
                self._lst_orders_sent.append({"id": timestamp, "cl_ord_id": self._profitdll.send_buy_order(
                    conta=lst_sides[0].get("broker").get("account"),
                    broker=lst_sides[0].get("broker").get("id"),
                    senha=lst_sides[0].get("broker").get("password"),
                    ativo=lst_sides[0].get("symbol"),
                    bolsa=lst_sides[0].get("stock_market"),
                    preco=lst_prices[1],
                    qtd=side_0_qty
                )})
                self._lst_orders_sent.append({"id": timestamp, "cl_ord_id": self._profitdll.send_sell_order(
                    conta=lst_sides[1].get("broker").get("account"),
                    broker=lst_sides[1].get("broker").get("id"),
                    senha=lst_sides[1].get("broker").get("password"),
                    ativo=lst_sides[1].get("symbol"),
                    bolsa=lst_sides[1].get("stock_market"),
                    preco=lst_prices[3],
                    qtd=side_1_qty
                )})

        self._position_mgr.proc_positions()

        # exit point
        if self._get_spread() != 0:
            for pos in self._position_mgr.get_lst_positions([PositionMgr.POS_OPENED], [PositionMgr.POS_INIT]):
                for ordr in pos.get("open_arms"):

                    '''
                    order = {
                        "corretora": corretora, "qtd": qtd, "traded_qtd": traded_qtd, "leaves_qtd": leaves_qtd,
                        "side": side, "price": price, "stop_price": stop_price, "avg_price": avg_price, 
                        "profit_id": profit_id, "tipo_ordem": tipo_ordem, "conta": conta, "titular": titular, 
                        "cl_ord_id": cl_ord_id, "status": status, "date": date, "symbol": asset_id.ticker,
                    }
                    '''

                    thr_sel = None
                    lst_spread = self._dct_inst.get("spread")
                    for thr in arms:
                        if thr.ge("symbol") == ordr.get("symbol"):
                            thr_sel = thr
                            break

                    if ordr.get("side") == "S":
                        self._lst_orders_sent.append({"id": None, "cl_ord_id": self._profitdll.send_buy_order(
                            conta=thr_sel.get("broker").get("account"), broker=thr_sel.get("broker").get("id"),
                            senha=thr_sel.get("broker").get("password"),
                            ativo=thr_sel.get("symbol"), bolsa=thr_sel.get("stock_market"),
                            preco=lst_spread[0][1], qtd=thr_sel.get("qtd")

                        )})
                    else:
                        self._lst_orders_sent.append({"id": None, "cl_ord_id": self._profitdll.send_sell_order(
                            conta=thr_sel.get("broker").get("account"), broker=thr_sel.get("broker").get("id"),
                            senha=thr_sel.get("broker").get("password"),
                            ativo=thr_sel.get("symbol"), bolsa=thr_sel.get("stock_market"),
                            preco=lst_spread[1][0], qtd=thr_sel.get("qtd")
                        )})

    def _get_spread(self):
        """
        This algo is Desgigned to work with 2 assets simultaneously.
        The spreado of each asset has a list with two lists inside, one for 'BUY' side other for 'SELL' side,
        in this order.
            lst_spread[[[qtd, price], [qtd, price]], [[qtd, price], [qtd, price]]]

        :return: the spread.
        """
        lst_spread = self._dct_inst.get("spread")
        return lst_spread[1][1][0] - lst_spread[0][0][0]
