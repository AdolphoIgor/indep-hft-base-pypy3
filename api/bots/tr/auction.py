import multiprocessing
import time

# import api.utils.network.profit_dll_sim
from api.bots.bot import Bot
from api.bots.tr.auction_bot import AuctionBot
from api.jobs.internal_config_provider import InternalConfigProviders
from api.logger import logger
from api.utils.parallelism.ThreadPool import ThreadPool


class Auction(AuctionBot):
    MAX_PROCESS = int(multiprocessing.cpu_count() / 2)
    MAX_PROCESS_WORKERS = MAX_PROCESS * 16
    # MAX_PROCESS_WORKERS = 1

    _thread_pool = None

    def __init__(self, name, daemon, algo: dict, config_prov: InternalConfigProviders):
        super().__init__(name, daemon, algo, Bot.ARM_TOO_MANY, config_prov)

        self._stop_limit = self._algo.get("stop_param")["stop_limit"]
        self._opening_volume = self._algo.get("start_param").get("threshold")["opening_volume"]

    def enqueue_auction(self, sbl):
        if not self._thread_pool:
            self._thread_pool = ThreadPool(self.dequeue_auction, max_workers=self.MAX_PROCESS_WORKERS,
                                           prefixo="AUCTION", queue_max_size=self.MAX_PROCESS_WORKERS * 2)

        return self._thread_pool.enfilera_job(**{'job': sbl})

    def enqueue_auction_return(self) -> list:
        if not self._thread_pool:
            return []

        return self._thread_pool.get_retorno()

    def dequeue_auction(self, fila, retorno, thread_name):
        algo_name = None
        while not fila.empty():
            try:
                value = fila.get()
                if not algo_name:
                    algo_name = f"{self._algo.get('name')} - {value[0]}"

                logger.info(f"{thread_name}: Now processing {algo_name}...")
                retorno.append(self._run_algo(value))

            except Exception as e:
                logger.info(f"{thread_name}: There was a problem at processing {algo_name}.")
                retorno.append({'exception': str(e)})

            finally:
                fila.task_done()
                logger.info(f"{thread_name}: The {algo_name} processing has been done!")

    def _execute(self):
        if not self._dct_inst:
            return

        time_sleep = 5
        dct_enqueued = {}
        while self._stop_limit < 0:
            lst_act_sbls = [[sbl, quote.get("vol")] for sbl, quote in self._dct_inst.get("quote").items()
                            if quote.get("state") == 4 and sbl not in dct_enqueued and
                            quote.get("vol", 0) >= self._opening_volume and
                            quote.get("theoretical_price", 0) >= 0]

            if not lst_act_sbls:
                break

            lst_act_sbls.sort(key=(lambda x: x[1]), reverse=True)
            lst_act_sbls = lst_act_sbls[:self.MAX_PROCESS_WORKERS]

            for sbl in lst_act_sbls:
                for thr in self._algo.get("threads"):
                    if sbl[0] == thr.get("symbol"):

                        if not self._dct_inst:
                            continue

                        lp = self._dct_inst.get("lp")
                        if not lp:
                            continue

                        if not lp.get(sbl[0]):
                            continue

                        if len(sbl) == 2:
                            sbl.append(thr)
                            sbl.append({})

                        if self.enqueue_auction(sbl):
                            dct_enqueued[sbl[0]] = sbl[1:]
                            break

                        time.sleep(time_sleep)
                        if time_sleep <= 300:  # 5 min
                            time_sleep *= 2

            lst_ret = self.enqueue_auction_return()[:]
            for ret in lst_ret:
                symbol = list(ret)[0]
                if symbol != 'exception':

                    algo_name = f"{self._algo.get('name')} - {symbol}"

                    lst_pos = self._get_position()
                    if lst_pos[0] > 0:
                        logger.info(f"AUCTION: The {algo_name} stop was reached.")

                    self._stop_limit += lst_pos[0]
                    if self._stop_limit >= 0:
                        logger.info(f"AUCTION: The daily stop for {algo_name} was reached.")

                    dct_enqueued.pop(list(ret)[0])
                    time_sleep = 5

    def _run_algo(self, item: list):

        """
            change_state_ticker_callback -> callback que trata da mudança de estado do ativo.
        """

        def get_entry_signal(theo_price, lst_lp_book: list):
            lst_lp_book = [lst_lp_book[0][::-1], lst_lp_book[1][::-1]]
            lst_res = []
            for lside in lst_lp_book:
                qtd, i = 0, 0
                for ls in lside:
                    i += 1
                    qtd += ls[1]

                    if ls[0] == theo_price:
                        break

                lst_res.append([qtd, i])

            qtt_remain = lst_res[0][0] - lst_res[1][0]
            if qtt_remain > 0:
                lst_lp_book = lst_lp_book[0][lst_res[0][1]:]
            else:
                lst_lp_book = lst_lp_book[1][lst_res[1][1]:]

            qtt = abs(qtt_remain)
            max_prc, max_prc_lvl, bst_prc, bst_prc_lvl, qtt_lvl_lower = 0, 0, 0, 0, 0
            for lprc in lst_lp_book:
                if qtt <= 0:
                    break

                max_prc = lprc[0]
                max_prc_lvl += 1
                qtt -= lprc[1]

                if not qtt_lvl_lower or qtt_lvl_lower > lprc[1]:
                    bst_prc = lprc[0]
                    bst_prc_lvl = max_prc_lvl
                    qtt_lvl_lower = lprc[1]

            return ["S" if qtt_remain < 0 else "B", max_prc, max_prc_lvl, bst_prc, bst_prc_lvl]

        def get_lst_ordrs():
            dct_ordrs = self._dct_inst.get("orders", {})
            if not dct_ordrs:
                self._init_orders_instruments()

            return self._dct_inst.get("orders", {}).get(str_symbol, None)

        str_symbol = item[0]
        if self._stop_limit >= 0:
            return {str_symbol, False}

        dct_thr = item[2]
        dct_vars = item[3]
        lst_book = self._dct_inst.get("lp").get(str_symbol)
        dct_quote = self._dct_inst.get("quote").get(str_symbol)

        theoretical_price = 0

        lst_orders = None
        lst_entry_signal = None
        dct_vars["order_placed"] = False
        while self._stop_limit <= 0 and dct_quote.get("state") == 4:

            # logger.debug(f"{dct_thr.get('symbol')}-Em Leilão, sem stop limit.")
            if theoretical_price != dct_quote.get("theoretical_price"):
                theoretical_price = dct_quote.get("theoretical_price")

                logger.debug(f"theoretical_price: {theoretical_price}")
                logger.debug(f"lst_book[0]: {lst_book[0][:1]}")  # começo do book
                logger.debug(f"lst_book[0]: {lst_book[0][::-1][:1]}")  # topo do book
                logger.debug(f"lst_book[1]: {lst_book[1][:1]}")  # final do book
                logger.debug(f"lst_book[1]: {lst_book[1][::-1][:1]}")  # topo do book

            lst_entry_signal = get_entry_signal(theoretical_price, lst_book)
            if self._stop_limit <= 0 and lst_entry_signal[4] > 2 and not dct_vars.get("order_placed"):
                logger.debug(
                    f"{dct_thr.get('symbol')}-Em Leilão, sem stop limit, deu sinal de entrada. {lst_entry_signal}")

                # logger.debug(f"lst_book[0]: {lst_book[0][:1]}")  # começo do book
                # logger.debug(f"lst_book[0]: {lst_book[0][::-1][:1]}")  # topo do book
                #
                # logger.debug(f"lst_book[1]: {lst_book[1][:1]}")  # final do book
                # logger.debug(f"lst_book[1]: {lst_book[1][::-1][:1]}")  # topo do book

                if self._stop_limit <= 0 and lst_entry_signal[0] == "B":
                    self._profit_dll.send_buy_order(
                        conta=dct_thr.get("broker").get("account"),
                        broker=dct_thr.get("broker").get("id"),
                        senha=dct_thr.get("broker").get("password"),
                        ativo=str_symbol,
                        bolsa=dct_thr.get("stock_market"),
                        preco=dct_quote.get("theoretical_price"),
                        qtd=dct_thr.get("start_param").get("order_op_qty") * dct_thr.get("lote")
                    )

                    dct_vars["order_placed"] = True

                elif self._stop_limit <= 0 and lst_entry_signal[0] == "S":
                    self._profit_dll.send_sell_order(
                        conta=dct_thr.get("broker").get("account"),
                        broker=dct_thr.get("broker").get("id"),
                        senha=dct_thr.get("broker").get("password"),
                        ativo=str_symbol,
                        bolsa=dct_thr.get("stock_market"),
                        preco=dct_quote.get("theoretical_price"),
                        qtd=dct_thr.get("start_param").get("order_op_qty") * dct_thr.get("lote")
                    )

                    dct_vars["order_placed"] = True

                time.sleep(0.1)

                logger.debug(f"{dct_thr.get('symbol')}-Em Leilão, sem stop limit, deu entrada!")

            if not dct_vars.get("order_placed"):
                # logger.debug(f"{dct_thr.get('symbol')}-Em Leilão, sem stop limit, não deu entrada!")
                time.sleep(0.0001)
                continue

            if not lst_orders:
                logger.debug(f"{dct_thr.get('symbol')}-Em Leilão, sem stop limit, deu entrada mas ordem ainda não "
                             f"enviada...")
                time.sleep(0.1)
                lst_orders = get_lst_ordrs()

            # If there was some delay on the OMS response for the las limit order sended...
            dct_ord_0 = self._get_order_w_status(lst_orders, "New")
            if not dct_ord_0:
                logger.debug(f"{dct_thr.get('symbol')}-Em Leilão, sem stop limit, deu entrada mas ordem ainda não "
                             f"confirmada...")
                time.sleep(0.0001)
                continue

            # If limit order was pulled out of the auction.
            if dct_ord_0.get("price") != dct_quote.get("theoretical_price"):
                logger.debug(f"{dct_thr.get('symbol')}-Em Leilão, sem stop limit, deu entrada, ordem confirmada,"
                             f"mas saiu do preço teorico. Pr. Ord:{dct_ord_0.get('price')}, "
                             f"Pr. Teo:{dct_quote.get('theoretical_price')}")

                # logger.debug(f"lst_book[0]: {lst_book[0][:1]}") #começo do book
                # logger.debug(f"lst_book[0]: {lst_book[0][::-1][:1]}") #topo do book
                #
                # logger.debug(f"lst_book[1]: {lst_book[1][:1]}") #final do book
                # logger.debug(f"lst_book[1]: {lst_book[1][::-1][:1]}") #topo do book

                logger.debug(f"{dct_thr.get('symbol')}-Em Leilão, sem stop limit, deu entrada, ordem confirmada,"
                             f"mas saiu do preço teorico. Cancelando a ordem...")
                self._profit_dll.send_cancel_order(
                    conta=dct_thr.get("broker").get("account"),
                    broker=dct_thr.get("broker").get("id"),
                    senha=dct_thr.get("broker").get("password"),
                    cl_ord_id=dct_ord_0.get("cl_ord_id")
                )

                while True:
                    dct_ord_0 = self._get_order_w_status(lst_orders, "Canceled")
                    if dct_ord_0:
                        lst_orders.clear()
                        dct_vars["order_placed"] = False
                        logger.debug(f"{dct_thr.get('symbol')}-Em Leilão, sem stop limit, deu entrada, ordem "
                                     f"confirmada, mas saiu do preço teorico. Ordem cancelada!")
                        break

                    time.sleep(0.0001)

            # api.utils.network.profit_dll_sim.breakpoint_stopped = True
            # dct_quote["state"] = 0
            # breakpoint()

        # The auction reach the end without placing any orders (nothing to do).
        if not dct_quote.get("state") == 4 and not dct_vars.get("order_placed"):
            logger.debug(f"{dct_thr.get('symbol')}-Fim de leilão, sem ordem enviada.")
            return {str_symbol, False}

        # The auction reach the end but the order wasn't fullfiled (cancel it and return).
        dct_ord_0 = self._get_order_w_status(lst_orders, "New")

        # dct_ord_1 = dct_ord_0.copy()
        # dct_ord_1["cl_ord_id"] += 1
        # dct_ord_1["profit_id"] += 1
        # dct_ord_1["date"] = ""
        # dct_ord_1["status"] = "PartiallyFilled"
        # lst_orders.append(dct_ord_1)
        # dct_ord_0 = {}

        if dct_ord_0:
            logger.debug(f"{dct_thr.get('symbol')}-Fim de leilão, ordem enviada, sem execução. Cancelando ordem...")
            self._profit_dll.send_cancel_order(
                conta=dct_thr.get("broker").get("account"),
                broker=dct_thr.get("broker").get("id"),
                senha=dct_thr.get("broker").get("password"),
                cl_ord_id=dct_ord_0.get("cl_ord_id")
            )

            while True:
                dct_ord_0 = self._get_order_w_status(lst_orders, "Canceled")
                if dct_ord_0:
                    lst_orders.clear()
                    dct_vars["order_placed"] = False
                    logger.debug(f"{dct_thr.get('symbol')}-Fim de leilão, ordem enviada, sem execução. "
                                 f"Ordem cancelada.")
                    break

                time.sleep(0.0001)

            return {str_symbol, False}

        # The auction reach the end but the order weren't totally fullfiled.
        dct_ord_0 = self._get_order_w_status(lst_orders, "PartiallyFilled")
        if dct_ord_0:
            logger.debug(f"{dct_thr.get('symbol')}-Fim de leilão, ordem enviada, parcialmente executada.")
            self._profit_dll.send_cancel_order(
                conta=dct_thr.get("broker").get("account"),
                broker=dct_thr.get("broker").get("id"),
                senha=dct_thr.get("broker").get("password"),
                cl_ord_id=dct_ord_0.get("cl_ord_id")
            )
            logger.debug(f"{dct_thr.get('symbol')}-Fim de leilão, ordem enviada, parcialmente executada. "
                         f"Cancelando parte não executada...")

        traded_qtd = dct_ord_0.get("traded_qtd")
        traded_prc = dct_ord_0.get("price")
        traded_side = dct_ord_0.get("side")
        lst_sprd = self._dct_inst.get("spread_rt").get(str_symbol)
        lst_book = lst_sprd[0] if dct_ord_0.get("side") == 1 else lst_sprd[1]

        # lst_book[1] = traded_prc

        while True:

            if lst_book[1] == traded_prc and lst_book[0] <= traded_qtd * 3:

                logger.debug(f"{dct_thr.get('symbol')}-Fim de leilão, ordem enviada, zerando no fim da fila.")

                # Se a "ordem stop" for executada imediatamente, então tem que substituir por uma ordem limite para
                # a saída e uma ordem a mercado para stop na monitoração da fila do preço de stop.
                # (pendura a saída primeiro e depois monitora a fila)
                if traded_side == 1:
                    self._profit_dll.send_stop_buy_order(
                        conta=dct_thr.get("broker").get("account"),
                        broker=dct_thr.get("broker").get("id"),
                        senha=dct_thr.get("broker").get("password"),
                        ativo=str_symbol,
                        bolsa=dct_thr.get("stock_market"),
                        preco=lst_entry_signal[3],
                        s_stop_price=traded_prc,
                        qtd=traded_qtd
                    )
                else:
                    self._profit_dll.send_stop_sell_order(
                        conta=dct_thr.get("broker").get("account"),
                        broker=dct_thr.get("broker").get("id"),
                        senha=dct_thr.get("broker").get("password"),
                        ativo=str_symbol,
                        bolsa=dct_thr.get("stock_market"),
                        preco=lst_entry_signal[3],
                        s_stop_price=traded_prc,
                        qtd=traded_qtd
                    )

                break

            time.sleep(0.0001)

        return {str_symbol, True}
