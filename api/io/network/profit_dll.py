import struct
from ctypes import *

from api.indep import InternalConfigProviders
from api.logger import logger

# Error Codes
NL_ERR_INIT = 80
NL_OK = 0
NL_ERR_INVALID_ARGS = 90
NL_ERR_INTERNAL_ERROR = 100


# @dataclass
class TAssetID(Structure):
    _fields_ = [("ticker", c_wchar_p),
                ("bolsa", c_wchar_p),
                ("feed", c_int)]


# @dataclass
class TGroupOffer(Structure):
    _fields_ = [("nPosition", c_int),
                ("nQtd", c_int),
                ("nOfferID", c_int),
                ("nAgent", c_int),
                ("sPrice", c_double),
                ("strDtOffer", c_int)]


# @dataclass
class TGroupPrice(Structure):
    _fields_ = [("nQtd", c_int),
                ("nCount", c_int),
                ("sPrice", c_double)]


# @dataclass
class TNewTradeCallback(Structure):
    _fields_ = [("assetId", TAssetID),
                ("date", c_wchar_p),
                ("tradeNumber", c_uint),
                ("price", c_double),
                ("vol", c_double),
                ("qtd", c_int),
                ("buyAgent", c_int),
                ("sellAgent", c_int),
                ("tradeType", c_int),
                ("bIsEdit", c_int)]


class TTheoreticalPriceCallback(Structure):
    _fields_ = [("assetId", TAssetID),
                ("dTheoreticalPrice", c_double),
                ("nTheoreticalQtd", c_uint)]


# @dataclass
class TNewDailyCallback(Structure):
    _fields_ = [("tAssetIDRec", TAssetID),
                ("date", c_wchar_p),
                ("sOpen", c_double),
                ("sHigh", c_double),
                ("sLow", c_double),
                ("sClose", c_double),
                ("sVol", c_double),
                ("sAjuste", c_double),
                ("sMaxLimit", c_double),
                ("sMinLimit", c_double),
                ("sVolBuyer", c_double),
                ("sVolSeller", c_double),
                ("nQtd", c_int),
                ("nNegocios", c_int),
                ("nContratosOpen", c_int),
                ("nQtdBuyer", c_int),
                ("nQtdSeller", c_int),
                ("nNegBuyer", c_int),
                ("nNegSeller", c_int)]


# @dataclass
class TNewHistoryCallback(Structure):
    _fields_ = [("assetId", TAssetID),
                ("date", c_wchar_p),
                ("tradeNumber", c_uint),
                ("price", c_double),
                ("vol", c_double),
                ("qtd", c_int),
                ("buyAgent", c_int),
                ("sellAgent", c_int),
                ("tradeType", c_int)]


# @dataclass
class TProgressCallBack(Structure):
    _fields_ = [("assetId", TAssetID),
                ("nProgress", c_int)]


# @dataclass
class TNewTinyBookCallBack(Structure):
    _fields_ = [("assetId", TAssetID),
                ("price", c_double),
                ("qtd", c_int),
                ("side", c_int)]


# @dataclass
class TPriceBookCallback(Structure):
    _fields_ = [("assetId", TAssetID),
                ("nAction", c_int),
                ("nPosition", c_int),
                ("side", c_int),
                ("nQtd", c_int),
                ("ncount", c_int),
                ("sprice", c_double),
                ("pArraySell", POINTER(c_int)),
                ("pArrayBuy", POINTER(c_int))]


# @dataclass
class TOfferBookCallback(Structure):
    _fields_ = [("assetId", TAssetID),
                ("nAction", c_int),
                ("nPosition", c_int),
                ("side", c_int),
                ("nQtd", c_int),
                ("nAgent", c_int),
                ("nOfferID", c_longlong),
                ("sPrice", c_double),
                ("bHasPrice", c_int),
                ("bHasQtd", c_int),
                ("bHasDate", c_int),
                ("bHasOfferId", c_int),
                ("bHasAgent", c_int),
                ("date", c_wchar_p),
                ("pArraySell", POINTER(c_int)),
                ("pArrayBuy", POINTER(c_int))]


