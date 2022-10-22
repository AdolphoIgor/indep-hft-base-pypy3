import struct
from ctypes import *
from datetime import datetime, timedelta

from api.indep import InternalConfigProviders
from api.logger import logger


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
    # CONSTANT Error Codes
    _NL_ERR_INIT = 80
    _NL_OK = 0
    _NL_ERR_INVALID_ARGS = 90
    _NL_ERR_INTERNAL_ERROR = 100

    # Pathway to Profit DLL. Keep in mind that Python interpreter must be 32bits version.
    _profit_dll = WinDLL("ProfitDLL.dll")
    _profit_dll.argtypes = None

    # initialiation
    _profit_dll.DLLInitializeLogin.restype = c_short
    _profit_dll.DLLInitializeMarketLogin.restype = c_short
    _profit_dll.DLLFinalize.restype = c_short

    # calls
    _profit_dll.SubscribeTicker.restype = c_short
    _profit_dll.UnsubscribeTicker.restype = c_short
    _profit_dll.SubscribePriceBook.restype = c_short
    _profit_dll.UnsubscribePriceBook.restype = c_short
    _profit_dll.SubscribeOfferBook.restype = c_short
    _profit_dll.UnsubscribeOfferBook.restype = c_short
    _profit_dll.GetAgentNameByID.restype = c_wchar_p
    _profit_dll.GetAgentShortNameByID.restype = c_wchar_p
    _profit_dll.SendBuyOrder.restype = c_longlong
    _profit_dll.SendSellOrder.restype = c_longlong
    _profit_dll.SendStopBuyOrder.restype = c_longlong
    _profit_dll.SendStopSellOrder.restype = c_longlong
    _profit_dll.SendChangeOrder.restype = c_short
    _profit_dll.SendCancelOrder.restype = c_short
    _profit_dll.SendCancelOrders.restype = c_short
    _profit_dll.SendCancelAllOrders.restype = c_short
    _profit_dll.SendZeroPosition.restype = c_longlong
    _profit_dll.GetAccount.restype = c_short
    _profit_dll.GetOrders.restype = c_short
    _profit_dll.GetOrder.restype = c_short
    _profit_dll.GetOrderProfitID.restype = c_short
    _profit_dll.GetPosition.restype = POINTER(c_int)
    _profit_dll.GetHistoryTrades.restype = c_short
    _profit_dll.GetSerieHistory.restype = c_short
    _profit_dll.SubscribeAdjustHistory.restype = c_short
    _profit_dll.UnsubscribeAdjustHistory.restype = c_short
    _profit_dll.SetAdjustHistoryCallback.restype = c_short
    _profit_dll.SetAdjustHistoryCallbackV2.restype = c_short
    _profit_dll.SetTheoreticalPriceCallback.restype = c_short
    _profit_dll.SetServerAndPort.restype = c_short
    _profit_dll.GetServerClock.restype = c_short
    _profit_dll.GetLastDailyClose.restype = c_short

    # callbacks
    _profit_dll.SetDayTrade.restype = c_short
    _profit_dll.SetChangeCotationCallback.restype = c_short
    _profit_dll.SetAssetListCallback.restype = c_short
    _profit_dll.SetAssetListInfoCallback.restype = c_short
    _profit_dll.SetAssetListInfoCallbackV2.restype = c_short
    _profit_dll.SetEnabledLogToDebug.restype = c_short
    _profit_dll.RequestTickerInfo.restype = c_short
    _profit_dll.GetAllTicker.restype = c_short
    _profit_dll.SetChangeStateTickerCallback.restype = c_short
    _profit_dll.SetEnabledHistOrder.restype = c_short

    _dct_asset_state = {
        0: "opened", 2: "frozen", 3: "inhibited", 4: "auctioned", 6: "closed", 10: "preclosing", 13: "preopening"
    }

    _dct_asset_sec_type = {
        0: "Future", 1: "Spot", 2: "SpotOption", 3: "FutureOption", 4: "DerivativeTerm", 5: "Stock", 6: "Option",
        7: "Forward", 8: "ETF", 9: "Index", 10: "OptionExercise", 11: "Unknown", 12: "EconomicIndicator",
        13: "MultilegInstrument", 14: "CommonStock", 15: "PreferredStock", 16: "SecurityLoan", 17: "OptionOnIndex",
        18: "Rights", 19: "CorporateFixedIncome"
    }

    _dct_asset_sec_sub_type = {
        0: "FXSpot", 1: "Gold", 2: "Index", 3: "InterestRate", 4: "FXRate", 5: "ForeignDebt", 6: "Agricultural",
        7: "Energy", 8: "EconomicIndicator", 9: "Strategy", 10: "FutureOption", 11: "Volatility", 12: "Swap",
        13: "MiniContract", 14: "FinancialRollOver", 15: "AgriculturalRollOver", 16: "CarbonCredit", 17: "Unknown",
        18: "Fractionary", 19: "Stock", 20: "Currency", 21: "OTC", 22: "OTCMercadoBalcaoFII",
        23: "FIIFundo de Investimento ImobiliarioOrdinaryRights", 24: "(DO)PreferredRights", 25: "(DP)CommonShares",
        26: "(ON)PreferredShares", 27: "(PN)ClassApreferredShares", 28: "(PNA)ClassBpreferredShares",
        29: "(PNB)ClassCpreferredShares", 30: "(PNC)ClassDpreferredShares", 31: "(PND)OrdinaryReceipts",
        32: "(ON REC)PreferredReceipts", 33: "(PN REC)CommonForward", 34: "FlexibleForward", 35: "DollarForward",
        36: "IndexPointsForward", 37: "NonTradeableETFIndex", 38: "PredefinedCoveredSpread", 39: "TraceableETF",
        40: "NonTradeableIndex", 41: "UserDefinedSpread", 42: "ExchangeDefinedspread", 43: "SecurityLoan",
        44: "TradeableIndex", 45: "Others"
    }

    def __init__(self, config_prov: InternalConfigProviders):
        # here the instruments will be kept.
        self._config_prov = config_prov

        # memory pointers to every list of instruments.
        lst_instruments = self._config_prov.get_internal_provider_data("instruments")
        self._dct_quote = self._config_prov.get_internal_provider_data("quote", sublist=lst_instruments)
        self._dct_tt = self._config_prov.get_internal_provider_data("tt", sublist=lst_instruments)
        self._dct_lp = self._config_prov.get_internal_provider_data("lp", sublist=lst_instruments)
        self._dct_lo = self._config_prov.get_internal_provider_data("lo", sublist=lst_instruments)
        self._dct_account = self._config_prov.get_internal_provider_data("account", sublist=lst_instruments)
        self._dct_orders = self._config_prov.get_internal_provider_data("orders", sublist=lst_instruments)
        self._dct_progress = self._config_prov.get_internal_provider_data("progress", sublist=lst_instruments)
        self._dct_spread = self._config_prov.get_internal_provider_data("spread", sublist=lst_instruments)

        self._b_ativo = False
        self._b_market_connected = False
        self._b_connectado = False
        self._b_broker_connected = False
        self._n_nount = 0
        self._price_array_sell = []
        self._price_array_buy = []

    def __del__(self):
        if self.is_connected():
            self.disconnect()

    def connect(self, soft_key, username, password, b_roteamento=True):
        try:
            if b_roteamento:
                # market data e roteamento
                self._profit_dll.DLLInitializeLogin(
                    c_wchar_p(soft_key), c_wchar_p(username), c_wchar_p(password), self._state_callback,
                    self._history_callback, self._order_change_callback, self._account_callback,
                    self._new_trade_callback, self._new_daily_callback, self._price_book_callback,
                    self._offer_book_callback, self._history_trade_callback, self._progress_callback,
                    self._tiny_book_callback)
            else:
                # market data only
                self._profit_dll.DLLInitializeMarketLogin(
                    c_wchar_p(soft_key), c_wchar_p(username), c_wchar_p(password), self._state_callback,
                    self._new_trade_callback, self._new_daily_callback, self._price_book_callback,
                    self._offer_book_callback, self._history_trade_callback, self._progress_callback,
                    self._tiny_book_callback)

            while True:
                if self.is_connected:
                    self._profit_dll.SetChangeCotationCallback(self._change_cotation_callback)
                    self._profit_dll.SetAssetListCallback(self._asset_list_callback)
                    self._profit_dll.SetAssetListInfoCallback(self._asset_list_info_callback)
                    self._profit_dll.SetAssetListInfoCallbackV2(self._asset_list_info_callback_v2)
                    self._profit_dll.SetAdjustHistoryCallback(self._adjust_history_callback)
                    self._profit_dll.SetAdjustHistoryCallbackV2(self._adjust_history_callback_v2)
                    self._profit_dll.SetChangeStateTickerCallback(self._change_state_ticker_callback)
                    self._profit_dll.SetTheoreticalPriceCallback(self._set_theoretical_price_callback)

                    logger.info("DLL Conected.")
                    break

        except Exception as e:
            logger.error(str(e))

    def disconnect(self):
        if self.is_connected():
            self._b_ativo = False
            self._b_market_connected = False
            self._b_connectado = False
            self._b_broker_connected = False
            self._profit_dll.DLLFinalize()

    def is_connected(self) -> bool:
        return self._b_market_connected

    def get_asset_state(self) -> dict:
        return self._dct_asset_state.copy()

    # METHODS ----------------------------------------------------------------------------------------------------------
    def subscribe_ticker(self, ticker: str, bolsa: str):
        """
        :param ticker:
        :param bolsa:
        :return: triggers self._adjust_history_callback or self._adjust_history_callback_v2
        """
        # TODO: find out which callback functions will be called.
        return self._profit_dll.SubscribeTicker(c_wchar_p(ticker), c_wchar_p(bolsa))

    def unsubscribe_ticker(self, ticker: str, bolsa: str):
        """
        :param ticker:
        :param bolsa:
        :return:
        """
        return self._profit_dll.UnsubscribeTicker(c_wchar_p(ticker), c_wchar_p(bolsa))

    def subscribe_price_book(self, ticker: str, bolsa: str):
        """
        :param ticker:
        :param bolsa:
        :return: Triggers the callback function self._price_book_callback()
        """
        return self._profit_dll.SubscribePriceBook(c_wchar_p(ticker), c_wchar_p(bolsa))

    def unsubscribe_price_book(self, ticker: str, bolsa: str):
        """
        :param ticker:
        :param bolsa:
        :return:
        """
        return self._profit_dll.UnsubscribePriceBook(c_wchar_p(ticker), c_wchar_p(bolsa))

    def subscribe_offer_book(self, ticker: str, bolsa: str):
        """
        :param ticker:
        :param bolsa:
        :return: Triggers the callback function self._offer_book_callback()
        """
        return self._profit_dll.SubscribeOfferBook(c_wchar_p(ticker), c_wchar_p(bolsa))

    def unsubscribe_offer_book(self, ticker: str, bolsa: str):
        """
        :param ticker:
        :param bolsa:
        :return:
        """
        return self._profit_dll.UnsubscribeOfferBook(c_wchar_p(ticker), c_wchar_p(bolsa))

    def get_agent_name_by_id(self, n_id: int):
        """
        :param n_id:
        :return:
        """
        return self._profit_dll.GetAgentNameByID(c_int(n_id))

    def get_agent_short_name_by_id(self, n_id: int):
        """
        :param n_id:
        :return:
        """
        return self._profit_dll.GetAgentShortNameByID(c_int(n_id))

    def send_buy_order(self, conta: str, broker: str, senha: str, ativo: str, bolsa: str, preco: float, qtd: int):
        """
        :param conta:
        :param broker:
        :param senha:
        :param ativo:
        :param bolsa: [B=Bovespa | F=BM&F]
        :param preco:
        :param qtd:
        :return: Returns de cl_ord_id to be compared to the return of self._history_trade_callback().
        """
        return self._profit_dll.SendBuyOrder(c_wchar_p(conta), c_wchar_p(broker), c_wchar_p(senha), c_wchar_p(ativo),
                                             c_wchar_p(bolsa), c_double(preco), c_int(qtd))

    def send_sell_order(self, conta: str, broker: str, senha: str, ativo: str, bolsa: str, preco: float, qtd: int):
        """
        :param conta:
        :param broker:
        :param senha:
        :param ativo:
        :param bolsa: [B=Bovespa | F=BM&F]
        :param preco:
        :param qtd:
        :return: Returns de cl_ord_id to be compared to the return of self._history_trade_callback().
        """
        return self._profit_dll.SendSellOrder(c_wchar_p(conta), c_wchar_p(broker), c_wchar_p(senha), c_wchar_p(ativo),
                                              c_wchar_p(bolsa), c_double(preco), c_int(qtd))

    def send_stop_buy_order(self, conta: str, broker: str, senha: str, ativo: str, bolsa: str, preco: float,
                            s_stop_price: float, qtd: int):
        """
        :param conta:
        :param broker:
        :param senha:
        :param ativo:
        :param bolsa: [B=Bovespa | F=BM&F]
        :param preco:
        :param s_stop_price:
        :param qtd:
        :return: Returns de cl_ord_id to be compared to the return of self._history_trade_callback().
        """
        return self._profit_dll.SendStopBuyOrder(c_wchar_p(conta), c_wchar_p(broker), c_wchar_p(senha),
                                                 c_wchar_p(ativo), c_wchar_p(bolsa), c_double(preco),
                                                 c_double(s_stop_price), c_int(qtd))

    def send_stop_sell_order(self, conta: str, broker: str, senha: str, ativo: str, bolsa: str, preco: float,
                             s_stop_price: float, qtd: int):
        """
        :param conta:
        :param broker:
        :param senha:
        :param ativo:
        :param bolsa: [B=Bovespa | F=BM&F]
        :param preco:
        :param s_stop_price:
        :param qtd:
        :return: Returns de cl_ord_id to be compared to the return of self._history_trade_callback().
        """
        return self._profit_dll.SendSellOrder(c_wchar_p(conta), c_wchar_p(broker), c_wchar_p(senha),
                                              c_wchar_p(ativo), c_wchar_p(bolsa), c_double(preco),
                                              c_double(s_stop_price), c_int(qtd))

    def send_change_order(self, conta: str, broker: str, senha: str, cl_ord_id: str, preco: float, qtd: int):
        """
        :param conta:
        :param broker:
        :param senha:
        :param cl_ord_id:
        :param preco:
        :param qtd:
        :return:
        """
        return self._profit_dll.SendChangeOrder(c_wchar_p(conta), c_wchar_p(broker), c_wchar_p(senha),
                                                c_wchar_p(cl_ord_id), c_double(preco), c_int(qtd))

    def send_cancel_order(self, conta: str, broker: str, cl_ord_id: str, senha: str):
        """
        :param conta:
        :param broker:
        :param cl_ord_id:
        :param senha:
        :return:
        """
        return self._profit_dll.SendCancelOrder(c_wchar_p(conta), c_wchar_p(broker), c_wchar_p(cl_ord_id),
                                                c_wchar_p(senha))

    def send_cancel_orders(self, conta: str, broker: str, senha: str, ativo: str, bolsa: str):
        """
        :param conta:
        :param broker:
        :param senha:
        :param ativo:
        :param bolsa:
        :return:
        """
        return self._profit_dll.SendCancelOrders(c_wchar_p(conta), c_wchar_p(broker), c_wchar_p(senha),
                                                 c_wchar_p(ativo), c_wchar_p(bolsa))

    def send_cancel_all_orders(self, conta: str, broker: str, senha: str):
        """
        :param conta:
        :param broker:
        :param senha:
        :return:
        """
        return self._profit_dll.SendCancelAllOrders(c_wchar_p(conta), c_wchar_p(broker), c_wchar_p(senha))

    def send_zero_position(self, conta: str, broker: str, ativo: str, bolsa: str, senha: str, price: float):
        """
        :param conta:
        :param broker:
        :param ativo:
        :param bolsa:
        :param senha:
        :param price:
        :return: Returns de cl_ord_id to be compared to the return of self._history_trade_callback().
        """
        return self._profit_dll.SendZeroPosition(c_wchar_p(conta), c_wchar_p(broker), c_wchar_p(ativo),
                                                 c_wchar_p(senha), c_wchar_p(bolsa), c_double(price))

    def get_account(self):
        """
        :return: Returns on self._account_callback().
        """
        return self._profit_dll.GetAccount()

    def get_orders(self, conta: str, broker: str, dt_start: str, dt_end: str):
        """
        :param conta:
        :param broker:
        :param dt_start:
        :param dt_end:
        :return: Returns on self._history_trade_callback().
        """
        return self._profit_dll.GetOrders(c_wchar_p(conta), c_wchar_p(broker), c_wchar_p(dt_start), c_wchar_p(dt_end))

    def get_order(self, cl_ord_id: float):
        """
        :param cl_ord_id:
        :return: Returns on self._order_change_callback().
        """
        return self._profit_dll.GetOrder(c_double(cl_ord_id))

    def get_order_profit_id(self, n_profit_id: float):
        """
        :param n_profit_id:
        :return: Returns on self._order_change_callback().
        """
        return self._profit_dll.GetOrders(c_double(n_profit_id))

    def get_position(self, conta: str, broker: str, ativo: str, bolsa: str):
        """
        :param conta:
        :param broker:
        :param ativo:
        :param bolsa:
        :return: a dictionary fulfilled wit the server's response.
        """
        result = self._profit_dll.GetPosition(c_wchar_p(conta), c_wchar_p(broker), c_wchar_p(ativo), c_wchar_p(bolsa))

        ret = {}
        n_qtd = result[0]
        if n_qtd == 0:
            logger.info("Nao ha posicao para esse ativo")
            return result, ret

        n_tam = result[1]
        logger.info(f"qtd: {n_qtd}, n_tam: {n_tam}")

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

            logger.info(ret)

        return result, ret

    def get_history_trades(self, ativo: str, bolsa: str, dt_start: str, dt_end: str):
        """
        :param ativo:
        :param bolsa:
        :param dt_start:
        :param dt_end:
        :return: Triggers self._history_trade_callback() and self._progress_callback()
        """
        return self._profit_dll.GetHistoryTrades(c_wchar_p(ativo), c_wchar_p(bolsa), c_wchar_p(dt_start),
                                                 c_wchar_p(dt_end))

    def get_serie_history(self, ativo: str, bolsa: str, dt_start: str, dt_end: str, n_quote_number_start: int,
                          n_quote_number_end: int):
        """
        :param ativo:
        :param bolsa:
        :param dt_start:
        :param dt_end:
        :param n_quote_number_start:
        :param n_quote_number_end:
        :return: Triggers self._history_trade_callback and self._progress_callback
        """
        return self._profit_dll.GetSerieHistory(c_wchar_p(ativo), c_wchar_p(bolsa), c_wchar_p(dt_start),
                                                c_wchar_p(dt_end), c_uint(n_quote_number_start),
                                                c_uint(n_quote_number_end))

    def set_day_trade(self, b_use_day_trade: bool):
        """
        :param: b_use_day_trade:
        :return: a tuple with one of this class constants (_NL_ERR_INIT, _NL_OK, _NL_ERR_INVALID_ARGS,
                    _NL_ERR_INTERNAL_ERROR) and the variable b_use_day_trade
        """
        b_use_day_trade = c_int(1 if b_use_day_trade else 0)
        return self._profit_dll.SetDayTrade(b_use_day_trade), b_use_day_trade

    def set_enabled_log_to_debug(self, b_enabled: bool):
        """
        :param b_enabled:
        :return: a tuple with one of this class constants (_NL_ERR_INIT, _NL_OK, _NL_ERR_INVALID_ARGS,
                    _NL_ERR_INTERNAL_ERROR) and the variable b_enabled
        """
        b_enabled = c_int(1 if b_enabled else 0)
        return self._profit_dll.SetEnabledLogToDebug(b_enabled), b_enabled

    def request_ticker_info(self, ativo: str, bolsa: str):
        """
            Is designed ask for new information about an asset.

            Can only be called before a connection has been established.

            :return: Triggers self._asset_list_info_callback(), and
            self._asset_list_callback()
        """
        return self._profit_dll.RequestTickerInfo(c_wchar_p(ativo), c_wchar_p(bolsa))

    def get_all_ticker(self, bolsa: str):
        """
        Is designed ask for new information about assets from a specific stockmarket.

        Can only be called before a connection has been established.

        :param: bolsa: B=Bovespa | F=BMF |‘’=ALL.
        :return: Triggers self._asset_list_info_callback(), and
        self._asset_list_callback()
        """
        return self._profit_dll.GetAllTicker(c_wchar_p(bolsa))

    def set_enabled_hist_order(self, b_enabled: bool):
        """
        :param b_enabled:
        :return: a tuple with one of this class constants (_NL_ERR_INIT, _NL_OK, _NL_ERR_INVALID_ARGS,
                    _NL_ERR_INTERNAL_ERROR) and the variable b_enabled
        """
        b_enabled = c_int(1 if b_enabled else 0)
        return self._profit_dll.SetEnabledHistOrder(b_enabled), b_enabled

    def subscribe_adjust_history(self, ativo: str, bolsa: str):
        """
        :param ativo:
        :param bolsa:
        :return: triggers self._adjust_history_callback()
        """
        return self._profit_dll.SubscribeAdjustHistory(c_wchar_p(ativo), c_wchar_p(bolsa))

    def unsubscribe_adjust_history(self, ativo: str, bolsa: str):
        """
        :param ativo:
        :param bolsa:
        :return:
        """
        return self._profit_dll.UnSubscribeAdjustHistory(c_wchar_p(ativo), c_wchar_p(bolsa))

    def set_server_and_port(self, server, port: str):
        """
            Is designed to connect to custom market Data servers. The internal staff must tell you when this strategy
            is necessary.

            Can only be called before a connection has been established.

            :return: Can return any constants of this class whose name starts with 'self._NL_...'.
        """
        return self._profit_dll.SetServerAndPort(c_wchar_p(server), c_wchar_p(port))

    def get_server_clock(self):
        """
            Returns the current datetime from the server's internal clock.

            Can only be called after a connection has been established.

            :return: Returns a tuple with any constants of this class whose name starts with 'self._NL_...' and a
            dictionary containing the date data (or not, empty) depending on the result of the call.
        """
        dt_prm = c_double(-1.0)
        year_prm, mth_prm, day_prm = c_int(-1), c_int(-1), c_int(-1)
        hr_prm, min_prm, sec_prm, mil_prm = c_int(-1), c_int(-1), c_int(-1), c_int(-1)

        ret_dct = {}
        ret = self._profit_dll.GetServerClock(dt_prm, year_prm, mth_prm, day_prm, hr_prm, min_prm, sec_prm, mil_prm)
        if ret != self._NL_OK:
            return ret, ret_dct

        ret_dct['date'] = datetime.fromtimestamp(dt_prm.value)
        ret_dct['year'] = year_prm.value
        ret_dct['month'] = mth_prm.value
        ret_dct['day'] = day_prm.value
        ret_dct['hour'] = hr_prm.value
        ret_dct['min'] = min_prm.value
        ret_dct['sec'] = sec_prm.value
        ret_dct['mil'] = mil_prm.value
        ret_dct['bra_format'] = f"{year_prm.value}/{mth_prm.value}/{day_prm.value} {hr_prm.value}:{min_prm.value}:" \
                                f"{sec_prm.value}.{mil_prm.value}"
        return ret, ret_dct

    def get_last_daily_close(self, ticker, bolsa, bol_val_adj=1):
        """
            Returns the close value from the last session. if bol_val_adj == True will return the adjusted value,
            commonly used in future markets.

            Can only be called after a connection has been established.
            Can only be called after a previous call to self.subscribe_ticker() which means, the ticker has to be
            already subscribed to receive data from the server.

            Triggers self._progress_callback() and self._adjust_history_callback().

            :return Returns a tuple with  NL_OK or NL_WAITING_SERVER or NL_ERR_INVALID_ARGS and the close value.
        """
        val_close = c_double(-1.0)
        ret = self._profit_dll.GetLastDailyClose(c_wchar_p(ticker), c_wchar_p(bolsa), val_close, c_int(bol_val_adj))
        return ret, val_close

    # CALLBACKS --------------------------------------------------------------------------------------------------------
    @WINFUNCTYPE(None, TAssetID, c_wchar_p, c_uint, c_double)
    def _change_cotation_callback(self, asset_id, date, trade_number, price):
        dct_quote = self._dct_quote.get(asset_id.ticker, {})
        dct_quote["date"] = date
        dct_quote["last"] = price
        dct_quote["trade_number"] = trade_number

    @WINFUNCTYPE(None, TAssetID, c_wchar_p)
    def _asset_list_callback(self, asset_id, name):
        dct_quote = self._dct_quote.get(asset_id.ticker, {})
        dct_quote["description"] = name

    @staticmethod
    def __get_tick_value(name: str) -> float:
        name = name.upper()
        if name.startswith(("DOL", "WDO"), 0):
            return 0.5

        if name.startswith(("IND", "WIN"), 0):
            return 1.0

        return 0.1

    @WINFUNCTYPE(None, TAssetID, c_wchar_p, c_wchar_p, c_int, c_int, c_int, c_int, c_int, c_double, c_double, c_wchar_p,
                 c_wchar_p)
    def _asset_list_info_callback(self, asset_id, name, description, min_order_qtd, max_order_qtd, lote, security_type,
                                  security_sub_type, min_price_increment, contract_multiplier, valid_date, isin):
        dct_quote = self._dct_quote.get(asset_id.ticker, {})
        dct_quote["name"] = name
        dct_quote["description"] = description
        dct_quote["min_order_qtd"] = min_order_qtd
        dct_quote["max_order_qtd"] = max_order_qtd
        dct_quote["lote"] = lote
        dct_quote["security_type"] = security_type
        dct_quote["security_sub_type"] = security_sub_type
        dct_quote["min_price_increment"] = min_price_increment
        dct_quote["contract_multiplier"] = contract_multiplier
        dct_quote["valid_date"] = valid_date
        dct_quote["isin"] = isin
        dct_quote["security_type_desc"] = self._dct_asset_sec_type.get(security_type)
        dct_quote["security_sub_type_desc"] = self._dct_asset_sec_type.get(security_sub_type)
        dct_quote["tick_value"] = self.__get_tick_value(name)

    @WINFUNCTYPE(None, TAssetID, c_wchar_p, c_wchar_p, c_int, c_int, c_int, c_int, c_int, c_int, c_double, c_double,
                 c_wchar_p, c_wchar_p, c_wchar_p, c_wchar_p)
    def _asset_list_info_callback_v2(self, asset_id, name, description, min_order_qtd, max_order_qtd, lote,
                                     security_type, security_sub_type, min_price_increment, contract_multiplier,
                                     valid_date, isin, setor, sub_setor, segmento):
        dct_quote = self._dct_quote.get(asset_id.ticker, {})
        dct_quote["name"] = name
        dct_quote["description"] = description
        dct_quote["min_order_qtd"] = min_order_qtd
        dct_quote["max_order_qtd"] = max_order_qtd
        dct_quote["lote"] = lote
        dct_quote["security_type"] = security_type
        dct_quote["security_sub_type"] = security_sub_type
        dct_quote["min_price_increment"] = min_price_increment
        dct_quote["contract_multiplier"] = contract_multiplier
        dct_quote["valid_date"] = valid_date
        dct_quote["isin"] = isin
        dct_quote["setor"] = setor
        dct_quote["sub_setor"] = sub_setor
        dct_quote["segmento"] = segmento
        dct_quote["security_type_desc"] = self._dct_asset_sec_type.get(security_type)
        dct_quote["security_sub_type_desc"] = self._dct_asset_sec_type.get(security_sub_type)
        dct_quote["tick_value"] = self.__get_tick_value(name)

    @WINFUNCTYPE(None, TAssetID, c_double, c_wchar_p, c_wchar_p, c_wchar_p, c_wchar_p, c_wchar_p, c_int)
    def _adjust_history_callback(self, asset_id, value, adjust_type, observ, ajuste, deliber, pagamento, affect_price):
        dct_quote = self._dct_quote.get(asset_id.ticker, {})
        dct_quote["ajuste"] = value

    @WINFUNCTYPE(None, TAssetID, c_double, c_wchar_p, c_wchar_p, c_wchar_p, c_wchar_p, c_wchar_p, c_uint, c_double)
    def _adjust_history_callback_v2(self, asset_id, value, adj_type, observ, dt_ajuste, dt_delib, dt_pagamento, flags,
                                    mult):
        dct_quote = self._dct_quote.get(asset_id.ticker, {})
        dct_quote["ajuste"] = value

    @WINFUNCTYPE(None, TAssetID, c_wchar_p, c_int)
    def _change_state_ticker_callback(self, asset_id, date, state):
        dct_quote = self._dct_quote.get(asset_id.ticker, {})
        dct_quote["date"] = date
        dct_quote["state"] = state
        dct_quote["desc_state"] = self._dct_asset_state.get(state)

    @WINFUNCTYPE(None, TAssetID, c_int, c_int, c_int, c_int, c_int, c_double, POINTER(c_int), POINTER(c_int))
    def _price_book_callback(self, asset_id, action, position, side, qtd, count, price, array_sell, array_buy):

        def decript(price_array):
            price_array_descripted = []
            n_qtd = price_array[0]
            n_tam = price_array[1]

            arr = cast(price_array, POINTER(c_char))
            frame = bytearray()
            for i in range(n_tam):
                c = arr[i]
                frame.append(c[0])

            start = 8
            for i in range(n_qtd):
                i_price = struct.unpack("d", frame[start:start + 8])[0]
                start += 8
                i_qtd = struct.unpack("i", frame[start:start + 4])[0]
                start += 4
                i_count = struct.unpack("i", frame[start:start + 4])[0]
                price_array_descripted.append([i_price, i_qtd, i_count])

            return price_array_descripted

        lst_book = self._dct_lp.get(asset_id.ticker, [])

        if action == 4:
            lst_book.append(decript(array_buy))
            lst_book.append(decript(array_sell))
            return

        lst_book_side = lst_book[side]
        position = len(lst_book_side) - position - 1

        # action[atAdd = 0, atEdit = 1, atDelete = 2, atDeleteFrom = 3, atFullBook = 4]
        if action == 0:
            lst_book_side.insert(position + 1, [price, qtd, count])

        elif action == 1:
            lst_book_side[position] = [price, qtd, count]

        elif action == 2:
            lst_book_side.pop(position)

        elif action == 3:
            lst_book[side] = lst_book_side[position:]

    @WINFUNCTYPE(None, TAssetID, c_int, c_int, c_int, c_int, c_int, c_longlong, c_double, c_char, c_char, c_char,
                 c_char, c_char, c_wchar_p, POINTER(c_int), POINTER(c_int))
    def _offer_book_callback(self, asset_id, action, position, side, qtd, agent, offer_id, price, has_price, has_qtd,
                             has_date, has_offer_id, has_agent, date, array_sell, array_buy):

        def decript(price_array):
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

                price_array_descripted.append([i_price, i_qtd, i_agent, i_offer_id, i_date])

            return price_array_descripted

        lst_book = self._dct_lo.get(asset_id.ticker, [])

        if action == 4:
            lst_book.append(decript(array_buy))
            lst_book.append(decript(array_sell))
            return

        lst_book_side = lst_book[side]
        position = len(lst_book_side) - position - 1

        # action[atAdd = 0, atEdit = 1, atDelete = 2, atDeleteFrom = 3, atFullBook = 4]
        if action == 0:
            lst_book_side.insert(position + 1, [price, qtd, agent, offer_id, date, None])

        elif action == 1:
            lst_book_side[position] = [price, qtd, agent, offer_id, date]

        elif action == 2:
            lst_book_side.pop(position)

        elif action == 3:
            lst_book[side] = lst_book_side[position:]

    @WINFUNCTYPE(None, TAssetID, c_double, c_longlong)
    def _set_theoretical_price_callback(self, asset_id, theoretical_price, theoretical_qtd):
        dct_quote = self._dct_quote.get(asset_id.ticker, {})
        dct_quote["theoretical_price"] = theoretical_price
        dct_quote["theoretical_qtd"] = theoretical_qtd

    @WINFUNCTYPE(None, c_int32, c_int32)
    def _state_callback(self, type_val, result):
        # 0 : connStLogin (Notify Login Change)
        if type_val == 0:
            if result == 0:
                self._b_connectado = True
                logger.info("Login: conectado.")
            else:
                self._b_connectado = False
                logger.info(f"Login: {str(result)}.")

        # 1 : connStBroker (Notify Broker Change)
        elif type_val == 1:
            if result == 5:
                self._b_broker_connected = True
                logger.info("Broker: Conectado.")
            elif result > 2:
                self._b_broker_connected = False
                logger.info("Broker: Sem conexão com corretora.")
            else:
                self._b_broker_connected = False
                logger.info(f"Broker: Sem conexão com servidores ({str(result)}).")

        # 2 : connStMarket (Notify Market Change)
        elif type_val == 2:
            if result == 4:
                logger.info("Market: Conectado.")
                self._b_market_connected = True
            else:
                logger.info(f"Market: {str(result)}.")
                self._b_market_connected = False

        # 3 : connStActv (Notify Atctivation do Profit)
        elif type_val == 3:
            if result == 0:
                logger.info("Ativação: OK.")
                self._b_ativo = True
            else:
                logger.info(f"Ativação: {str(result)}.")
                self._b_ativo = False

        if self._b_market_connected and self._b_ativo and self._b_connectado:
            logger.info("Serviços Conectados.")

    def find_lim_ord_pos_book_offer(self, tipo_ordem, status, asset_id, side, price, date, cl_ord_id):
        if (tipo_ordem == "limitada" and status == "open") or (tipo_ordem == "market" and status == "part_exec"):
            lst_book = self._dct_lo.get(asset_id.ticker, [])

            lst_prc = list(filter(lambda x: x[0] == price, lst_book[side]))
            if lst_prc:
                lst_offers = list(filter(lambda x: datetime.strptime(x, "%Y-%m-%d %H:%M:%S.%f") == date, lst_prc))
                if not lst_offers:
                    dt_start = datetime.strptime(date, "%Y-%m-%d %H:%M:%S.%f")
                    dt_end = dt_start + timedelta(milliseconds=500)
                    dt_start = dt_start - timedelta(milliseconds=500)
                    lst_offers = list(filter(lambda x: dt_start < datetime.strptime(x, "%Y-%m-%d %H:%M:%S.%f") < dt_end,
                                             lst_prc))
                if lst_offers:
                    lst_offers[-1][1].append(cl_ord_id)

    @WINFUNCTYPE(None, TAssetID, c_int, c_int, c_int, c_int, c_int, c_double, c_double, c_double, c_longlong, c_wchar_p,
                 c_wchar_p, c_wchar_p, c_wchar_p, c_wchar_p, c_wchar_p)
    def _history_callback(self, asset_id, corretora, qtd, traded_qtd, leaves_qtd, side, price, stop_price, avg_price,
                          profit_id, tipo_ordem, conta, titular, cl_ord_id, status, date):

        self.find_lim_ord_pos_book_offer(tipo_ordem, status, asset_id, side, price, date, cl_ord_id)

        lst_orders = self._dct_orders.get(asset_id.ticker, [])
        order = None
        for ordr in lst_orders:
            if ordr.get("cl_ord_id") == cl_ord_id:
                order = ordr
                break

        if order is None:
            lst_orders.append({
                "corretora": corretora, "qtd": qtd, "traded_qtd": traded_qtd, "leaves_qtd": leaves_qtd, "side": side,
                "price": price, "stop_price": stop_price, "avg_price": avg_price, "profit_id": profit_id,
                "tipo_ordem": tipo_ordem, "conta": conta, "titular": titular, "cl_ord_id": cl_ord_id, "status": status,
                "date": date
            })
        else:
            order.update({
                "corretora": corretora, "qtd": qtd, "traded_qtd": traded_qtd, "leaves_qtd": leaves_qtd, "side": side,
                "price": price, "stop_price": stop_price, "avg_price": avg_price, "profit_id": profit_id,
                "tipo_ordem": tipo_ordem, "conta": conta, "titular": titular, "cl_ord_id": cl_ord_id, "status": status,
                "date": date
            })

    @WINFUNCTYPE(None, TAssetID, c_int)
    def _progress_callback(self, asset_id, progress):
        dct_progress = self._dct_progress.get(asset_id.ticker, {})
        dct_progress.update({"progress": progress})

    @WINFUNCTYPE(None, TAssetID, c_wchar_p, c_uint, c_double, c_double, c_int, c_int, c_int, c_int)
    def _history_trade_callback(self, asset_id, date, trade_number, price, vol, qtd, buy_agent, sell_agent, trade_type):
        # trade_type = 2: Compra, 3: Venda, 4: Leilão, 13:RLP.
        if trade_type in [2, 3, 4, 14]:
            lst_tt = self._dct_tt.get(asset_id.ticker, [])
            lst_tt.append([trade_number, date, price, qtd, buy_agent, sell_agent])

    @WINFUNCTYPE(None, TAssetID, c_int, c_int, c_int, c_int, c_int, c_double, c_double, c_double, c_longlong,
                 c_wchar_p, c_wchar_p, c_wchar_p, c_wchar_p, c_wchar_p, c_wchar_p, c_wchar_p)
    def _order_change_callback(self, asset_id, corretora, qtd, traded_qtd, leaves_qtd, side, price, stop_price,
                               avg_price, profit_id, tipo_ordem, conta, titular, cl_ord_id, status, date, text_message):

        self.find_lim_ord_pos_book_offer(tipo_ordem, status, asset_id, side, price, date, cl_ord_id)

        lst_orders = self._dct_orders.get(asset_id.ticker, [])
        order = None
        for ordr in lst_orders:
            if ordr.get("cl_ord_id") == cl_ord_id:
                order = ordr
                break

        if order is None:
            lst_orders.append({
                "corretora": corretora, "qtd": qtd, "traded_qtd": traded_qtd, "leaves_qtd": leaves_qtd, "side": side,
                "price": price, "stop_price": stop_price, "avg_price": avg_price, "profit_id": profit_id,
                "tipo_ordem": tipo_ordem, "conta": conta, "titular": titular, "cl_ord_id": cl_ord_id, "status": status,
                "date": date, "text_message": text_message
            })
        else:
            order.update({
                "corretora": corretora, "qtd": qtd, "traded_qtd": traded_qtd, "leaves_qtd": leaves_qtd, "side": side,
                "price": price, "stop_price": stop_price, "avg_price": avg_price, "profit_id": profit_id,
                "tipo_ordem": tipo_ordem, "conta": conta, "titular": titular, "cl_ord_id": cl_ord_id, "status": status,
                "date": date, "text_message": text_message
            })

    @WINFUNCTYPE(None, c_int, c_wchar_p, c_wchar_p, c_wchar_p)
    def _account_callback(self, corretora, corretora_nome_completo, account_id, nome_titular):
        dct_account = self._dct_account.get("Corretora", {})
        dct_account.update({"corretora": corretora, "corretora_nome_completo": corretora_nome_completo,
                            "account_id": account_id, "nome_titular": nome_titular
                            })

    @WINFUNCTYPE(None, TAssetID, c_wchar_p, c_uint, c_double, c_double, c_int, c_int, c_int, c_int, c_wchar)
    def _new_trade_callback(self, asset_id, date, trade_number, price, vol, qtd, buy_agent, sell_agent, trade_type,
                            is_edit):
        # trade_type = 2: Compra, 3: Venda, 4: Leilão, 13:RLP.
        if trade_type in [2, 3, 4, 14]:
            lst_tt = self._dct_tt.get(asset_id.ticker, [])
            lst_tt.append([trade_number, date, price, qtd, buy_agent, sell_agent])

    @WINFUNCTYPE(None, TAssetID, c_double, c_int, c_int)
    def _tiny_book_callback(self, asset_id, price, qtd, side):
        lst_spread = self._dct_spread.get(asset_id.ticker, [])
        lst_spread[side] = [qtd, price]

    @WINFUNCTYPE(None, TAssetID, c_wchar_p, c_double, c_double, c_double, c_double, c_double, c_double, c_double,
                 c_double, c_double, c_double, c_int, c_int, c_int, c_int, c_int, c_int, c_int)
    def _new_daily_callback(self, asset_id, date, open_val, high, low, close, vol, ajuste, max_limit, min_limit,
                            vol_buyer, vol_seller, qtd, negocios, contratos_open, qtd_buyer, qtd_seller, neg_buyer,
                            neg_seller):
        dct_quote = self._dct_quote.get(asset_id.ticker, {})
        dct_quote.update({"date": date, "open_val": open_val, "high": high, "low": low, "close": close, "vol": vol,
                          "ajuste": ajuste, "max_limit": max_limit, "min_limit": min_limit, "vol_buyer": vol_buyer,
                          "vol_seller": vol_seller, "qtd": qtd, "negocios": negocios, "contratos_open": contratos_open,
                          "qtd_buyer": qtd_buyer, "qtd_seller": qtd_seller, "neg_buyer": neg_buyer,
                          "neg_seller": neg_seller
                          })
