import multiprocessing
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from api.bots.bot import Bot
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
                    sbl.append({})

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

        dct_vars["order_placed"] = False
        lst_orders = self._dct_inst.get("orders", {}).get(str_symbol, None)

        while dct_quote.get("state") == "auctioned":
            lst_entry_signal = self.__get_entry_signal()

            if lst_entry_signal[2] > 2 and not dct_vars.get("order_placed"):
                if lst_entry_signal[0] == "B":
                    self._profit_dll.send_buy_order(
                        conta=dct_thr.get("broker").get("account"),
                        broker=dct_thr.get("broker").get("id"),
                        senha=dct_thr.get("broker").get("password"),
                        ativo=str_symbol,
                        bolsa=dct_thr.get("stock_market"),
                        preco=dct_quote.get("quote").get("theoretical_price"),
                        qtd=dct_thr.get("start_param").get("order_op_qty") * dct_thr.get("lote")
                    )
                else:
                    self._profit_dll.send_sell_order(
                        conta=dct_thr.get("broker").get("account"),
                        broker=dct_thr.get("broker").get("id"),
                        senha=dct_thr.get("broker").get("password"),
                        ativo=str_symbol,
                        bolsa=dct_thr.get("stock_market"),
                        preco=dct_quote.get("quote").get("theoretical_price"),
                        qtd=dct_thr.get("start_param").get("order_op_qty") * dct_thr.get("lote")
                    )

                dct_vars["order_placed"] = True

            if not dct_vars.get("order_placed"):
                time.sleep(0.00001)
                continue

            # Se a ordem nova ficou fora da formação do preço teórico, cancela e espera novo sinal.
            dct_ord_0 = self._get_order_w_status(lst_orders, "New")
            if not dct_ord_0:
                time.sleep(0.00001)
                continue

            if dct_ord_0.get("price") != dct_quote.get("theoretical_price"):
                self._profit_dll.send_cancel_order(
                    conta=dct_thr.get("broker").get("account"),
                    broker=dct_thr.get("broker").get("id"),
                    senha=dct_thr.get("broker").get("password"),
                    cl_ord_id=dct_ord_0.get("cl_ord_id")
                )

                while True:
                    dct_ord_0 = self._get_order_w_status(lst_orders, "Cancel")
                    if dct_ord_0:
                        lst_orders.clear()
                        dct_vars["order_placed"] = False
                        break

                    time.sleep(0.00001)

        # The auction reach the end without placing any orders (nothing to do).
        if not dct_quote.get("state") == "auctioned" and not dct_vars.get("order_placed"):
            return

        time.sleep(1)

        # The auction reach the end but the order weren't fullfiled (cancel it and return).
        dct_ord_0 = self._get_order_w_status(lst_orders, "New")
        if dct_ord_0:
            self._profit_dll.send_cancel_order(
                conta=dct_thr.get("broker").get("account"),
                broker=dct_thr.get("broker").get("id"),
                senha=dct_thr.get("broker").get("password"),
                cl_ord_id=dct_ord_0.get("cl_ord_id")
            )

            while True:
                dct_ord_0 = self._get_order_w_status(lst_orders, "Cancel")
                if dct_ord_0:
                    lst_orders.clear()
                    dct_vars["order_placed"] = False
                    break

            time.sleep(0.00001)
            return

        # The auction reach the end but the order weren't fullfiled.
        dct_ord_0 = self._get_order_w_status(lst_orders, "PartiallyFilled")
        if dct_ord_0:
            self._profit_dll.send_cancel_order(
                conta=dct_thr.get("broker").get("account"),
                broker=dct_thr.get("broker").get("id"),
                senha=dct_thr.get("broker").get("password"),
                cl_ord_id=dct_ord_0.get("cl_ord_id")
            )

        lst_sprd = self._dct_inst.get("spread")
        lst_book = lst_sprd[0] if dct_ord_0.get("side") == "B" else lst_sprd[1]
        while True:
            time.sleep(0.00001)
            if lst_book[0][1] == dct_ord_0.get("price") and (lst_book[0][0] * 3) <= dct_ord_0.get("traded_qtd"):
                if dct_ord_0.get("size") == 1:
                    self._profit_dll.send_stop_buy_order(
                        conta=dct_thr.get("broker").get("account"),
                        broker=dct_thr.get("broker").get("id"),
                        senha=dct_thr.get("broker").get("password"),
                        ativo=str_symbol,
                        bolsa=dct_thr.get("stock_market"),
                        preco=lst_book[0][1],
                        s_stop_price=lst_book[0][1],
                        qtd=dct_ord_0.get("traded_qtd")
                    )
                else:
                    self._profit_dll.send_stop_sell_order(
                        conta=dct_thr.get("broker").get("account"),
                        broker=dct_thr.get("broker").get("id"),
                        senha=dct_thr.get("broker").get("password"),
                        ativo=str_symbol,
                        bolsa=dct_thr.get("stock_market"),
                        preco=lst_book[0][1],
                        s_stop_price=lst_book[0][1],
                        qtd=dct_ord_0.get("traded_qtd")
                    )

                break
