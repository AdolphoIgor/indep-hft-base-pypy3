import time
from datetime import datetime, timedelta
from threading import Thread

from api.jobs.internal_config_provider import InternalConfigProviders
from api.utils.network.profit_dll import ProfitDLL
from api.utils.network.profit_dll_recorder import REC_TIME_FMT, REC_PATH
from api.utils.network.profit_dll_win import TAssetID


class ProfitDLLSim(ProfitDLL):
    # Simulator capabilities
    _profit_id = 0
    _cl_ord_id = 0

    def __init__(self, config_prov: InternalConfigProviders, simulator=False):
        super().__init__(config_prov)
        # self._replay = True
        self._simulator = simulator

    def play_log(self, f_date: str, loop_start=None, loop_ending=None):
        def play(file_date: str, loop_init=None, loop_end=None):
            try:
                if loop_init:
                    loop_init = datetime.strptime(f"{file_date} {loop_init}.0", REC_TIME_FMT)

                if loop_end:
                    loop_end = datetime.strptime(f"{file_date} {loop_end}.0", REC_TIME_FMT)

            except Exception:
                raise Exception("Error converting datetime format from replay.")

            try:
                self._b_market_connected = True

                file_path = f"{REC_PATH}/{datetime.strptime(file_date, '%Y-%m-%d').strftime('%Y%m%d')}.log"
                with open(file_path, mode='r', encoding="UTF-8", newline='\n') as file:

                    file_start_idx = 0
                    time_track_a = None
                    while True:

                        fl_val = file.readline()
                        if not fl_val:
                            break

                        lst_val = fl_val.replace('\n', '').split("|")
                        time_track_b = datetime.strptime(lst_val[0], REC_TIME_FMT)
                        print(f"time: {lst_val[0]}, value: {lst_val[1]}|{lst_val[2][:10]}")

                        if loop_init and loop_init > time_track_b:
                            file_start_idx += 1
                            continue

                        if not time_track_a:
                            time_track_a = time_track_b

                        time_diff = time_track_b - time_track_a
                        if time_diff > timedelta(microseconds=0):
                            # time_diff -= timedelta(microseconds=500)
                            lg_sleep = eval(f"{time_diff.seconds}.{time_diff.microseconds}")
                            time.sleep(lg_sleep)

                        asset_id = TAssetID()
                        lst_param = eval(lst_val[2])
                        asset_id.ticker = lst_param[0]
                        lst_param[0] = asset_id
                        exec(f"self.{lst_val[1]}(*lst_param)")

                        if loop_end and loop_end <= time_track_b:
                            file.seek(file_start_idx)

                        time_track_a = time_track_b

            except Exception as e:
                print(f"Exception raised in play_log(). Error: {e}")

            finally:
                self._b_market_connected = False

        play_thr = Thread(target=play, name="play", args=(f_date, loop_start, loop_ending,))
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
        if self._simulator:

            lst_book = self._dct_lp.get(ativo, None)
            if not lst_book:
                return

            ord_status = ""
            self._profit_id += 1
            self._cl_ord_id += 1

            # [price, qtd, count]
            lst_lp_b = lst_book[0]
            lst_lp_s = lst_book[1]
            orig_qtt = qtd

            tipo_ordem = "Market"
            avg_prc = lst_lp_b[0]
            if preco <= lst_lp_b[0]:
                tipo_ordem = "Limit"
                ord_status = "New"

            elif preco == lst_lp_s[0] and qtd > lst_lp_s[0]:
                ord_status = "PartiallyFilled"

            elif preco >= lst_lp_s[0]:
                ord_status = "Filled"

                for lvl in lst_lp_s:
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
                "corretora": "simulador", "qtd": qtd, "traded_qtd": qtd, "leaves_qtd": 0, "side": 0, "price": preco,
                "stop_price": 0, "avg_price": avg_prc, "profit_id": self._profit_id, "tipo_ordem": tipo_ordem,
                "conta": "simulador", "titular": "simulador", "cl_ord_id": self._cl_ord_id, "status": ord_status,
                "date": datetime.now(), "symbol": ativo
            }

            lst_orders.append(dtc_ordr)

    def send_sell_order(self, conta: str, broker: str, senha: str, ativo: str, bolsa: str, preco: float, qtd: int):
        if self._simulator:

            lst_book = self._dct_lp.get(ativo, None)
            if not lst_book:
                return

            ord_status = ""
            self._profit_id += 1
            self._cl_ord_id += 1

            # [price, qtd, count]
            lst_lp_b = lst_book[0]
            lst_lp_s = lst_book[1]
            orig_qtt = qtd

            tipo_ordem = "Market"
            avg_prc = lst_lp_b[0]
            if preco >= lst_lp_b[0]:
                tipo_ordem = "Limit"
                ord_status = "New"

            elif preco == lst_lp_s[0] and qtd > lst_lp_s[0]:
                ord_status = "PartiallyFilled"

            elif preco <= lst_lp_s[0]:
                ord_status = "Filled"

                for lvl in lst_lp_s:
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
                "corretora": "simulador", "qtd": qtd, "traded_qtd": qtd, "leaves_qtd": 0, "side": 0, "price": preco,
                "stop_price": 0, "avg_price": avg_prc, "profit_id": self._profit_id, "tipo_ordem": tipo_ordem,
                "conta": "simulador", "titular": "simulador", "cl_ord_id": self._cl_ord_id, "status": ord_status,
                "date": datetime.now(), "symbol": ativo
            }

            lst_orders.append(dtc_ordr)

    def send_stop_buy_order(self, conta: str, broker: str, senha: str, ativo: str, bolsa: str, preco: float,
                            s_stop_price: float, qtd: int):
        return

    def send_stop_sell_order(self, conta: str, broker: str, senha: str, ativo: str, bolsa: str, preco: float,
                             s_stop_price: float, qtd: int):
        return

    def send_change_order(self, conta: str, broker: str, senha: str, cl_ord_id: str, preco: float, qtd: int):
        return

    def send_cancel_order(self, conta: str, broker: str, cl_ord_id: str, senha: str):
        return

    def send_cancel_orders(self, conta: str, broker: str, senha: str, ativo: str, bolsa: str):
        return

    def send_cancel_all_orders(self, conta: str, broker: str, senha: str):
        return

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
