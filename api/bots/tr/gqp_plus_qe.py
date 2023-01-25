from datetime import datetime

from api.bots.bot import Bot
from api.bots.tr.momentum import Momentum
from api.bots.tr.position import PositionMgr
from api.bots.tr.tr_bot import TRBot
from api.jobs.internal_config_provider import InternalConfigProviders


class GoodQueuePlaceWithQueueEnding(TRBot):

    def __init__(self, name, daemon, algo: dict, config_prov: InternalConfigProviders):
        super().__init__(name, daemon, algo, Bot.ARM_ONE, config_prov)
        self._dct_pos_threads = self._position_mgr.get_pos_arms()

        self._momentum = Momentum()

        self._arms = self._position_mgr.get_pos_arms()
        self._tpl_arm = (
            self._arms[0].get("broker").get("account"),
            self._arms[0].get("broker").get("id"),
            self._arms[0].get("broker").get("password"),
            self._arms[0].get("symbol"),
            self._arms[0].get("stock_market"),
            self._arms[0].get("start_param").get("order_op_qty") * self._arms[0].get("lote")
        )
        self._qtd_ff = self._arms[0].get("start_param").get("order_op_qty") * 3

    def _execute(self):
        """
           Desafio: tem qu ler o fluxo de ordens para saber de que lado entrar

           ATENÇÂO: Este tipo de operação é para somente uma trade simultaneo.
        """

        # entry point.
        self._arms = self._position_mgr.get_pos_arms()
        if not self._is_asset_state(["opened"]) and self._position_mgr.get_pos().get("qtd_open_positions") == 0:
            return

        if self._arms[0].get("position").get("has_ord_rem"):
            lst_lp = self._dct_inst.get("lp")
            lst_mm = self._momentum.get_momentum(self._dct_inst.get("tt"))
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")

            # [[[price, qtd, count], [price, qtd, count]], [[price, qtd, count], [price, qtd, count]]]
            # buy
            if lst_mm[3] and lst_lp[1][0][1] <= self._qtd_ff:
                lst_sides = [lst_lp[1][0][0], lst_lp[1][1][0], lst_lp[0][0][0]]

                self._lst_orders_sent.append({"id": timestamp, "cl_ord_id": self._profit_dll.send_buy_order(
                    conta=self._tpl_arm[0], broker=self._tpl_arm[1], senha=self._tpl_arm[2], ativo=self._tpl_arm[3],
                    bolsa=self._tpl_arm[4], preco=lst_sides[0], qtd=self._tpl_arm[5])})

            # sell
            elif lst_mm[4] and lst_lp[0][0][1] <= self._qtd_ff:
                lst_sides = [lst_lp[0][0][0], lst_lp[0][1][0], lst_lp[1][0][0]]

                self._lst_orders_sent.append({"id": timestamp, "cl_ord_id": self._profit_dll.send_sell_order(
                    conta=self._tpl_arm[0], broker=self._tpl_arm[1], senha=self._tpl_arm[2], ativo=self._tpl_arm[3],
                    bolsa=self._tpl_arm[4], preco=lst_sides[0], qtd=self._tpl_arm[5])})

            self._position_mgr.proc_positions()

            # Se a ordem não foi executada, cancela o trade.
            lst_new_ordrs = [
                ordr for pos in self._position_mgr.get_lst_positions([PositionMgr.POS_NEW], [PositionMgr.POS_INIT])
                for ordr in pos.get("open_arms") if ordr.get("status") == "New"
            ]

            if lst_new_ordrs:
                for ordr in lst_new_ordrs:
                    self._lst_orders_sent.append({"id": None, "cl_ord_id": self._profit_dll.send_cancel_order(
                        conta=self._tpl_arm[0], broker=self._tpl_arm[1], senha=self._tpl_arm[2],
                        cl_ord_id=ordr.get("cl_ord_id")
                    )})

                return

        if self._is_asset_state(["opened"]):

            self._position_mgr.proc_positions()

            """
                pegar a ordem executada e ainda não zerada e já colocar a ordem de saída GAIN no nivel certo...
            """
            if self._position_mgr.get_pos().get("qtd_open_positions") > 0:
                lst_exec_ordrs = [
                    ordr for pos in self._position_mgr.get_lst_positions(
                        [PositionMgr.POS_PRT_OPENED, PositionMgr.POS_OPENED], [PositionMgr.POS_INIT])
                    for ordr in pos.get("open_arms")
                    if ordr.get("status") in ["PartiallyFilled", "Filled"]
                ]

                lst_sprd = self._dct_inst.get("spread")
                for ordr in lst_exec_ordrs:
                    lst_book = lst_sprd[0] if ordr.get("side") == "B" else lst_sprd[1]

                    # se a ordem foi executada parcialmente (na abertura), cancelar o saldo restante
                    if ordr.get("qtd") != ordr.get("traded_qtd"):
                        self._lst_orders_sent.append({"id": None, "cl_ord_id": self._profit_dll.send_cancel_order(
                            conta=self._dct_pos_threads.get("broker").get("account"),
                            broker=self._dct_pos_threads.get("broker").get("id"),
                            senha=self._dct_pos_threads.get("broker").get("password"),
                            cl_ord_id=ordr.get("cl_ord_id")
                        )})

                    if ordr.get("side") == "B":
                        self._lst_orders_sent.append({"id": None, "cl_ord_id": self._profit_dll.send_sell_order(
                            conta=self._dct_pos_threads.get("broker").get("account"),
                            broker=self._dct_pos_threads.get("broker").get("id"),
                            senha=self._dct_pos_threads.get("broker").get("password"),
                            ativo=self._dct_pos_threads.get("symbol"),
                            bolsa=self._dct_pos_threads.get("stock_market"),
                            preco=lst_book[0][1],
                            qtd=ordr.get("traded_qtd")
                        )})
                    else:
                        self._lst_orders_sent.append({"id": None, "cl_ord_id": self._profit_dll.send_buy_order(
                            conta=self._dct_pos_threads.get("broker").get("account"),
                            broker=self._dct_pos_threads.get("broker").get("id"),
                            senha=self._dct_pos_threads.get("broker").get("password"),
                            ativo=self._dct_pos_threads.get("symbol"),
                            bolsa=self._dct_pos_threads.get("stock_market"),
                            preco=lst_book[0][1],
                            qtd=ordr.get("traded_qtd")
                        )})

                self._position_mgr.proc_positions()

            """
                monitorar a fila de execução, se chegar a 80% enviar ordem stop e cancelar a ordem de saída GAIN.
            """
            while self._position_mgr.get_pos().get("qtd_open_positions"):

                lst_new_ordrs = [
                    ordr for pos in self._position_mgr.get_lst_positions(
                        [PositionMgr.POS_OPENED], [PositionMgr.POS_NEW, PositionMgr.POS_PRT_EXEC])
                    for ordr in pos.get("open_arms") if ordr.get("status") in ["New", "PartiallyFilled"]
                ]

                '''
                order = {
                    "corretora": corretora, "qtd": qtd, "traded_qtd": traded_qtd, "leaves_qtd": leaves_qtd,
                    "side": side, "price": price, "stop_price": stop_price, "avg_price": avg_price, 
                    "profit_id": profit_id, "tipo_ordem": tipo_ordem, "conta": conta, "titular": titular, 
                    "cl_ord_id": cl_ord_id, "status": status, "date": date, "symbol": asset_id.ticker,
                }
                '''

                lst_sprd = self._dct_inst.get("spread")
                for ordr in lst_new_ordrs:

                    lst_book = lst_sprd[0] if ordr.get("side") == "B" else lst_sprd[1]

                    if lst_book[0][1] == ordr.get("price") and (lst_book[0][0] * 3) <= ordr.get("qtd"):
                        self._lst_orders_sent.append({"id": None, "cl_ord_id": self._profit_dll.send_cancel_order(
                            conta=self._dct_pos_threads.get("broker").get("account"),
                            broker=self._dct_pos_threads.get("broker").get("id"),
                            senha=self._dct_pos_threads.get("broker").get("password"),
                            cl_ord_id=ordr.get("cl_ord_id")
                        )})

                        if ordr.get("side") == "B":
                            self._lst_orders_sent.append({"id": None, "cl_ord_id": self._profit_dll.send_buy_order(
                                conta=self._dct_pos_threads.get("broker").get("account"),
                                broker=self._dct_pos_threads.get("broker").get("id"),
                                senha=self._dct_pos_threads.get("broker").get("password"),
                                ativo=self._dct_pos_threads.get("symbol"),
                                bolsa=self._dct_pos_threads.get("stock_market"),
                                preco=lst_book[0][1],
                                qtd=ordr.get("leaves_qtd")
                            )})

                        else:
                            self._lst_orders_sent.append({"id": None, "cl_ord_id": self._profit_dll.send_sell_order(
                                conta=self._dct_pos_threads.get("broker").get("account"),
                                broker=self._dct_pos_threads.get("broker").get("id"),
                                senha=self._dct_pos_threads.get("broker").get("password"),
                                ativo=self._dct_pos_threads.get("symbol"),
                                bolsa=self._dct_pos_threads.get("stock_market"),
                                preco=lst_book[0][1],
                                qtd=ordr.get("leaves_qtd")
                            )})

                self._position_mgr.proc_positions()
