import os
import struct
import time
from ctypes import *
from datetime import datetime
from queue import Queue
from threading import Thread

from api.jobs.internal_config_provider import InternalConfigProviders

# recording capabilities
REC_PATH = "logs/profit_logs"
REC_FILE_PATH = f"{REC_PATH}/{datetime.now().strftime('%Y%m%d')}.log"
REC_TIME_FMT = '%Y-%m-%d %H:%M:%S.%f'

if os.name == "nt":
    from api.utils.network.profit_dll_win import ProfitDLLWin


    class ProfitDLLRecorder(ProfitDLLWin):

        _rec_queue_buffer = Queue()
        _rec_thr = None

        def __init__(self, config_prov: InternalConfigProviders, soft_key="", username="", password=""):
            super().__init__(config_prov, soft_key, username, password)
            self._record = True

        def record_log(self, instr_nm: str, instr: any):
            def record_data():
                os.makedirs(os.path.dirname(REC_FILE_PATH), exist_ok=True)
                with open(REC_FILE_PATH, mode='a', encoding="UTF-8", newline='\n') as file:
                    while True:
                        if not self._rec_queue_buffer.empty():
                            file.write(self._rec_queue_buffer.get())
                            file.flush()

                        time.sleep(0.0001)

            if self._record:
                str_rec = f"{datetime.now().strftime(REC_TIME_FMT)}|{instr_nm}|{instr}\n"
                self._rec_queue_buffer.put(str_rec)

                if not self._rec_thr:
                    self._rec_thr = Thread(target=record_data, name="recorder")
                    self._rec_thr.start()

        # CALLBACKS ----------------------------------------------------------------------------------------------------
        def change_cotation_callback(self, asset_id, date, trade_number, price):
            super().change_cotation_callback(asset_id, date, trade_number, price)
            self.record_log("change_cotation_callback", [asset_id.ticker, date, trade_number, price])

        def asset_list_callback(self, asset_id, name):
            super().asset_list_callback(asset_id, name)
            self.record_log("asset_list_callback", [asset_id.ticker, name])

        def asset_list_info_callback(self, asset_id, name, description, min_order_qtd, max_order_qtd, lote,
                                     security_type, security_sub_type, min_price_increment, contract_multiplier,
                                     valid_date, isin):
            super().asset_list_info_callback(asset_id, name, description, min_order_qtd, max_order_qtd, lote,
                                             security_type, security_sub_type, min_price_increment, contract_multiplier,
                                             valid_date, isin)
            self.record_log("asset_list_info_callback",
                            [asset_id.ticker, name, description, min_order_qtd, max_order_qtd,
                             lote, security_type, security_sub_type, min_price_increment,
                             contract_multiplier, valid_date, isin])

        def asset_list_info_callback_v2(self, asset_id, name, description, min_order_qtd, max_order_qtd, lote,
                                        security_type, security_sub_type, min_price_increment, contract_multiplier,
                                        valid_date, isin, setor, sub_setor, segmento):
            super().asset_list_info_callback_v2(asset_id, name, description, min_order_qtd, max_order_qtd, lote,
                                                security_type, security_sub_type, min_price_increment,
                                                contract_multiplier, valid_date, isin, setor, sub_setor, segmento)
            self.record_log("asset_list_info_callback_v2", [asset_id.ticker, name, description, min_order_qtd,
                                                            max_order_qtd, lote, security_type, security_sub_type,
                                                            min_price_increment, contract_multiplier, valid_date, isin,
                                                            setor, sub_setor, segmento])

        def adjust_history_callback(self, asset_id, value, adj_type, observ, dt_ajuste, dt_delib, dt_pagamento,
                                    aff_price):
            super().adjust_history_callback(asset_id, value, adj_type, observ, dt_ajuste, dt_delib, dt_pagamento,
                                            aff_price)
            self.record_log("adjust_history_callback", [asset_id.ticker, value, adj_type, observ, dt_ajuste, dt_delib,
                                                        dt_pagamento, aff_price])

        def adjust_history_callback_v2(self, asset_id, value, adj_type, observ, dt_ajuste, dt_delib, dt_pagamento,
                                       flags, mult):
            super().adjust_history_callback_v2(asset_id, value, adj_type, observ, dt_ajuste, dt_delib, dt_pagamento,
                                               flags, mult)
            self.record_log("adjust_history_callback_v2",
                            [asset_id.ticker, value, adj_type, observ, dt_ajuste, dt_delib,
                             dt_pagamento, flags, mult])

        def change_state_ticker_callback(self, asset_id, date, state):
            super().change_state_ticker_callback(asset_id, date, state)
            self.record_log("change_state_ticker_callback", [asset_id.ticker, date, state])

        def price_book_callback(self, asset_id, action, position, side, qtd, count, price, array_sell, array_buy):
            def decript(price_array):
                price_array_decripted = []

                arr = cast(price_array, POINTER(c_char))
                frame = bytearray()
                for i in range(price_array[1]):
                    c = arr[i]
                    frame.append(c[0])

                start = 8
                for i in range(price_array[0]):
                    i_price = struct.unpack("d", frame[start:start + 8])[0]
                    start += 8
                    i_qtd = struct.unpack("i", frame[start:start + 4])[0]
                    start += 4
                    i_count = struct.unpack("i", frame[start:start + 4])[0]
                    start += 4

                    price_array_decripted.append([i_price, i_qtd, i_count])

                return price_array_decripted

            lst_book = self._dct_lp.get(asset_id.ticker, None)
            if not lst_book:
                lst_book = [None, None]
                self._dct_lp[asset_id.ticker] = lst_book

            if action == 4:
                if bool(array_buy):
                    lst_book[0] = decript(array_buy)

                if bool(array_sell):
                    lst_book[1] = decript(array_sell)

                self.record_log("price_book_callback", [asset_id.ticker, action, position, side, qtd, count, price,
                                                        lst_book[1], lst_book[0]])
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

            self.record_log("price_book_callback",
                            [asset_id.ticker, action, position, side, qtd, count, price, None, None])

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

            def decript(price_array):
                price_array_decripted = []

                arr = cast(price_array, POINTER(c_char))
                frame = bytearray()
                for i in range(price_array[1]):
                    c = arr[i]
                    frame.append(c[0])

                start = 8
                for i in range(price_array[0]):
                    i_price = struct.unpack("d", frame[start:start + 8])[0]
                    start += 8
                    i_qtd = struct.unpack("i", frame[start:start + 4])[0]
                    start += 4
                    i_agent = struct.unpack("i", frame[start:start + 4])[0]
                    start += 4
                    i_offer_id = struct.unpack("q", frame[start:start + 8])[0]
                    start += 8
                    date_length = struct.unpack("h", frame[start:start + 2])[0]
                    start += 2
                    i_date = frame[start:start + date_length]
                    start += date_length

                    price_array_decripted.append([i_price, i_qtd, i_agent, i_offer_id, i_date])

                return price_array_decripted

            lst_book = self._dct_lo.get(asset_id.ticker, None)
            if not lst_book:
                lst_book = [None, None]
                self._dct_lo[asset_id.ticker] = lst_book

            if action == 4:
                if bool(array_buy):
                    lst_book[0] = decript(array_buy)

                if bool(array_sell):
                    lst_book[1] = decript(array_sell)

                self.record_log("offer_book_callback", [asset_id.ticker, action, position, side, qtd, agent, offer_id,
                                                        price, has_price, has_qtd, has_date, has_offer_id, has_agent,
                                                        date, lst_book[1], lst_book[0]])

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

            self.record_log("offer_book_callback",
                            [asset_id.ticker, action, position, side, qtd, agent, offer_id, price,
                             has_price, has_qtd, has_date, has_offer_id, has_agent,
                             date, None, None])

        def set_theoretical_price_callback(self, asset_id, theoretical_price, theoretical_qtd):
            super().set_theoretical_price_callback(asset_id, theoretical_price, theoretical_qtd)
            self.record_log("set_theoretical_price_callback", [asset_id.ticker, theoretical_price, theoretical_qtd])

        def history_trade_callback(self, asset_id, date, trade_number, price, vol, qtd, buy_agent, sell_agent,
                                   trade_type):
            super().history_trade_callback(asset_id, date, trade_number, price, vol, qtd, buy_agent, sell_agent,
                                           trade_type)
            self.record_log("history_trade_callback",
                            [asset_id.ticker, date, trade_number, price, vol, qtd, buy_agent, sell_agent, trade_type])

        def new_trade_callback(self, asset_id, date, trade_number, price, vol, qtd, buy_agent, sell_agent, trade_type,
                               is_edit):
            super().new_trade_callback(asset_id, date, trade_number, price, vol, qtd, buy_agent, sell_agent, trade_type,
                                       is_edit)
            self.record_log("new_trade_callback", [asset_id.ticker, date, trade_number, price, vol, qtd, buy_agent,
                                                   sell_agent, trade_type, is_edit])

        def tiny_book_callback(self, asset_id, price, qtd, side):
            super().tiny_book_callback(asset_id, price, qtd, side)
            self.record_log("tiny_book_callback", [asset_id.ticker, price, qtd, side])

        def new_daily_callback(self, asset_id, date, open_val, high, low, close, vol, ajuste, max_limit, min_limit,
                               vol_buyer, vol_seller, qtd, negocios, contratos_open, qtd_buyer, qtd_seller, neg_buyer,
                               neg_seller):
            super().new_daily_callback(asset_id, date, open_val, high, low, close, vol, ajuste, max_limit, min_limit,
                                       vol_buyer, vol_seller, qtd, negocios, contratos_open, qtd_buyer, qtd_seller,
                                       neg_buyer, neg_seller)
            self.record_log("new_daily_callback", [asset_id.ticker, date, open_val, high, low, close, vol, ajuste,
                                                   max_limit, min_limit, vol_buyer, vol_seller, qtd, negocios,
                                                   contratos_open, qtd_buyer, qtd_seller, neg_buyer, neg_seller])
