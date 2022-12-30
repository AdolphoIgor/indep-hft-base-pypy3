from datetime import datetime

from api.bots.hft.bot import Bot
from api.bots.hft.position import PositionMgr
from api.jobs.internal_config_provider import InternalConfigProviders


class Arbitrage(Bot):

    def __init__(self, name, daemon, algo: dict, config_prov: InternalConfigProviders):
        super().__init__(name, daemon, algo, Bot.TWO_ARM, config_prov)

    def _get_signal(self):
        lst_spread = list(self._dct_inst.get("spread").values())
        return [(lst_spread[0][0][1] - lst_spread[1][1][1]) > 0, (lst_spread[1][0][1] - lst_spread[0][1][1]) > 0], \
            lst_spread

    def execute(self):
        # entry point
        arms = self._position_mgr.get_pos_arms()
        if self._is_asset_state(["opened"]) and arms[0].get("position").get("has_ord_rem") and \
                arms[1].get("position").get("has_ord_rem"):

            arm_0_qty = arms[0].get("start_param").get("order_op_qty")
            arm_1_qty = arms[1].get("start_param").get("order_op_qty")

            tpl_arm_0 = (
                arms[0].get("broker").get("account"),
                arms[0].get("broker").get("id"),
                arms[0].get("broker").get("password"),
                arms[0].get("symbol"),
                arms[0].get("stock_market"),
                arm_0_qty
            )

            tpl_arm_1 = (
                arms[1].get("broker").get("account"),
                arms[1].get("broker").get("id"),
                arms[1].get("broker").get("password"),
                arms[1].get("symbol"),
                arms[1].get("stock_market"),
                arm_1_qty
            )

            lst_sides = [
                (tpl_arm_0, tpl_arm_1),
                (tpl_arm_1, tpl_arm_0)
            ]

            lst_signal, lst_spread = self._get_signal()
            if any(lst_signal):
                if lst_signal[0]:
                    lst_sides = lst_sides[0]
                    lst_prices = [lst_spread[0][0][0], lst_spread[0][0][1], lst_spread[1][1][0], lst_spread[1][1][1]]
                else:
                    lst_sides = lst_sides[1]
                    lst_prices = [lst_spread[1][0][0], lst_spread[1][0][1], lst_spread[0][1][0], lst_spread[0][1][1]]

                if lst_prices[0] < lst_sides[0][-1] and lst_prices[1] < lst_sides[1][-1]:
                    return

                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
                self._lst_orders_sent.append({"id": timestamp, "cl_ord_id": self._profitdll.send_buy_order(
                    conta=lst_sides[0][0], broker=lst_sides[0][1], senha=lst_sides[0][2], ativo=lst_sides[0][3],
                    bolsa=lst_sides[0][4], preco=lst_prices[1], qtd=lst_sides[0][5]
                )})
                self._lst_orders_sent.append({"id": timestamp, "cl_ord_id": self._profitdll.send_sell_order(
                    conta=lst_sides[1][0], broker=lst_sides[1][1], senha=lst_sides[1][2], ativo=lst_sides[1][3],
                    bolsa=lst_sides[1][4], preco=lst_prices[3], qtd=lst_sides[1][5]
                )})

        self._position_mgr.proc_positions()

        # exit point
        if not any(self._get_signal()):
            for pos in self._position_mgr.get_lst_positions([PositionMgr.POS_OPENED], [PositionMgr.POS_INIT]):
                for ordr in pos.get("open_arms"):
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
