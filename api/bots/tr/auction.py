import multiprocessing
import time

from api.bots.bot import Bot
from api.jobs.internal_config_provider import InternalConfigProviders
from api.logger import logger
from api.utils.parallelism.ThreadPool import ThreadPool


class Auction(Bot):
    MAX_PROCESS = int(multiprocessing.cpu_count() / 2)
    # MAX_PROCESS_WORKERS = MAX_PROCESS * 16
    MAX_PROCESS_WORKERS = 1

    _thread_pool = None

    def __init__(self, name, daemon, algo: dict, config_prov: InternalConfigProviders):
        super().__init__(name, daemon, algo, Bot.ARM_ONE, config_prov)

        self.__stop_limit = self._algo.get("stop_param")["stop_limit"]
        self.__opening_volume = self._algo.get("start_param").get("threshold")["opening_volume"]

    def enqueue_auction(self, sbl):
        if not self._thread_pool:
            self._thread_pool = ThreadPool(self.dequeue_auction, max_workers=self.MAX_PROCESS_WORKERS,
                                           prefixo="AUCTION", queue_max_size=self.MAX_PROCESS_WORKERS * 2)

        return self._thread_pool.enfilera_job(**{'job': sbl})

    def enqueue_auction_return(self) -> list:
        return self._thread_pool.get_retorno()

    def dequeue_auction(self, fila, retorno, thread_name):

        while not fila.empty():
            value = None
            try:
                value = fila.get()
                logger.info(f"{thread_name}: Now processing {value[0]}...")
                retorno.append(self._run_algo(value))

            except Exception as e:
                logger.info(f"{thread_name}: There was a problem at processing.")
                retorno.append({'exception': str(e)})

            finally:
                fila.task_done()
                logger.info(f"{thread_name}: The processing to {value[0]} has been done!")

    def __get_entry_signal(self, symbol: str):
        dct_quote = self._dct_inst.get("quote").get(symbol)
        print(f"LOG dct_quote: {dct_quote}")
        lst_book = self._dct_inst.get("lp").get(symbol)
        print(f"LOG lst_book: {lst_book}")
        return

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
        time_sleep = 5
        dct_enqueued = {}
        while self.__stop_limit < 0:
            lst_act_sbls = [[sbl, quote] for sbl, quote in self._dct_inst.get("quote").items()
                            if quote.get("state") == 4 and sbl not in dct_enqueued and
                            quote.get("vol", 0) >= self.__opening_volume]

            if not lst_act_sbls:
                break

            # shows the progress of the server's response
            # self._config_prov._lst_config_pool[1].get("value")[8].get('value').get("CMSA3")

            lst_act_sbls.sort(key=(lambda x: x[1].get("vol")), reverse=True)
            lst_act_sbls = lst_act_sbls[:self.MAX_PROCESS_WORKERS]

            for sbl in lst_act_sbls:
                for thr in self._algo.get("threads"):
                    if sbl[0] == thr.get("symbol"):
                        if len(sbl) == 2:
                            sbl.append(thr)
                            sbl.append({})

                        if not self.enqueue_auction(sbl):
                            time.sleep(time_sleep)
                            if time_sleep <= 300:  # 5 min
                                time_sleep *= 2
                        else:
                            dct_enqueued[sbl[0]] = sbl[1:]

            lst_ret = self.enqueue_auction_return()[:]
            for ret in lst_ret:
                dct_thr = dct_enqueued.get(ret[1])[2]
                dct_pos = self._profit_dll.get_position(
                    conta=dct_thr.get("broker").get("account"), broker=dct_thr.get("broker").get("id"),
                    ativo=dct_thr.get("symbol"), bolsa=dct_thr.get("stock_market")
                )

                intraday_pos = dct_pos.get("intraday_pos")
                if intraday_pos <= 0:
                    logger.info(f"AUCTION: The {ret[1]} stop was reached.")

                self.__stop_limit += dct_pos.get("intraday_pos")
                if self.__stop_limit <= 0:
                    logger.info(f"AUCTION: The daily stop was reached.")

                dct_enqueued.pop(ret[1])
                time_sleep = 5

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

        while self.__stop_limit <= 0 and dct_quote.get("state") == 4:
            lst_entry_signal = self.__get_entry_signal(str_symbol)

            # TODO: remover apos debug
            continue

            if self.__stop_limit <= 0 and lst_entry_signal[2] > 2 and not dct_vars.get("order_placed"):
                if self.__stop_limit <= 0 and lst_entry_signal[0] == "B":
                    self._profit_dll.send_buy_order(
                        conta=dct_thr.get("broker").get("account"),
                        broker=dct_thr.get("broker").get("id"),
                        senha=dct_thr.get("broker").get("password"),
                        ativo=str_symbol,
                        bolsa=dct_thr.get("stock_market"),
                        preco=dct_quote.get("quote").get("theoretical_price"),
                        qtd=dct_thr.get("start_param").get("order_op_qty") * dct_thr.get("lote")
                    )

                    dct_vars["order_placed"] = True

                elif self.__stop_limit <= 0 and lst_entry_signal[0] == "S":
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

            # Wheather the order was pulled out of the auction.
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
        if not dct_quote.get("state") == 4 and not dct_vars.get("order_placed"):
            return str_symbol, False

        time.sleep(5)

        # The auction reach the end but the order wasn't fullfiled (cancel it and return).
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
            return str_symbol, False

        # The auction reach the end but the order weren't totally fullfiled.
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

        return str_symbol, False