class ProfitDLL:
    # Caminho para a DLL, python tem que ser 32bits
    _profit_dll = WinDLL("ProfitDLL.dll")
    _profit_dll.argtypes = None
    _profit_dll.SendSellOrder.restype = c_longlong
    _profit_dll.SendBuyOrder.restype = c_longlong
    _profit_dll.SendStopBuyOrder.restype = c_longlong
    _profit_dll.SendStopSellOrder.restype = c_longlong
    _profit_dll.SendZeroPosition.restype = c_longlong
    _profit_dll.GetAgentNameByID.restype = c_wchar_p
    _profit_dll.GetAgentShortNameByID.restype = c_wchar_p
    _profit_dll.GetPosition.restype = POINTER(c_int)

    def __init__(self, config_prov: InternalConfigProviders):
        # here the instruments will be kept.
        self._config_prov = config_prov
        self._b_ativo = False
        self._b_market_connected = False
        self._b_connectado = False
        self._b_broker_connected = False
        self._n_nount = 0
        self._price_array_sell = []
        self._price_array_buy = []

    def __del__(self):
        self.disconnect()

    def connect(self, soft_key, username, password, b_roteamento=True):
        try:
            if b_roteamento:
                # market data e roteamento
                self._profit_dll.DLLInitializeLogin(
                    c_wchar_p(soft_key), c_wchar_p(username), c_wchar_p(password), self._state_callback,
                    self._history_callback, self._order_change_callback, self._account_callback,
                    self._new_trade_callback, self._new_daily_callback, self._price_book_callback,
                    self._offer_book_callback, self._new_history_callback, self._progress_callback,
                    self._new_tiny_book_callback)
            else:
                # market data only
                self._profit_dll.DLLInitializeMarketLogin(
                    c_wchar_p(soft_key), c_wchar_p(username), c_wchar_p(password), self._state_callback,
                    self._new_trade_callback, self._new_daily_callback, self._price_book_callback,
                    self._offer_book_callback, self._new_history_callback, self._progress_callback,
                    self._new_tiny_book_callback)

            while True:
                if self.is_connected:
                    self._profit_dll.SetAssetListCallback(self._asset_list_callback)
                    self._profit_dll.SetAdjustHistoryCallbackV2(self._adjust_history_callback_v2)
                    logger.info("DLL Conected.")
                    break

        except Exception as e:
            logger.error(str(e))

    def disconnect(self):
        self._b_ativo = False
        self._b_market_connected = False
        self._b_connectado = False
        self._b_broker_connected = False
        self._profit_dll.DLLFinalize()

    def is_connected(self) -> bool:
        return self._b_market_connected

    @WINFUNCTYPE(None, c_int32, c_int32)
    def _state_callback(self, n_type, n_result):
        # notificacoes de login
        if n_type == 0:
            if n_result == 0:
                self._b_connectado = True
                logger.info("Login: conectado.")
            else:
                self._b_connectado = False
                logger.info(f"Login: {str(n_result)}.")

        elif n_type == 1:
            if n_result == 5:
                self._b_broker_connected = True
                logger.info("Broker: Conectado.")
            elif n_result > 2:
                self._b_broker_connected = False
                logger.info("Broker: Sem conexão com corretora.")
            else:
                self._b_broker_connected = False
                logger.info(f"Broker: Sem conexão com servidores ({str(n_result)}).")

        # notificacoes de login no Market
        elif n_type == 2:
            if n_result == 4:
                logger.info("Market: Conectado.")
                self._b_market_connected = True
            else:
                logger.info(f"Market: {str(n_result)}.")
                self._b_market_connected = False

        # notificacoes de login
        elif n_type == 3:
            if n_result == 0:
                logger.info("Ativação: OK.")
                self._b_ativo = True
            else:
                logger.info(f"Ativação: {str(n_result)}.")
                self._b_ativo = False

        if self._b_market_connected and self._b_ativo and self._b_connectado:
            logger.info("Serviços Conectados.")

        return

    @WINFUNCTYPE(None, TAssetID, c_wchar_p, c_uint, c_double, c_double, c_int, c_int, c_int, c_int)
    def _new_history_callback(self, asset_id, date, trade_number, price, vol, qtd, buy_agent, sell_agent, trade_type):
        logger.info(asset_id.ticker + " | Trade History | " + date + " (" + str(trade_number) + ") " + str(price))
        return

    @WINFUNCTYPE(None, TAssetID, c_int)
    def _progress_callback(self, asset_id, n_progress):
        logger.info(asset_id.ticker + " | Progress | " + str(n_progress))
        return

    @WINFUNCTYPE(None, TAssetID, c_int, c_int, c_int, c_int, c_int, c_double, c_double, c_double, c_longlong,
                 c_wchar_p, c_wchar_p, c_wchar_p, c_wchar_p, c_wchar_p, c_wchar_p)
    def _history_callback(self, r_asset_id, n_corretora, n_qtd, n_traded_qtd, n_leaves_qtd, side, s_price, s_stop_price,
                          s_avg_price, n_profit_id, tipo_ordem, conta, titular, cl_ord_id, status, date):
        logger.info("_history_callback Corretora=" + str(tipo_ordem))
        return

    @WINFUNCTYPE(None, TAssetID, c_int, c_int, c_int, c_int, c_int, c_double, c_double, c_double, c_longlong,
                 c_wchar_p, c_wchar_p, c_wchar_p, c_wchar_p, c_wchar_p, c_wchar_p, c_wchar_p)
    def _order_change_callback(self, r_asset_id, n_corretora, n_qtd, n_traded_qtd, n_leaves_qtd, side, s_price,
                               s_stop_price, s_avg_price, n_profit_id, tipo_ordem, conta, titular, cl_ord_id, status,
                               date, text_message):
        logger.info("todo - _order_change_callback Conta=" + str(conta))
        return

    @WINFUNCTYPE(None, c_int, c_wchar_p, c_wchar_p, c_wchar_p)
    def _account_callback(self, n_corretora, corretora_nome_completo, account_id, nome_titular):
        logger.info("Conta | " + account_id + " - " + nome_titular + " | Corretora " + str(n_corretora) + " - " +
                    corretora_nome_completo)
        return

    @WINFUNCTYPE(None, TAssetID, c_int, c_int, c_int, c_int, c_int, c_double, POINTER(c_int), POINTER(c_int))
    def _price_book_callback(self, asset_id, n_action, n_position, side, n_qtd, n_count, s_price, p_array_sell,
                             p_array_buy):
        if p_array_sell is not None:
            logger.info("todo - _price_book_callback")
        return

    @WINFUNCTYPE(None, TAssetID, c_wchar_p, c_uint, c_double, c_double, c_int, c_int, c_int, c_int, c_wchar)
    def _new_trade_callback(self, asset_id, date, trade_number, price, vol, qtd, buy_agent, sell_agent, trade_type,
                            b_is_edit):
        logger.info(asset_id.ticker + " | Trade | " + str(date) + "(" + str(trade_number) + ") " + str(price))
        return

    @WINFUNCTYPE(None, TAssetID, c_double, c_int, c_int)
    def _new_tiny_book_callback(self, asset_id, price, qtd, side):
        if side == 0:
            logger.info(asset_id.ticker + " | TinyBook | Buy: " + str(price) + " " + str(qtd))
        else:
            logger.info(asset_id.ticker + " | TinyBook | Sell: " + str(price) + " " + str(qtd))

        return

    @WINFUNCTYPE(None, TAssetID, c_wchar_p, c_double, c_double, c_double, c_double, c_double, c_double, c_double,
                 c_double, c_double, c_double, c_int, c_int, c_int, c_int, c_int, c_int, c_int)
    def _new_daily_callback(self, asset_id, date, s_open, s_high, s_low, s_close, s_vol, s_ajuste, s_max_limit,
                            s_min_limit, s_vol_buyer, s_vol_seller, n_qtd, n_negocios, n_contratos_open, n_qtd_buyer,
                            n_qtd_seller, n_neg_buyer, n_neg_seller):
        logger.info(asset_id.ticker + " | DailySignal | " + date + " Open: " + str(s_open) + " High: " + str(s_high) +
                    " Low: " + str(s_low) + " Close: " + str(s_close))
        return

    @staticmethod
    def _descript_price_array(price_array):
        price_array_descripted = []
        n_qtd = price_array[0]
        n_tam = price_array[1]
        logger.info(f"qtd: {n_qtd}, n_tam: {n_tam}")

        arr = cast(price_array, POINTER(c_char))
        frame = bytearray()
        for i in range(n_tam):
            c = arr[i]
            frame.append(c[0])

        start = 8
        for i in range(n_qtd):
            price = struct.unpack("d", frame[start:start + 8])[0]
            start += 8
            qtd = struct.unpack("i", frame[start:start + 4])[0]
            start += 4
            agent = struct.unpack("i", frame[start:start + 4])[0]
            start += 4
            offer_id = struct.unpack("q", frame[start:start + 8])[0]
            start += 8
            date_length = struct.unpack("h", frame[start:start + 2])[0]
            start += 2
            date = frame[start:start + date_length]
            start += date_length

            price_array_descripted.append([price, qtd, agent, offer_id, date])

        return price_array_descripted

    @WINFUNCTYPE(None, TAssetID, c_int, c_int, c_int, c_int, c_int, c_longlong, c_double, c_int, c_int, c_int, c_int,
                 c_int, c_wchar_p, POINTER(c_int), POINTER(c_int))
    def _offer_book_callback(self, asset_id, n_action, n_position, side, n_qtd, n_agent, n_offer_id, s_price,
                             b_has_price, b_has_qtd, b_has_date, b_has_offer_id, b_has_agent, date, p_array_sell,
                             p_array_buy):

        if bool(p_array_sell):
            self._price_array_sell = self._descript_price_array(p_array_sell)

        if bool(p_array_buy):
            self._price_array_buy = self._descript_price_array(p_array_buy)

        if side == 0:
            lst_book = self._price_array_buy
        else:
            lst_book = self._price_array_sell

        if lst_book and 0 <= n_position <= len(lst_book):
            """
            atAdd = 0
            atEdit = 1
            atDelete = 2
            atDeleteFrom = 3
            atFullBook = 4
            """
            if n_action == 0:
                group = [s_price, n_qtd, n_agent]
                idx = len(lst_book) - n_position
                lst_book.insert(idx, group)
            elif n_action == 1:
                group = lst_book[-n_position - 1]
                group[1] = group[1] + n_qtd
                group[2] = group[2] + n_agent
            elif n_action == 2:
                del lst_book[-n_position - 1]
            elif n_action == 3:
                del lst_book[-n_position - 1:]
        return

    @WINFUNCTYPE(None, TAssetID, c_wchar_p, c_uint, c_double)
    def _change_cotation_callback(self, asset_id, date, trade_number, s_price):
        logger.info("todo - _change_cotation_callback")
        return

    @WINFUNCTYPE(None, TAssetID, c_wchar_p)
    def _asset_list_callback(self, asset_id, str_name):
        logger.info("_asset_list_callback Ticker=" + str(asset_id.ticker) + " Name=" + str(str_name))
        return

    @WINFUNCTYPE(None, TAssetID, c_double, c_wchar_p, c_wchar_p, c_wchar_p, c_wchar_p, c_wchar_p, c_uint, c_double)
    def _adjust_history_callback_v2(self, asset_id, value, str_type, str_observ, dt_ajuste, dt_delib, dt_pagamento,
                                    n_flags, d_mult):
        logger.info("todo - _adjust_history_callback_v2")
        return

    def send_sell_order(self, conta: str, broker: str, senha: str, ativo: str, bolsa: str, preco: float, qtd: int):
        return self._profit_dll.SendSellOrder(c_wchar_p(conta), c_wchar_p(broker), c_wchar_p(senha), c_wchar_p(ativo),
                                              c_wchar_p(bolsa), c_double(preco), c_int(qtd))

    def subscribe_offer(self, asset, bolsa):
        return self._profit_dll.SubscribeOfferBook(c_wchar_p(asset), c_wchar_p(bolsa))

    def subscribe_ticker(self, asset, bolsa):
        return self._profit_dll.SubscribeTicker(c_wchar_p(asset), c_wchar_p(bolsa))

    def unsubscribe_ticker(self, asset, bolsa):
        return self._profit_dll.UnsubscribeTicker(c_wchar_p(asset), c_wchar_p(bolsa))

    def print_last_adjusted(self, asset, side, ):
        return self._profit_dll.GetLastDailyClose(c_wchar_p(asset), c_wchar_p(side), byref(c_double()), 1)

    def print_position(self, asset, bolsa, corretora, acc_id):
        result = self._profit_dll.GetPosition(c_wchar_p(str(acc_id)), c_wchar_p(str(corretora)), c_wchar_p(asset),
                                              c_wchar_p(bolsa))

        n_qtd = result[0]

        if n_qtd == 0:
            logger.info("Nao ha posicao para esse ativo")
        else:
            n_tam = result[1]
            logger.info(f"qtd: {n_qtd}, n_tam: {n_tam}")

            arr = cast(result, POINTER(c_char))
            frame = bytearray()
            for i in range(n_tam):
                c = arr[i]
                frame.append(c[0])

            start = 8

            for i in range(n_qtd):
                corretora_id = struct.unpack("i", frame[start:start + 4])[0]
                start += 4

                acc_id_length = struct.unpack("h", frame[start:start + 2])[0]
                start += 2
                account_id = frame[start:start + acc_id_length]
                start += acc_id_length

                titular_length = struct.unpack("h", frame[start:start + 2])[0]
                start += 2
                titular = frame[start:start + titular_length]
                start += titular_length

                ticker_length = struct.unpack("h", frame[start:start + 2])[0]
                start += 2
                ticker = frame[start:start + ticker_length]
                start += ticker_length

                intraday_pos = struct.unpack("i", frame[start:start + 4])[0]
                start += 4

                price = struct.unpack("d", frame[start:start + 8])[0]
                start += 8

                avg_sell_price = struct.unpack("d", frame[start:start + 8])[0]
                start += 8

                sell_qtd = struct.unpack("i", frame[start:start + 4])[0]
                start += 4

                avg_buy_price = struct.unpack("d", frame[start:start + 8])[0]
                start += 8

                buy_qtd = struct.unpack("i", frame[start:start + 4])[0]
                start += 4

                custody_d1 = struct.unpack("i", frame[start:start + 4])[0]
                start += 4

                custody_d2 = struct.unpack("i", frame[start:start + 4])[0]
                start += 4

                custody_d3 = struct.unpack("i", frame[start:start + 4])[0]
                start += 4

                blocked = struct.unpack("i", frame[start:start + 4])[0]
                start += 4

                pending = struct.unpack("i", frame[start:start + 4])[0]
                start += 4

                allocated = struct.unpack("i", frame[start:start + 4])[0]
                start += 4

                provisioned = struct.unpack("i", frame[start:start + 4])[0]
                start += 4

                qtd_position = struct.unpack("i", frame[start:start + 4])[0]
                start += 4

                available = struct.unpack("i", frame[start:start + 4])[0]
                start += 4

                logger.info(f"Corretora: {corretora_id}, Titular: {str(titular)}, Ticker: {str(ticker)}, "
                            f"Price: {price}, AvgSellPrice: {avg_sell_price}, AvgBuyPrice: {avg_buy_price}, "
                            f"SellQtd: {sell_qtd}, BuyQtd: {buy_qtd}")
