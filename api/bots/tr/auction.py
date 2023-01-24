import multiprocessing
from concurrent.futures import ThreadPoolExecutor, as_completed

from api.bots.bot import Bot
from api.bots.tr.position import PositionMgr
from api.jobs.internal_config_provider import InternalConfigProviders


class Auction(Bot):
    MAX_PROCESS = int(multiprocessing.cpu_count() / 2)
    MAX_PROCESS_WORKERS = MAX_PROCESS * 16

    def __init__(self, name, daemon, algo: dict, config_prov: InternalConfigProviders):
        super().__init__(name, daemon, algo, Bot.ARM_ONE, config_prov)

    def __get_entry_signal(self):
        lst_book = self._dct_inst.get("lp")
        lst_lp = [lst_book[0], lst_book[1]]
        qtd = lst_lp[0][0][0] - lst_lp[1][0][0] + lst_lp[0][1][0] - lst_lp[1][1][0]

        qtd = abs(qtd)
        nivel_p_dentro = 2
        lst_niv_menor_liq = None
        side = "B" if qtd > 0 else "S"
        while True:
            if qtd <= 0:
                break

            try:
                idx = 1 if side == "B" else 0
                qtd_nivel = lst_lp[idx][nivel_p_dentro][0]
                prc_nivel = lst_lp[idx][nivel_p_dentro][1]
                qtd -= qtd_nivel

            except Exception:
                break

            if nivel_p_dentro == 2:
                lst_niv_menor_liq = [nivel_p_dentro, qtd_nivel, prc_nivel]

            elif lst_niv_menor_liq[1] > qtd_nivel:
                lst_niv_menor_liq[0] = nivel_p_dentro
                lst_niv_menor_liq[1] = qtd_nivel
                lst_niv_menor_liq[2] = prc_nivel

            nivel_p_dentro += 1

        return [side, qtd, nivel_p_dentro, lst_niv_menor_liq]

    def _execute(self):
        lst_act_sbls = [[sbl, quote] for sbl, quote in self._dct_inst.get("quote").item()
                        if quote.get("state") == "auctioned"]

        lst_act_sbls = lst_act_sbls.sort(key=(lambda x: x.get("vol")))[:self.MAX_PROCESS_WORKERS]

        for sbl in lst_act_sbls:
            for thr in self._algo.get("threads"):
                if sbl[0] == thr.get("symbol"):
                    sbl.append(thr)
                    sbl.append({"pos_opened": False})

        lst_retornos = []
        with ThreadPoolExecutor(max_workers=self.MAX_PROCESS_WORKERS) as executor:
            lst_thr = [executor.submit(self._run_algo, item) for item in lst_act_sbls]

            for thread in as_completed(lst_thr):
                lst_retornos.append((thread.result(), thread.exception()))

    def _run_algo(self, item: tuple):
        """
            {
                "date": date, "open_val": open_val, "high": high, "low": low, "close": close, "vol": vol,
                "ajuste": ajuste, "max_limit": max_limit, "min_limit": min_limit, "vol_buyer": vol_buyer,
                "vol_seller": vol_seller, "qtd": qtd, "negocios": negocios, "contratos_open": contratos_open,
                "qtd_buyer": qtd_buyer, "qtd_seller": qtd_seller, "neg_buyer": neg_buyer,
                "neg_seller": neg_seller
            }
        """
        str_symbol = item[0]
        dct_quote = item[1]
        dct_thr = item[2]
        dct_vars = item[3]

        lst_orders = self._dct_inst.get("orders", {}).get(str_symbol, None)

        while dct_quote.get("state") == "auctioned":
            self._lst_entry_signal = self.__get_entry_signal()

            if self._lst_entry_signal[2] > 2 and not dct_vars.get("order_placed", False):
                if self._lst_entry_signal[0] == "B":
                    self._profit_dll.send_buy_order(
                        conta=dct_thr.get("broker").get("account"),
                        broker=dct_thr.get("broker").get("id"),
                        senha=dct_thr.get("broker").get("password"),
                        ativo=str_symbol,
                        bolsa=dct_thr.get("stock_market"),
                        preco=dct_quote.get("quote").get("theoretical_price"),
                        qtd=dct_thr.get("start_param").get("order_op_qty")
                    )
                else:
                    self._profit_dll.send_sell_order(
                        conta=dct_thr.get("broker").get("account"),
                        broker=dct_thr.get("broker").get("id"),
                        senha=dct_thr.get("broker").get("password"),
                        ativo=str_symbol,
                        bolsa=dct_thr.get("stock_market"),
                        preco=dct_quote.get("quote").get("theoretical_price"),
                        qtd=dct_thr.get("start_param").get("order_op_qty")
                    )

                dct_vars["order_placed"] = True

            # Se a ordem nova ficou fora da formação do preço teórico, cancela e espera novo sinal.
            dct_ord_0 = self._get_order_w_status(lst_orders, "New")
            if dct_ord_0:
                if dct_ord_0.get("price") != dct_quote.get("theoretical_price"):
                    self._profit_dll.send_cancel_order(
                        conta=dct_thr.get("broker").get("account"),
                        broker=dct_thr.get("broker").get("id"),
                        senha=dct_thr.get("broker").get("password"),
                        cl_ord_id=dct_ord_0.get("cl_ord_id")
                    )
                lst_orders.remove(dct_ord_0)

                dct_ord_0 = self._get_order_w_status(lst_orders, "Cancel")
                if dct_ord_0:
                    lst_orders.clear()

                dct_vars["order_placed"] = False

        """
            A saída nunca será dentro do leilão, prorrogação ou fase randomica...
        """
        if self._is_asset_state(["opened"]):

            self._position_mgr.proc_positions()

            # se abriu o mercado e a ordem de entrada não foi atendida, cancela a ordem.
            if self._position_mgr.get_pos().get("qtd_open_positions") == 0:
                lst_new_ordrs = [
                    ordr for pos in self._position_mgr.get_lst_positions([PositionMgr.POS_NEW], [PositionMgr.POS_INIT])
                    for ordr in pos.get("open_arms")
                    if ordr.get("status") == "New"
                ]

                if lst_new_ordrs:
                    for ordr in lst_new_ordrs:
                        self._lst_orders_sent.append({"id": None, "cl_ord_id": self._profit_dll.send_cancel_order(
                            conta=self._dct_pos_threads.get("broker").get("account"),
                            broker=self._dct_pos_threads.get("broker").get("id"),
                            senha=self._dct_pos_threads.get("broker").get("password"),
                            cl_ord_id=ordr.get("cl_ord_id")
                        )})
                    self._position_mgr.proc_positions()
                    return

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

                for ordr in lst_exec_ordrs:
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
                            preco=self._lst_entry_signal[3][2],
                            qtd=ordr.get("traded_qtd")
                        )})
                    else:
                        self._lst_orders_sent.append({"id": None, "cl_ord_id": self._profit_dll.send_buy_order(
                            conta=self._dct_pos_threads.get("broker").get("account"),
                            broker=self._dct_pos_threads.get("broker").get("id"),
                            senha=self._dct_pos_threads.get("broker").get("password"),
                            ativo=self._dct_pos_threads.get("symbol"),
                            bolsa=self._dct_pos_threads.get("stock_market"),
                            preco=self._lst_entry_signal[3][2],
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
