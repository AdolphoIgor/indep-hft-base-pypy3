import time
from datetime import datetime, timedelta
from threading import Thread

from api.jobs.internal_config_provider import InternalConfigProviders
from api.logger import logger
from api.utils.network.profit_dll import ProfitDLL
from api.utils.network.profit_dll_recorder import REC_TIME_FMT, REC_PATH
from api.utils.network.profit_dll_win import TAssetID

breakpoint_stopped = False


class ProfitDLLSim(ProfitDLL):
    # Simulator capabilities
    _profit_id = 0
    _cl_ord_id = 0

    def __init__(self, config_prov: InternalConfigProviders, simulator=False):
        super().__init__(config_prov)
        self._simulator = simulator

    def play_log(self, f_date: str, loop_start=None, loop_ending=None, speed=0, no_wait=False):
        def play(file_date: str, loop_init, loop_end, loop_speed, loop_no_wait):
            try:
                if loop_init:
                    loop_init = datetime.strptime(f"{file_date} {loop_init}.0", REC_TIME_FMT)

                if loop_end:
                    loop_end = datetime.strptime(f"{file_date} {loop_end}.0", REC_TIME_FMT)

            except Exception:
                raise Exception("Error converting datetime format from replay.")

            file_path = f"{REC_PATH}/{datetime.strptime(file_date, '%Y-%m-%d').strftime('%Y%m%d')}.log"
            try:

                self._b_market_connected = True

                with open(file_path, mode='r', encoding="UTF-8", newline='\n') as file:

                    file_start_idx = 0
                    time_track_a = None
                    act_line = -1
                    lst_repl_sbl = ['DOLFUT', 'WDOFUT', 'INDFUT', 'WINFUT']
                    while True:

                        if breakpoint_stopped:
                            breakpoint()

                        fl_val = file.readline()
                        if not fl_val:
                            break

                        lst_val = fl_val.replace('\n', '').split("|")
                        act_line += 1
                        time_track_b = datetime.strptime(lst_val[0], REC_TIME_FMT)
                        # print(f"time: {lst_val[0]}, value: {lst_val[1]}|{lst_val[2][:10]}")

                        if loop_init and loop_init > time_track_b:
                            file_start_idx += 1
                            continue

                        if not time_track_a:
                            time_track_a = time_track_b

                        time_diff = time_track_b - time_track_a
                        if time_diff > timedelta(microseconds=0):
                            # time_diff -= timedelta(microseconds=500)
                            lg_sleep = eval(f"{time_diff.seconds}.{time_diff.microseconds}")
                            if not loop_no_wait:
                                if speed:
                                    lg_sleep = lg_sleep / loop_speed if loop_speed > 0 else lg_sleep * loop_speed

                                time.sleep(lg_sleep)

                        asset_id = TAssetID()
                        lst_val[2] = eval(lst_val[2].replace("nan", "-1"))

                        symbol = lst_val[2][0]
                        for sbl in lst_repl_sbl:
                            if symbol.find(sbl[:3]) >= 0:
                                symbol = sbl
                                break

                        asset_id.ticker = symbol
                        lst_val[2][0] = asset_id
                        exec(f"self.{lst_val[1]}(*lst_val[2])")

                        if loop_end and loop_end <= time_track_b:
                            file.seek(file_start_idx)

                        time_track_a = time_track_b

            except Exception as e:
                logger.debug(f"Exception raised in play_log(). File: {file_path}")
                logger.debug(f"Exception raised in play_log(). Line: {act_line}")
                logger.debug(f"Exception raised in play_log(). Time: {time_track_b}")
                logger.debug(f"Exception raised in play_log(). Error: {e}")

            finally:
                self._b_market_connected = False
                logger.info(f"The replay for {file_date} has been ended.")

        play_thr = Thread(target=play, name="play", args=(f_date, loop_start, loop_ending, speed, no_wait))
        play_thr.start()

    # METHODS ----------------------------------------------------------------------------------------------------------
    def subscribe_ticker(self, ticker: str, bolsa: str):
        return

    def unsubscribe_ticker(self, ticker: str, bolsa: str):
        return

    def subscribe_price_book(self, ticker: str, bolsa: str):
        return

    def unsubscribe_price_book(self, ticker: str, bolsa: str):
        return

    def subscribe_offer_book(self, ticker: str, bolsa: str):
        return

    def unsubscribe_offer_book(self, ticker: str, bolsa: str):
        return

    def get_agent_name_by_id(self, n_id: int):
        return

    def get_agent_short_name_by_id(self, n_id: int):
        return

    def send_buy_order(self, conta: str, broker: str, senha: str, ativo: str, bolsa: str, preco: float, qtd: int):
        if not self._simulator:
            super().send_buy_order(conta, broker, senha, ativo, bolsa, preco, qtd)
            return

        lst_book = self._dct_lp.get(ativo, None)
        if not lst_book:
            return

        ord_status = ""
        self._profit_id += 1
        self._cl_ord_id += 1

        # [price, qtd, count]
        lst_lp_b = lst_book[0][-1][0]
        lst_lp_s = lst_book[1][0][0]
        orig_qtt = qtd

        dct_qte = self._dct_quote.get(ativo)
        # auction in progress...
        if dct_qte.get("state") == 4:
            lst_lp_b = dct_qte.get("theoretical_price")
            lst_lp_s = lst_lp_b

        tipo_ordem = "Market"
        avg_prc = lst_lp_b
        if preco <= lst_lp_b:
            tipo_ordem = "Limit"
            ord_status = "New"

        elif preco == lst_lp_s and qtd > lst_lp_s:
            ord_status = "PartiallyFilled"

        elif preco >= lst_lp_s:
            ord_status = "Filled"

            for lvl in lst_book[1]:
                if qtd >= lvl[1]:
                    avg_prc += lvl[0] * lvl[1]
                    qtd -= lvl[1]

                else:
                    avg_prc += lvl[0] * qtd

            avg_prc /= orig_qtt

        lst_orders = self._dct_orders.get(ativo, [])
        if not lst_orders:
            self._dct_orders[ativo] = lst_orders

        dtc_ordr = {
            "corretora": "simulador", "qtd": qtd, "traded_qtd": qtd, "leaves_qtd": 0, "side": 1, "price": preco,
            "stop_price": 0, "avg_price": avg_prc, "profit_id": self._profit_id, "tipo_ordem": tipo_ordem,
            "conta": "simulador", "titular": "simulador", "cl_ord_id": self._cl_ord_id, "status": ord_status,
            "date": datetime.now(), "symbol": ativo
        }

        lst_orders.append(dtc_ordr)
        logger.debug(f"send_buy_order -> {dtc_ordr}")

    def send_sell_order(self, conta: str, broker: str, senha: str, ativo: str, bolsa: str, preco: float, qtd: int):
        if not self._simulator:
            super().send_sell_order(conta, broker, senha, ativo, bolsa, preco, qtd)
            return

        lst_book = self._dct_lp.get(ativo, None)
        if not lst_book:
            return

        ord_status = ""
        self._profit_id += 1
        self._cl_ord_id += 1

        # [price, qtd, count]
        lst_lp_b = lst_book[0][-1][0]
        lst_lp_s = lst_book[1][0][0]
        orig_qtt = qtd

        dct_qte = self._dct_quote.get(ativo)
        # auction in progress...
        if dct_qte.get("state") == 4:
            lst_lp_b = dct_qte.get("theoretical_price")
            lst_lp_s = lst_lp_b

        tipo_ordem = "Market"
        avg_prc = lst_lp_s
        if preco <= lst_lp_s:
            tipo_ordem = "Limit"
            ord_status = "New"

        elif preco == lst_lp_b and qtd > lst_lp_b:
            ord_status = "PartiallyFilled"

        elif preco >= lst_lp_b:
            ord_status = "Filled"

            for lvl in lst_book[1]:
                if qtd >= lvl[1]:
                    avg_prc += lvl[0] * lvl[1]
                    qtd -= lvl[1]

                else:
                    avg_prc += lvl[0] * qtd

            avg_prc /= orig_qtt

        lst_orders = self._dct_orders.get(ativo, [])
        if not lst_orders:
            self._dct_orders[ativo] = lst_orders

        dtc_ordr = {
            "corretora": "simulador", "qtd": qtd, "traded_qtd": qtd, "leaves_qtd": 0, "side": 2, "price": preco,
            "stop_price": 0, "avg_price": avg_prc, "profit_id": self._profit_id, "tipo_ordem": tipo_ordem,
            "conta": "simulador", "titular": "simulador", "cl_ord_id": self._cl_ord_id, "status": ord_status,
            "date": datetime.now(), "symbol": ativo
        }

        lst_orders.append(dtc_ordr)
        logger.debug(f"send_sell_order -> {dtc_ordr}")

    def send_stop_buy_order(self, conta: str, broker: str, senha: str, ativo: str, bolsa: str, preco: float,
                            s_stop_price: float, qtd: int):
        self.send_sell_order(conta, broker, senha, ativo, bolsa, preco, qtd)
        self.send_sell_order(conta, broker, senha, ativo, bolsa, s_stop_price, qtd)

    def send_stop_sell_order(self, conta: str, broker: str, senha: str, ativo: str, bolsa: str, preco: float,
                             s_stop_price: float, qtd: int):
        self.send_buy_order(conta, broker, senha, ativo, bolsa, preco, qtd)
        self.send_buy_order(conta, broker, senha, ativo, bolsa, s_stop_price, qtd)

    def send_change_order(self, conta: str, broker: str, senha: str, cl_ord_id: str, preco: float, qtd: int):
        return

    def send_cancel_order(self, conta: str, broker: str, cl_ord_id: str, senha: str):
        if not self._simulator:
            super().send_cancel_order(conta, broker, cl_ord_id, senha)
            return

        symbol = None
        dct_org_ordr = None
        for sbl, lst_ordrs in self._dct_orders.items():
            for ordr in lst_ordrs:
                if ordr.get("cl_ord_id") == cl_ord_id:
                    symbol = sbl
                    dct_org_ordr = ordr
                    self._dct_orders[symbol] = lst_ordrs

        if not symbol:
            return

        # auction in progress... prevent order to be canceled if its price is into theoretical price.
        dct_qte = self._dct_quote.get(symbol)
        if dct_qte.get("state") == 4:
            # Lado da ordem (Compra=1, Venda=2)
            th_prc = dct_qte.get("theoretical_price")
            eval1 = dct_org_ordr.get("side") == 1 and dct_org_ordr.get("price") >= th_prc
            eval2 = dct_org_ordr.get("side") == 2 and dct_org_ordr.get("price") <= th_prc
            if eval1 or eval2:
                return

        self._profit_id += 1
        self._cl_ord_id += 1

        dtc_ordr = dct_org_ordr.copy()
        dtc_ordr["status"] = "Canceled"
        dtc_ordr["date"] = datetime.now()
        dtc_ordr["profit_id"] = self._profit_id
        dtc_ordr["cl_ord_id"] = self._cl_ord_id

        self._dct_orders[symbol].append(dtc_ordr)
        logger.debug(f"send_cancel_order -> {dtc_ordr}")

    def send_cancel_orders(self, conta: str, broker: str, senha: str, ativo: str, bolsa: str):
        if not self._simulator:
            super().send_cancel_orders(conta, broker, senha, ativo, bolsa)
            return

        for ordr in self._dct_orders.get(ativo):
            symbol = ordr.get("symbol")

            # auction in progress... prevent order to be canceled if its price is into theoretical price.
            dct_qte = self._dct_quote.get(symbol)
            if dct_qte.get("state") == 4:
                # Lado da ordem (Compra=1, Venda=2)
                th_prc = dct_qte.get("theoretical_price")
                eval1 = dct_qte.get("side") == 1 and dct_qte.get("price") > th_prc
                eval2 = dct_qte.get("side") == 2 and dct_qte.get("price") < th_prc
                if eval1 or eval2:
                    break

            self._profit_id += 1
            dtc_ordr = ordr.copy()
            dtc_ordr["status"] = "Canceled"
            dtc_ordr["date"] = datetime.now()
            dtc_ordr["profit_id"] = self._profit_id
            dtc_ordr["cl_ord_id"] = self._cl_ord_id

            self._dct_orders[symbol].append(dtc_ordr)
            logger.debug(f"send_cancel_orders -> {dtc_ordr}")

    def send_cancel_all_orders(self, conta: str, broker: str, senha: str):
        if not self._simulator:
            super().send_cancel_all_orders(conta, broker, senha)
            return

        for sbl, lst_ordrs in self._dct_orders.items():
            for ordr in lst_ordrs:

                # auction in progress... prevent order to be canceled if its price is into theoretical price.
                dct_qte = self._dct_quote.get(sbl)
                if dct_qte.get("state") == 4:
                    # Lado da ordem (Compra=1, Venda=2)
                    th_prc = dct_qte.get("theoretical_price")
                    eval1 = dct_qte.get("side") == 1 and dct_qte.get("price") > th_prc
                    eval2 = dct_qte.get("side") == 2 and dct_qte.get("price") < th_prc
                    if eval1 or eval2:
                        break

                self._profit_id += 1
                dtc_ordr = ordr.copy()
                dtc_ordr["status"] = "Canceled"
                dtc_ordr["date"] = datetime.now()
                dtc_ordr["profit_id"] = self._profit_id
                dtc_ordr["cl_ord_id"] = self._cl_ord_id

                self._dct_orders[sbl].append(dtc_ordr)
                logger.debug(f"send_cancel_all_orders -> {dtc_ordr}")

    def send_zero_position(self, conta: str, broker: str, ativo: str, bolsa: str, senha: str, price: float):
        return

    def get_account(self):
        return

    def get_orders(self, conta: str, broker: str, dt_start: str, dt_end: str):
        return

    def get_order(self, cl_ord_id: str):
        return

    def get_order_profit_id(self, n_profit_id: int):
        return

    def get_position(self, conta: str, broker: str, ativo: str, bolsa: str):
        return

    def get_history_trades(self, ativo: str, bolsa: str, dt_start: str, dt_end: str):
        return

    def get_serie_history(self, ativo: str, bolsa: str, dt_start: str, dt_end: str, n_quote_number_start: int,
                          n_quote_number_end: int):
        return

    def set_day_trade(self, b_use_day_trade: bool):
        return

    def set_enabled_log_to_debug(self, b_enabled: bool):
        return

    def request_ticker_info(self, ticker: str, bolsa: str):
        return

    def get_all_ticker(self, bolsa: str):
        return

    def set_enabled_hist_order(self, b_enabled: bool):
        return

    def subscribe_adjust_history(self, ativo: str, bolsa: str):
        return

    def unsubscribe_adjust_history(self, ativo: str, bolsa: str):
        return

    def set_server_and_port(self, server, port: str):
        return

    def get_server_clock(self):
        return

    def get_last_daily_close(self, ticker: str, bolsa: str, bol_val_adj=1):
        return

    # CALLBACKS --------------------------------------------------------------------------------------------------------
    def price_book_callback(self, asset_id, action, position, side, qtd, count, price, array_sell, array_buy):
        lst_book = self._dct_lp.get(asset_id.ticker, None)
        if not lst_book:
            lst_book = [None, None]
            self._dct_lp[asset_id.ticker] = lst_book

        if action == 4:
            lst_book[0] = array_buy
            lst_book[1] = array_sell

            return

        lst_book_side = lst_book[side]
        if not lst_book_side:
            return

        if len(lst_book_side) == 0 or position > len(lst_book_side) or position < 0:
            return

        # action[atAdd = 0, atEdit = 1, atDelete = 2, atDeleteFrom = 3, atFullBook = 4]
        if action == 0:
            lst_book_side.insert(len(lst_book_side) - position, [price, qtd, count])

        elif action == 1:
            group = lst_book_side[-position - 1]
            group[1] = group[1] + qtd
            group[2] = group[2] + count

        elif action == 2:
            del lst_book_side[-position - 1]

        elif action == 3:
            del lst_book_side[-position - 1:]

        lst_spread_rt = self._dct_spread_rt.get(asset_id.ticker, None)
        if not lst_spread_rt:
            lst_spread_rt = [None, None]
            self._dct_spread_rt[asset_id.ticker] = lst_spread_rt

        if lst_book[side]:
            lst_spread_rt[side] = lst_book[side][::-1][0][:2][::-1]

    def offer_book_callback(self, asset_id, action, position, side, qtd, agent, offer_id, price, has_price, has_qtd,
                            has_date, has_offer_id, has_agent, date, array_sell, array_buy):
        def make_price_book(offer_book: list):
            def proc_side(offer_side_book: list, levels=10):
                lst_res = []
                last_prc, qtt, idx = 0, 0, 0
                lst_prv_off = []
                for lvl_prc in offer_side_book:
                    if len(lst_res) > levels:
                        break

                    act_price = lvl_prc[0]
                    if not last_prc:
                        last_prc = act_price

                    if not last_prc == act_price:
                        lst_res.append([last_prc, qtt, idx, lst_prv_off])
                        qtt, idx = 0, 0
                        last_prc = act_price
                        lst_prv_off = []

                    qtt += lvl_prc[1]
                    idx += 1
                    if len(lvl_prc) == 6:
                        lst_prv_off.append([idx, lvl_prc[3], lvl_prc[5]])

                return lst_res[::-1]

            if not offer_book:
                return []

            return [proc_side(offer_book[0][::-1]), proc_side(offer_book[1][::-1])]

        lst_book = self._dct_lo.get(asset_id.ticker, None)
        if not lst_book:
            lst_book = [None, None]
            self._dct_lo[asset_id.ticker] = lst_book

        if action == 4:
            lst_book[0] = array_buy
            lst_book[1] = array_sell

            return

        lst_book_side = lst_book[side]
        if not lst_book_side:
            return

        if len(lst_book_side) == 0 or position > len(lst_book_side) or position < 0:
            return

        lst_book_side = lst_book[side]

        # action[atAdd = 0, atEdit = 1, atDelete = 2, atDeleteFrom = 3, atFullBook = 4]
        if action == 0:
            lst_book_side.insert(len(lst_book_side) - position, [price, qtd, agent, offer_id, date, None])

        elif action == 1:
            group = lst_book_side[-position - 1]
            group[1] = group[1] + qtd
            group[2] = group[2] + agent

        elif action == 2:
            del lst_book_side[-position - 1]

        elif action == 3:
            del lst_book_side[-position - 1:]

        lp_tr = make_price_book(lst_book)
        self._dct_lp_tr[asset_id.ticker] = lp_tr

    def _execute_orders(self, ativo, date, price, qtd, trade_type):
        if not self._simulator:
            return

        if trade_type not in [2, 3, 4, 12, 13]:
            return

        lst_ordrs = self._dct_orders.get(ativo, [])
        for ordr in lst_ordrs:
            if ordr.get("status") in ["New", "PartiallyFilled"]:
                b_found = False
                for itm in lst_ordrs:
                    if ordr.get("profit_id") == itm.get("profit_id") and itm.get("status") == "Filled":
                        break

                if b_found:
                    continue

                # Lado da ordem (Compra=1, Venda=2)
                if ordr.get("side") == 1 and price > ordr.get("price") or \
                        ordr.get("side") == 2 and price < ordr.get("price"):
                    continue

                self._profit_id += 1
                self._cl_ord_id += 1
                dtc_ordr = ordr.copy()
                if qtd >= dtc_ordr.get("traded_qtd"):
                    dtc_ordr["status"] = "Filled"
                    dtc_ordr["profit_id"] = self._profit_id
                    dtc_ordr["cl_ord_id"] = self._cl_ord_id

                else:
                    dtc_ordr["status"] = "PartiallyFilled"

                dtc_ordr["date"] = date

                self._dct_orders[ativo].append(dtc_ordr)
                logger.debug(f"_execute_orders -> {dtc_ordr}")

    def new_trade_callback(self, asset_id, date, trade_number, price, vol, qtd, buy_agent, sell_agent, trade_type,
                           is_edit):
        super().new_trade_callback(asset_id, date, trade_number, price, vol, qtd, buy_agent, sell_agent, trade_type,
                                   is_edit)
        self._execute_orders(asset_id.ticker, date, price, qtd, trade_type)
        # logger.debug(f"new_trade_callback -> {asset_id.ticker}, {date}, {price}, {qtd}")

    def history_trade_callback(self, asset_id, date, trade_number, price, vol, qtd, buy_agent, sell_agent, trade_type):
        super().history_trade_callback(asset_id, date, trade_number, price, vol, qtd, buy_agent, sell_agent, trade_type)
        self._execute_orders(asset_id.ticker, date, price, qtd, trade_type)
        # logger.debug(f"history_trade_callback -> {asset_id.ticker}, {date}, {price}, {qtd}")
