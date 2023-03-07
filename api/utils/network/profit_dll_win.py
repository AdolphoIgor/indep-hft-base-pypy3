import os
import struct
from ctypes import *

from api.jobs.internal_config_provider import InternalConfigProviders
from api.logger import logger
from api.utils.network.profit_dll import ProfitDLL


# @dataclass
class TAssetID(Structure):
    _fields_ = [("ticker", c_wchar_p),
                ("bolsa", c_wchar_p),
                ("feed", c_int)]


if os.name == "nt":

    class ProfitDLLWin(ProfitDLL):

        # CONSTANT Error Codes
        _NL_ERR_INIT = 80
        _NL_OK = 0
        _NL_ERR_INVALID_ARGS = 90
        _NL_ERR_INTERNAL_ERROR = 100

        # Pathway to Profit DLL. Keep in mind that Python interpreter must be 32bits version.
        _profit_dll = WinDLL("ProfitDLL.dll")
        _profit_dll.argtypes = None

        def __init__(self, config_prov: InternalConfigProviders, soft_key="", username="", password="",
                     b_roteamento=True):

            super().__init__(config_prov)

            # initialization
            self._profit_dll.DLLInitializeLogin.restype = c_short
            self._profit_dll.DLLInitializeMarketLogin.restype = c_short
            self._profit_dll.DLLFinalize.restype = c_short

            # calls
            self._profit_dll.SubscribeTicker.restype = c_short
            self._profit_dll.UnsubscribeTicker.restype = c_short
            self._profit_dll.SubscribePriceBook.restype = c_short
            self._profit_dll.UnsubscribePriceBook.restype = c_short
            self._profit_dll.SubscribeOfferBook.restype = c_short
            self._profit_dll.UnsubscribeOfferBook.restype = c_short
            self._profit_dll.GetAgentNameByID.restype = c_wchar_p
            self._profit_dll.GetAgentShortNameByID.restype = c_wchar_p
            self._profit_dll.SendBuyOrder.restype = c_longlong
            self._profit_dll.SendSellOrder.restype = c_longlong
            self._profit_dll.SendStopBuyOrder.restype = c_longlong
            self._profit_dll.SendStopSellOrder.restype = c_longlong
            self._profit_dll.SendChangeOrder.restype = c_short
            self._profit_dll.SendCancelOrder.restype = c_short
            self._profit_dll.SendCancelOrders.restype = c_short
            self._profit_dll.SendCancelAllOrders.restype = c_short
            self._profit_dll.SendZeroPosition.restype = c_longlong
            self._profit_dll.GetAccount.restype = c_short
            self._profit_dll.GetOrders.restype = c_short
            self._profit_dll.GetOrder.restype = c_short
            self._profit_dll.GetOrderProfitID.restype = c_short
            self._profit_dll.GetPosition.restype = POINTER(c_int)
            self._profit_dll.GetHistoryTrades.restype = c_short
            self._profit_dll.GetSerieHistory.restype = c_short
            self._profit_dll.SubscribeAdjustHistory.restype = c_short
            self._profit_dll.UnsubscribeAdjustHistory.restype = c_short
            self._profit_dll.SetAdjustHistoryCallback.restype = c_short
            self._profit_dll.SetAdjustHistoryCallbackV2.restype = c_short
            self._profit_dll.SetTheoreticalPriceCallback.restype = c_short
            self._profit_dll.SetServerAndPort.restype = c_short
            self._profit_dll.GetServerClock.restype = c_short
            self._profit_dll.GetLastDailyClose.restype = c_short

            # callbacks
            self._profit_dll.SetDayTrade.restype = c_short
            self._profit_dll.SetChangeCotationCallback.restype = c_short
            self._profit_dll.SetAssetListCallback.restype = c_short
            self._profit_dll.SetAssetListInfoCallback.restype = c_short
            self._profit_dll.SetAssetListInfoCallbackV2.restype = c_short
            self._profit_dll.SetEnabledLogToDebug.restype = c_short
            self._profit_dll.RequestTickerInfo.restype = c_short
            self._profit_dll.GetAllTicker.restype = c_short
            self._profit_dll.SetChangeStateTickerCallback.restype = c_short
            self._profit_dll.SetEnabledHistOrder.restype = c_short

            self._soft_key = soft_key
            self._username = username
            self._password = password
            self._b_roteamento = b_roteamento

        def connect(self):
            try:
                if self._b_roteamento:
                    # market data e roteamento
                    self._profit_dll.DLLInitializeLogin(
                        c_wchar_p(self._soft_key), c_wchar_p(self._username), c_wchar_p(self._password), state_callback,
                        history_callback, order_change_callback, account_callback,
                        new_trade_callback, new_daily_callback, price_book_callback,
                        offer_book_callback, history_trade_callback, progress_callback,
                        tiny_book_callback)
                else:
                    # market data only
                    self._profit_dll.DLLInitializeMarketLogin(
                        c_wchar_p(self._soft_key), c_wchar_p(self._username), c_wchar_p(self._password), state_callback,
                        new_trade_callback, new_daily_callback, price_book_callback,
                        offer_book_callback, history_trade_callback, progress_callback,
                        tiny_book_callback)

                while True:
                    if self.is_connected:
                        self._profit_dll.SetChangeCotationCallback(change_cotation_callback)
                        self._profit_dll.SetAssetListCallback(asset_list_callback)
                        self._profit_dll.SetAssetListInfoCallback(asset_list_info_callback)
                        self._profit_dll.SetAssetListInfoCallbackV2(asset_list_info_callback_v2)
                        self._profit_dll.SetAdjustHistoryCallback(adjust_history_callback)
                        self._profit_dll.SetAdjustHistoryCallbackV2(adjust_history_callback_v2)
                        self._profit_dll.SetChangeStateTickerCallback(change_state_ticker_callback)
                        self._profit_dll.SetTheoreticalPriceCallback(set_theoretical_price_callback)

                        break

            except Exception as e:
                logger.error(str(e))

        def disconnect(self):
            if self.is_connected():
                super().disconnect()
                self._profit_dll.DLLFinalize()

        # METHODS ------------------------------------------------------------------------------------------------------
        def subscribe_ticker(self, ticker: str, bolsa: str):
            return self._profit_dll.SubscribeTicker(c_wchar_p(ticker), c_wchar_p(bolsa))

        def unsubscribe_ticker(self, ticker: str, bolsa: str):
            return self._profit_dll.UnsubscribeTicker(c_wchar_p(ticker), c_wchar_p(bolsa))

        def subscribe_price_book(self, ticker: str, bolsa: str):
            return self._profit_dll.SubscribePriceBook(c_wchar_p(ticker), c_wchar_p(bolsa))

        def unsubscribe_price_book(self, ticker: str, bolsa: str):
            return self._profit_dll.UnsubscribePriceBook(c_wchar_p(ticker), c_wchar_p(bolsa))

        def subscribe_offer_book(self, ticker: str, bolsa: str):
            return self._profit_dll.SubscribeOfferBook(c_wchar_p(ticker), c_wchar_p(bolsa))

        def unsubscribe_offer_book(self, ticker: str, bolsa: str):
            return self._profit_dll.UnsubscribeOfferBook(c_wchar_p(ticker), c_wchar_p(bolsa))

        def get_agent_name_by_id(self, n_id: int):
            return self._profit_dll.GetAgentNameByID(c_int(n_id))

        def get_agent_short_name_by_id(self, n_id: int):
            return self._profit_dll.GetAgentShortNameByID(c_int(n_id))

        def send_buy_order(self, conta: str, broker: str, senha: str, ativo: str, bolsa: str, preco: float, qtd: int):
            return self._profit_dll.SendBuyOrder(c_wchar_p(conta), c_wchar_p(broker), c_wchar_p(senha),
                                                 c_wchar_p(ativo),
                                                 c_wchar_p(bolsa), c_double(preco), c_int(qtd))

        def send_sell_order(self, conta: str, broker: str, senha: str, ativo: str, bolsa: str, preco: float, qtd: int):
            return self._profit_dll.SendSellOrder(c_wchar_p(conta), c_wchar_p(broker), c_wchar_p(senha),
                                                  c_wchar_p(ativo),
                                                  c_wchar_p(bolsa), c_double(preco), c_int(qtd))

        def send_stop_buy_order(self, conta: str, broker: str, senha: str, ativo: str, bolsa: str, preco: float,
                                s_stop_price: float, qtd: int):
            return self._profit_dll.SendStopBuyOrder(c_wchar_p(conta), c_wchar_p(broker), c_wchar_p(senha),
                                                     c_wchar_p(ativo), c_wchar_p(bolsa), c_double(preco),
                                                     c_double(s_stop_price), c_int(qtd))

        def send_stop_sell_order(self, conta: str, broker: str, senha: str, ativo: str, bolsa: str, preco: float,
                                 s_stop_price: float, qtd: int):
            return self._profit_dll.SendStopSellOrder(c_wchar_p(conta), c_wchar_p(broker), c_wchar_p(senha),
                                                      c_wchar_p(ativo), c_wchar_p(bolsa), c_double(preco),
                                                      c_double(s_stop_price), c_int(qtd))

        def send_change_order(self, conta: str, broker: str, senha: str, cl_ord_id: str, preco: float, qtd: int):
            return self._profit_dll.SendChangeOrder(c_wchar_p(conta), c_wchar_p(broker), c_wchar_p(senha),
                                                    c_wchar_p(cl_ord_id), c_double(preco), c_int(qtd))

        def send_cancel_order(self, conta: str, broker: str, cl_ord_id: str, senha: str):
            return self._profit_dll.SendCancelOrder(c_wchar_p(conta), c_wchar_p(broker), c_wchar_p(cl_ord_id),
                                                    c_wchar_p(senha))

        def send_cancel_orders(self, conta: str, broker: str, senha: str, ativo: str, bolsa: str):
            return self._profit_dll.SendCancelOrders(c_wchar_p(conta), c_wchar_p(broker), c_wchar_p(senha),
                                                     c_wchar_p(ativo), c_wchar_p(bolsa))

        def send_cancel_all_orders(self, conta: str, broker: str, senha: str):
            return self._profit_dll.SendCancelAllOrders(c_wchar_p(conta), c_wchar_p(broker), c_wchar_p(senha))

        def send_zero_position(self, conta: str, broker: str, ativo: str, bolsa: str, senha: str, price: float):
            return self._profit_dll.SendZeroPosition(c_wchar_p(conta), c_wchar_p(broker), c_wchar_p(ativo),
                                                     c_wchar_p(senha), c_wchar_p(bolsa), c_double(price))

        def get_account(self):
            return self._profit_dll.GetAccount()

        def get_orders(self, conta: str, broker: str, dt_start: str, dt_end: str):
            return self._profit_dll.GetOrders(c_wchar_p(conta), c_wchar_p(broker), c_wchar_p(dt_start),
                                              c_wchar_p(dt_end))

        def get_order(self, cl_ord_id: str):
            return self._profit_dll.GetOrder(c_wchar_p(cl_ord_id))

        def get_order_profit_id(self, n_profit_id: int):
            return self._profit_dll.GetOrderProfitID(c_longlong(n_profit_id))

        def get_position(self, conta: str, broker: str, ativo: str, bolsa: str):
            result = self._profit_dll.GetPosition(c_wchar_p(conta), c_wchar_p(broker), c_wchar_p(ativo),
                                                  c_wchar_p(bolsa))

            ret = {}
            n_qtd = result[0]
            if n_qtd == 0:
                logger.info("Nao ha posicao para esse ativo")
                return ret

            n_tam = result[1]
            # logger.debug(f"qtd: {n_qtd}, n_tam: {n_tam}")

            arr = cast(result, POINTER(c_char))
            frame = bytearray()
            for i in range(n_tam):
                c = arr[i]
                frame.append(c[0])

            start = 8
            for i in range(n_qtd):
                ret['corretora_id'] = struct.unpack("i", frame[start:start + 4])[0]
                start += 4

                acc_id_length = struct.unpack("h", frame[start:start + 2])[0]
                start += 2
                ret['account_id'] = frame[start:start + acc_id_length]
                start += acc_id_length

                titular_length = struct.unpack("h", frame[start:start + 2])[0]
                start += 2
                ret['titular'] = frame[start:start + titular_length]
                start += titular_length

                ticker_length = struct.unpack("h", frame[start:start + 2])[0]
                start += 2
                ret['ticker'] = frame[start:start + ticker_length]
                start += ticker_length

                ret['intraday_pos'] = struct.unpack("i", frame[start:start + 4])[0]
                start += 4

                ret['price'] = struct.unpack("d", frame[start:start + 8])[0]
                start += 8

                ret['avg_sell_price'] = struct.unpack("d", frame[start:start + 8])[0]
                start += 8

                ret['sell_qtd'] = struct.unpack("i", frame[start:start + 4])[0]
                start += 4

                ret['avg_buy_price'] = struct.unpack("d", frame[start:start + 8])[0]
                start += 8

                ret['buy_qtd'] = struct.unpack("i", frame[start:start + 4])[0]
                start += 4

                ret['custody_d1'] = struct.unpack("i", frame[start:start + 4])[0]
                start += 4

                ret['custody_d2'] = struct.unpack("i", frame[start:start + 4])[0]
                start += 4

                ret['custody_d3'] = struct.unpack("i", frame[start:start + 4])[0]
                start += 4

                ret['blocked'] = struct.unpack("i", frame[start:start + 4])[0]
                start += 4

                ret['pending'] = struct.unpack("i", frame[start:start + 4])[0]
                start += 4

                ret['allocated'] = struct.unpack("i", frame[start:start + 4])[0]
                start += 4

                ret['provisioned'] = struct.unpack("i", frame[start:start + 4])[0]
                start += 4

                ret['qtd_position'] = struct.unpack("i", frame[start:start + 4])[0]
                start += 4

                ret['available'] = struct.unpack("i", frame[start:start + 4])[0]
                start += 4

                # logger.debug(ret)

            return ret

        def get_history_trades(self, ativo: str, bolsa: str, dt_start: str, dt_end: str):
            return self._profit_dll.GetHistoryTrades(c_wchar_p(ativo), c_wchar_p(bolsa), c_wchar_p(dt_start),
                                                     c_wchar_p(dt_end))

        def get_serie_history(self, ativo: str, bolsa: str, dt_start: str, dt_end: str, n_quote_number_start: int,
                              n_quote_number_end: int):
            return self._profit_dll.GetSerieHistory(c_wchar_p(ativo), c_wchar_p(bolsa), c_wchar_p(dt_start),
                                                    c_wchar_p(dt_end), c_uint(n_quote_number_start),
                                                    c_uint(n_quote_number_end))

        def set_day_trade(self, b_use_day_trade: bool):
            b_use_day_trade = c_int(1 if b_use_day_trade else 0)
            return self._profit_dll.SetDayTrade(b_use_day_trade), b_use_day_trade

        def set_enabled_log_to_debug(self, b_enabled: bool):
            b_enabled = c_int(1 if b_enabled else 0)
            return self._profit_dll.SetEnabledLogToDebug(b_enabled), b_enabled

        def request_ticker_info(self, ticker: str, bolsa: str):
            return self._profit_dll.RequestTickerInfo(c_wchar_p(ticker), c_wchar_p(bolsa))

        def get_all_ticker(self, bolsa: str):
            return self._profit_dll.GetAllTicker(c_wchar_p(bolsa))

        def set_enabled_hist_order(self, b_enabled: bool):
            b_enabled = c_int(1 if b_enabled else 0)
            return self._profit_dll.SetEnabledHistOrder(b_enabled), b_enabled

        def subscribe_adjust_history(self, ativo: str, bolsa: str):
            return self._profit_dll.SubscribeAdjustHistory(c_wchar_p(ativo), c_wchar_p(bolsa))

        def unsubscribe_adjust_history(self, ativo: str, bolsa: str):
            return self._profit_dll.UnsubscribeAdjustHistory(c_wchar_p(ativo), c_wchar_p(bolsa))

        def set_server_and_port(self, server, port: str):
            return self._profit_dll.SetServerAndPort(c_wchar_p(server), c_wchar_p(port))

        def get_server_clock(self):
            dt_prm = byref(c_double(-1.0))
            year_prm, mth_prm, day_prm = byref(c_int(0)), byref(c_int(0)), byref(c_int(0))
            hr_prm, min_prm, sec_prm, mil_prm = byref(c_int(0)), byref(c_int(0)), byref(c_int(0)), byref(c_int(0))

            ret_dct = {}
            ret = self._profit_dll.GetServerClock(dt_prm, year_prm, mth_prm, day_prm, hr_prm, min_prm, sec_prm, mil_prm)
            if ret != self._NL_OK:
                return ret, ret_dct

            ret_dct['year'] = year_prm.contents.value
            ret_dct['month'] = mth_prm.contents.value
            ret_dct['day'] = day_prm.contents.value
            ret_dct['hour'] = hr_prm.contents.value
            ret_dct['min'] = min_prm.contents.value
            ret_dct['sec'] = sec_prm.contents.value
            ret_dct['mil'] = mil_prm.contents.value
            ret_dct['bra_format'] = f"{ret_dct['year']}/{ret_dct['month']}/{ret_dct['day']} " \
                                    f"{ret_dct['hour']}:{ret_dct['min']}:{ret_dct['sec']}.{ret_dct['mil']}"
            ret_dct[
                'date'] = f"{ret_dct['year']}-{ret_dct['month']}-{ret_dct['day']} {ret_dct['hour']}:{ret_dct['min']}:" \
                          f"{ret_dct['sec']}.{ret_dct['mil']}"
            return ret, ret_dct

        def get_last_daily_close(self, ticker: str, bolsa: str, bol_val_adj=1):
            val_close = c_double(-1.0)
            ret = self._profit_dll.GetLastDailyClose(c_wchar_p(ticker), c_wchar_p(bolsa), byref(val_close),
                                                     c_int(bol_val_adj))
            return ret, val_close

        # CALLBACKS ----------------------------------------------------------------------------------------------------
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

            # print(f"price_book_callback-{asset_id.ticker}, {action}, {position}, {side}, {qtd}, {count}, {price}")

            lst_book = self._dct_lp.get(asset_id.ticker, None)
            if not lst_book:
                lst_book = [None, None]
                self._dct_lp[asset_id.ticker] = lst_book

            if action == 4:
                if bool(array_buy):
                    lst_book[0] = decript(array_buy)

                if bool(array_sell):
                    lst_book[1] = decript(array_sell)

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

            '''
            logger.debug(f"offer_book_callback-{asset_id.ticker}, {action}, {position}, {side}, {qtd}, {agent}, "
                         f"{offer_id}, {price}, {has_price}, {has_qtd}, {has_date}, {has_offer_id}, {has_agent}, "
                         f"{date}, {array_sell}, {array_buy}")
            '''

            lst_book = self._dct_lo.get(asset_id.ticker, None)

            if not lst_book:
                lst_book = [None, None]
                self._dct_lo[asset_id.ticker] = lst_book

            if action == 4:
                if bool(array_buy):
                    lst_book[0] = decript(array_buy)

                if bool(array_sell):
                    lst_book[1] = decript(array_sell)

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

            self._dct_lp_tr[asset_id.ticker] = make_price_book(lst_book)


    # WHEN THE PROFITDLL WILL BE INITIATED, PLEASE SET THAT REFERENCE HERE.
    # THAT WOULD ALLOW TO THE CALLBACKS TO FORWARD THOSE CALLS TO THE PYTHON DLL.
    prov_conn: ProfitDLL


    # CALLBACKS --------------------------------------------------------------------------------------------------------
    @WINFUNCTYPE(None, TAssetID, c_wchar_p, c_uint, c_double)
    def change_cotation_callback(asset_id, date, trade_number, price):
        if prov_conn:
            prov_conn.change_cotation_callback(asset_id, date, trade_number, price)


    @WINFUNCTYPE(None, TAssetID, c_wchar_p)
    def asset_list_callback(asset_id, name):
        if prov_conn:
            prov_conn.asset_list_callback(asset_id, name)


    @WINFUNCTYPE(None, TAssetID, c_wchar_p, c_wchar_p, c_int, c_int, c_int, c_int, c_int, c_double, c_double, c_wchar_p,
                 c_wchar_p)
    def asset_list_info_callback(asset_id, name, description, min_order_qtd, max_order_qtd, lote, security_type,
                                 security_sub_type, min_price_increment, contract_multiplier, valid_date, isin):
        if prov_conn:
            prov_conn.asset_list_info_callback(asset_id, name, description, min_order_qtd, max_order_qtd, lote,
                                               security_type, security_sub_type, min_price_increment,
                                               contract_multiplier,
                                               valid_date, isin)


    @WINFUNCTYPE(None, TAssetID, c_wchar_p, c_wchar_p, c_int, c_int, c_int, c_int, c_int, c_double, c_double,
                 c_wchar_p, c_wchar_p, c_wchar_p, c_wchar_p, c_wchar_p)
    def asset_list_info_callback_v2(asset_id, name, description, min_order_qtd, max_order_qtd, lote,
                                    security_type, security_sub_type, min_price_increment, contract_multiplier,
                                    valid_date, isin, setor, sub_setor, segmento):
        if prov_conn:
            prov_conn.asset_list_info_callback_v2(asset_id, name, description, min_order_qtd, max_order_qtd, lote,
                                                  security_type, security_sub_type, min_price_increment,
                                                  contract_multiplier,
                                                  valid_date, isin, setor, sub_setor, segmento)


    @WINFUNCTYPE(None, TAssetID, c_double, c_wchar_p, c_wchar_p, c_wchar_p, c_wchar_p, c_wchar_p, c_int)
    def adjust_history_callback(asset_id, value, adj_type, observ, dt_ajuste, dt_delib, dt_pagamento, aff_price):
        if prov_conn:
            prov_conn.adjust_history_callback(asset_id, value, adj_type, observ, dt_ajuste, dt_delib, dt_pagamento,
                                              aff_price)


    @WINFUNCTYPE(None, TAssetID, c_double, c_wchar_p, c_wchar_p, c_wchar_p, c_wchar_p, c_wchar_p, c_uint, c_double)
    def adjust_history_callback_v2(asset_id, value, adj_type, observ, dt_ajuste, dt_delib, dt_pagamento, flags,
                                   mult):
        if prov_conn:
            prov_conn.adjust_history_callback_v2(asset_id, value, adj_type, observ, dt_ajuste, dt_delib, dt_pagamento,
                                                 flags, mult)


    @WINFUNCTYPE(None, TAssetID, c_wchar_p, c_int)
    def change_state_ticker_callback(asset_id, date, state):
        if prov_conn:
            prov_conn.change_state_ticker_callback(asset_id, date, state)


    @WINFUNCTYPE(None, TAssetID, c_int, c_int, c_int, c_int, c_int, c_double, POINTER(c_int), POINTER(c_int))
    def price_book_callback(asset_id, action, position, side, qtd, count, price, array_sell, array_buy):
        if prov_conn:
            prov_conn.price_book_callback(asset_id, action, position, side, qtd, count, price, array_sell, array_buy)


    @WINFUNCTYPE(None, TAssetID, c_int, c_int, c_int, c_int, c_int, c_longlong, c_double, c_char, c_char, c_char,
                 c_char, c_char, c_wchar_p, POINTER(c_int), POINTER(c_int))
    def offer_book_callback(asset_id, action, position, side, qtd, agent, offer_id, price, has_price, has_qtd,
                            has_date, has_offer_id, has_agent, date, array_sell, array_buy):
        if prov_conn:
            prov_conn.offer_book_callback(asset_id, action, position, side, qtd, agent, offer_id, price, has_price,
                                          has_qtd,
                                          has_date, has_offer_id, has_agent, date, array_sell, array_buy)


    @WINFUNCTYPE(None, TAssetID, c_double, c_longlong)
    def set_theoretical_price_callback(asset_id, theoretical_price, theoretical_qtd):
        if prov_conn:
            prov_conn.set_theoretical_price_callback(asset_id, theoretical_price, theoretical_qtd)


    @WINFUNCTYPE(None, c_int32, c_int32)
    def state_callback(type_val, result):
        if prov_conn:
            prov_conn.state_callback(type_val, result)


    @WINFUNCTYPE(None, TAssetID, c_int, c_int, c_int, c_int, c_int, c_double, c_double, c_double, c_longlong, c_wchar_p,
                 c_wchar_p, c_wchar_p, c_wchar_p, c_wchar_p, c_wchar_p)
    def history_callback(asset_id, corretora, qtd, traded_qtd, leaves_qtd, side, price, stop_price, avg_price,
                         profit_id, tipo_ordem, conta, titular, cl_ord_id, status, date):
        if prov_conn:
            prov_conn.history_callback(asset_id, corretora, qtd, traded_qtd, leaves_qtd, side, price, stop_price,
                                       avg_price,
                                       profit_id, tipo_ordem, conta, titular, cl_ord_id, status, date)


    @WINFUNCTYPE(None, TAssetID, c_int)
    def progress_callback(asset_id, progress):
        if prov_conn:
            prov_conn.progress_callback(asset_id, progress)


    @WINFUNCTYPE(None, TAssetID, c_wchar_p, c_uint, c_double, c_double, c_int, c_int, c_int, c_int)
    def history_trade_callback(asset_id, date, trade_number, price, vol, qtd, buy_agent, sell_agent, trade_type):
        if prov_conn:
            prov_conn.history_trade_callback(asset_id, date, trade_number, price, vol, qtd, buy_agent, sell_agent,
                                             trade_type)


    @WINFUNCTYPE(None, TAssetID, c_int, c_int, c_int, c_int, c_int, c_double, c_double, c_double, c_longlong,
                 c_wchar_p, c_wchar_p, c_wchar_p, c_wchar_p, c_wchar_p, c_wchar_p, c_wchar_p)
    def order_change_callback(asset_id, corretora, qtd, traded_qtd, leaves_qtd, side, price, stop_price,
                              avg_price, profit_id, tipo_ordem, conta, titular, cl_ord_id, status, date, text_message):
        if prov_conn:
            prov_conn.order_change_callback(asset_id, corretora, qtd, traded_qtd, leaves_qtd, side, price, stop_price,
                                            avg_price, profit_id, tipo_ordem, conta, titular, cl_ord_id, status, date,
                                            text_message)


    @WINFUNCTYPE(None, c_int, c_wchar_p, c_wchar_p, c_wchar_p)
    def account_callback(corretora, corretora_nome_completo, account_id, nome_titular):
        if prov_conn:
            prov_conn.account_callback(corretora, corretora_nome_completo, account_id, nome_titular)


    @WINFUNCTYPE(None, TAssetID, c_wchar_p, c_uint, c_double, c_double, c_int, c_int, c_int, c_int, c_wchar)
    def new_trade_callback(asset_id, date, trade_number, price, vol, qtd, buy_agent, sell_agent, trade_type,
                           is_edit):
        if prov_conn:
            prov_conn.new_trade_callback(asset_id, date, trade_number, price, vol, qtd, buy_agent, sell_agent,
                                         trade_type,
                                         is_edit)


    @WINFUNCTYPE(None, TAssetID, c_double, c_int, c_int)
    def tiny_book_callback(asset_id, price, qtd, side):
        if prov_conn:
            prov_conn.tiny_book_callback(asset_id, price, qtd, side)


    @WINFUNCTYPE(None, TAssetID, c_wchar_p, c_double, c_double, c_double, c_double, c_double, c_double, c_double,
                 c_double, c_double, c_double, c_int, c_int, c_int, c_int, c_int, c_int, c_int)
    def new_daily_callback(asset_id, date, open_val, high, low, close, vol, ajuste, max_limit, min_limit,
                           vol_buyer, vol_seller, qtd, negocios, contratos_open, qtd_buyer, qtd_seller, neg_buyer,
                           neg_seller):
        if prov_conn:
            prov_conn.new_daily_callback(asset_id, date, open_val, high, low, close, vol, ajuste, max_limit, min_limit,
                                         vol_buyer, vol_seller, qtd, negocios, contratos_open, qtd_buyer, qtd_seller,
                                         neg_buyer,
                                         neg_seller)
