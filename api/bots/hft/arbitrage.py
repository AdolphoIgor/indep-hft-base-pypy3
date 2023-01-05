from datetime import datetime

from api.bots.tr.bot import Bot
from api.bots.tr.position import PositionMgr
from api.jobs.internal_config_provider import InternalConfigProviders


class Arbitrage(Bot):

    _pos_ok = True

    def __init__(self, name, daemon, algo: dict, config_prov: InternalConfigProviders):
        super().__init__(name, daemon, algo, Bot.TWO_ARM, config_prov)
        self._arms = self._position_mgr.get_pos_arms()

        self._tpl_arm_0 = (
            self._arms[0].get("broker").get("account"),
            self._arms[0].get("broker").get("id"),
            self._arms[0].get("broker").get("password"),
            self._arms[0].get("symbol"),
            self._arms[0].get("stock_market"),
            self._arms[0].get("start_param").get("order_op_qty")
        )

        self._tpl_arm_1 = (
            self._arms[1].get("broker").get("account"),
            self._arms[1].get("broker").get("id"),
            self._arms[1].get("broker").get("password"),
            self._arms[1].get("symbol"),
            self._arms[1].get("stock_market"),
            self._arms[1].get("start_param").get("order_op_qty")
        )

        self._lst_sides = [
            (self._tpl_arm_0, self._tpl_arm_1),
            (self._tpl_arm_1, self._tpl_arm_0)
        ]

    def _get_signal(self):
        lst_spread = list(self._dct_inst.get("spread").values())
        return [(lst_spread[0][0][1] - lst_spread[1][1][1]) > 0, (lst_spread[1][0][1] - lst_spread[0][1][1]) > 0], \
            lst_spread

    def _execute(self):
        # entry point

        self._arms = self._position_mgr.get_pos_arms()
        if self._pos_ok:
            if self._is_asset_state(["opened"]) and self._arms[0].get("position").get("has_ord_rem") and \
                    self._arms[1].get("position").get("has_ord_rem"):

                lst_signal, lst_spread = self._get_signal()
                # TODO: Retirar
                lst_signal = [True, False]
                if any(lst_signal):
                    if lst_signal[0]:
                        lst_sides = self._lst_sides[0]
                        lst_prices = [lst_spread[0][0][0], lst_spread[0][0][1], lst_spread[1][1][0], lst_spread[1][1][1]]
                    else:
                        lst_sides = self._lst_sides[1]
                        lst_prices = [lst_spread[1][0][0], lst_spread[1][0][1], lst_spread[0][1][0], lst_spread[0][1][1]]

                    if lst_prices[0] < lst_sides[0][-1] and lst_prices[1] < lst_sides[1][-1]:
                        return

                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
                    self._lst_orders_sent.append({"id": timestamp, "profit_id": self._profit_dll.send_buy_order(
                        conta=lst_sides[0][0], broker=lst_sides[0][1], senha=lst_sides[0][2], ativo=lst_sides[0][3],
                        bolsa=lst_sides[0][4], preco=lst_prices[1], qtd=lst_sides[0][5]
                    )})
                    self._lst_orders_sent.append({"id": timestamp, "profit_id": self._profit_dll.send_sell_order(
                        conta=lst_sides[1][0], broker=lst_sides[1][1], senha=lst_sides[1][2], ativo=lst_sides[1][3],
                        bolsa=lst_sides[1][4], preco=lst_prices[3], qtd=lst_sides[1][5]
                    )})

        self._pos_ok = self._position_mgr.proc_positions()

        # exit point
        if self._pos_ok:
            lst_signal, _ = self._get_signal()
            # TODO: Retirar
            lst_signal = [False, False]
            if not any(lst_signal):
                for pos in self._position_mgr.get_lst_positions([PositionMgr.POS_OPENED], [PositionMgr.POS_INIT]):
                    for ordr in pos.get("open_arms"):
                        thr_sel = None
                        lst_spread = self._dct_inst.get("spread")
                        for thr in self._arms:
                            if thr.ge("symbol") == ordr.get("symbol"):
                                thr_sel = thr
                                break

                        if ordr.get("side") == "S":
                            self._lst_orders_sent.append({"id": None, "profit_id": self._profit_dll.send_buy_order(
                                conta=thr_sel.get("broker").get("account"), broker=thr_sel.get("broker").get("id"),
                                senha=thr_sel.get("broker").get("password"),
                                ativo=thr_sel.get("symbol"), bolsa=thr_sel.get("stock_market"),
                                preco=lst_spread[0][1], qtd=thr_sel.get("qtd")

                            )})
                        else:
                            self._lst_orders_sent.append({"id": None, "profit_id": self._profit_dll.send_sell_order(
                                conta=thr_sel.get("broker").get("account"), broker=thr_sel.get("broker").get("id"),
                                senha=thr_sel.get("broker").get("password"),
                                ativo=thr_sel.get("symbol"), bolsa=thr_sel.get("stock_market"),
                                preco=lst_spread[1][0], qtd=thr_sel.get("qtd")
                            )})
