from datetime import datetime, timedelta

from api.jobs.internal_config_provider import InternalConfigProviders
from api.logger import logger


class ProfitDLL:

    _dct_side = {
        0: "Compra", 1: "Venda"
    }

    _dct_asset_state = {
        0: "opened", 2: "frozen", 3: "inhibited", 4: "auctioned", 6: "closed", 10: "preclosing", 13: "preopening"
    }

    _dct_trade_type = {
        1: "Cross trade", 2: "Compra agressão", 3: "Venda agressão", 4: "Leilão", 5: "Surveillance", 6: "Expit",
        32: "Desconhecido", 7: "Options Exercise", 8: "Over the counter", 9: "Derivative Term", 10: "Index",
        11: "BTC", 12: "On Behalf", 13: "RLP"
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

    # strAdjustType do callback TAdjustHistoryCallBack.
    _lst_str_adjust_type = [
        "None", "Unknown", "JurosRF", "Dividendo", "Rendimento", "Subscricao", "Desdobramento", "ResgateTotalRF",
        "ResgateTotalRV", "AmortizacaoRF", "JurosCapProprio", "SubsComRenuncia", "Bonificacao", "Grupamento",
        "JuncaoSerie", "Cisao", "Unknown"
    ]

    # tipo de ordem do callback TOrderChangeCallback
    _lst_tipo_ordem = [
        "Market", "Limit", "Stop", "StopLimit", "MarketOnClose", "WithOrWithout", "LimitOrBetter",
        "LimitWithOrWithout", "OnBasis", "OnClose", "LimitOnClose", "ForexMarket", "PreviouslyQuoted",
        "PreviouslyIndicated", "ForexLimit", "ForexSwap", "ForexPreviouslyQuoted", "Funari", "MarketIfTouched",
        "MarketWithLeftoverAsLimit", "PreviousFundValuationPoint", "Pegged", "Unknown"
    ]

    # Valores do Status das callbacks HistoryCallback e OrderChangeCallback.
    _dct_order_status = {
        0: 'New', 1: 'PartiallyFilled', 2: 'Filled', 3: 'DoneForDay', 4: 'Canceled', 5: 'Replaced',
        6: 'PendingCancel', 7: 'Stopped', 8: 'Rejected', 9: 'Suspended', 10: 'PendingNew',
        11: 'Calculated', 12: 'Expired', 13: 'AcceptedForBidding', 14: 'PendingReplace',
        15: 'PartiallyFilledCanceleds', 16: 'Received', 17: 'PartiallyFilledExpired', 200: 'Unknown',
        201: 'HadesCreated', 202: 'BrokerSent', 203: 'ClientCreated', 204: 'OrderNotCreated'
    }

    def __init__(self, config_prov: InternalConfigProviders):

        # here the instruments will be kept.
        self._config_prov = config_prov

        # memory pointers to every list of instruments.
        lst_instruments = self._config_prov.get_internal_provider_data("instruments")
        self._dct_quote = self._config_prov.get_internal_provider_data("quote", sublist=lst_instruments)
        self._dct_tt = self._config_prov.get_internal_provider_data("tt", sublist=lst_instruments)
        self._dct_lp = self._config_prov.get_internal_provider_data("lp", sublist=lst_instruments)
        self._dct_lp_tr = self._config_prov.get_internal_provider_data("lp_tr", sublist=lst_instruments)
        self._dct_lo = self._config_prov.get_internal_provider_data("lo", sublist=lst_instruments)
        self._dct_account = self._config_prov.get_internal_provider_data("account", sublist=lst_instruments)
        self._dct_orders = self._config_prov.get_internal_provider_data("orders", sublist=lst_instruments)
        self._dct_progress = self._config_prov.get_internal_provider_data("progress", sublist=lst_instruments)
        self._dct_spread = self._config_prov.get_internal_provider_data("spread", sublist=lst_instruments)
        self._dct_spread_rt = self._config_prov.get_internal_provider_data("spread_rt", sublist=lst_instruments)
        self._dct_ranking = self._config_prov.get_internal_provider_data("ranking", sublist=lst_instruments)

        self._b_ativo = False
        self._b_market_connected = False
        self._b_connectado = False
        self._b_broker_connected = False

    def __del__(self):
        if self.is_connected():
            self.disconnect()

    def connect(self):
        pass

    def disconnect(self):
        if self.is_connected():
            self._b_ativo = False
            self._b_market_connected = False
            self._b_connectado = False
            self._b_broker_connected = False

    def is_connected(self) -> bool:
        return self._b_market_connected

    def get_asset_state(self) -> dict:
        return self._dct_asset_state.copy()

    def get_dct_order_status(self) -> dict:
        return self._dct_order_status.copy()

    @staticmethod
    def get_dct_reversed(orig_dict: dict) -> dict:
        dct_dest = {}
        for k, v in orig_dict.items():
            dct_dest[v] = k

        return dct_dest

    # METHODS ------------------------------------------------------------------------------------------------------
    def subscribe_ticker(self, ticker: str, bolsa: str):
        pass

    def unsubscribe_ticker(self, ticker: str, bolsa: str):
        pass

    def subscribe_price_book(self, ticker: str, bolsa: str):
        pass

    def unsubscribe_price_book(self, ticker: str, bolsa: str):
        pass

    def subscribe_offer_book(self, ticker: str, bolsa: str):
        pass

    def unsubscribe_offer_book(self, ticker: str, bolsa: str):
        pass

    def get_agent_name_by_id(self, n_id: int):
        pass

    def get_agent_short_name_by_id(self, n_id: int):
        pass

    def send_buy_order(self, conta: str, broker: str, senha: str, ativo: str, bolsa: str, preco: float, qtd: int):
        pass

    def send_sell_order(self, conta: str, broker: str, senha: str, ativo: str, bolsa: str, preco: float, qtd: int):
        pass

    def send_stop_buy_order(self, conta: str, broker: str, senha: str, ativo: str, bolsa: str, preco: float,
                            s_stop_price: float, qtd: int):
        pass

    def send_stop_sell_order(self, conta: str, broker: str, senha: str, ativo: str, bolsa: str, preco: float,
                             s_stop_price: float, qtd: int):
        pass

    def send_change_order(self, conta: str, broker: str, senha: str, cl_ord_id: str, preco: float, qtd: int):
        pass

    def send_cancel_order(self, conta: str, broker: str, cl_ord_id: str, senha: str):
        pass

    def send_cancel_orders(self, conta: str, broker: str, senha: str, ativo: str, bolsa: str):
        pass

    def send_cancel_all_orders(self, conta: str, broker: str, senha: str):
        pass

    def send_zero_position(self, conta: str, broker: str, ativo: str, bolsa: str, senha: str, price: float):
        pass

    def get_account(self):
        pass

    def get_orders(self, conta: str, broker: str, dt_start: str, dt_end: str):
        pass

    def get_order(self, cl_ord_id: str):
        pass

    def get_order_profit_id(self, n_profit_id: int):
        pass

    def get_position(self, conta: str, broker: str, ativo: str, bolsa: str):
        pass

    def get_history_trades(self, ativo: str, bolsa: str, dt_start: str, dt_end: str):
        pass

    def get_serie_history(self, ativo: str, bolsa: str, dt_start: str, dt_end: str, n_quote_number_start: int,
                          n_quote_number_end: int):
        pass

    def set_day_trade(self, b_use_day_trade: bool):
        pass

    def set_enabled_log_to_debug(self, b_enabled: bool):
        pass

    def request_ticker_info(self, ticker: str, bolsa: str):
        pass

    def get_all_ticker(self, bolsa: str):
        pass

    def set_enabled_hist_order(self, b_enabled: bool):
        pass

    def subscribe_adjust_history(self, ativo: str, bolsa: str):
        pass

    def unsubscribe_adjust_history(self, ativo: str, bolsa: str):
        pass

    def set_server_and_port(self, server, port: str):
        pass

    def get_server_clock(self):
        pass

    def get_last_daily_close(self, ticker: str, bolsa: str, bol_val_adj=1):
        pass

    # CALLBACKS ----------------------------------------------------------------------------------------------------
    def change_cotation_callback(self, asset_id, date, trade_number, price):
        dct_quote = self._dct_quote.get(asset_id.ticker, {})
        if not dct_quote:
            self._dct_quote[asset_id.ticker] = dct_quote

        dct_quote["date"] = date
        dct_quote["last"] = price
        dct_quote["trade_number"] = trade_number

        # logger.debug(f"change_cotation_callback -> {dct_quote}")

    def asset_list_callback(self, asset_id, name):
        dct_quote = self._dct_quote.get(asset_id.ticker, {})
        if not dct_quote:
            self._dct_quote[asset_id.ticker] = dct_quote

        dct_quote["description"] = name

        # logger.debug(f"asset_list_callback -> {dct_quote}")

    def asset_list_info_callback(self, asset_id, name, description, min_order_qtd, max_order_qtd, lote,
                                 security_type,
                                 security_sub_type, min_price_increment, contract_multiplier, valid_date, isin):
        dct_quote = self._dct_quote.get(asset_id.ticker, {})
        if not dct_quote:
            self._dct_quote[asset_id.ticker] = dct_quote

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
        dct_quote["security_sub_type_desc"] = self._dct_asset_sec_sub_type.get(security_sub_type)

        # logger.debug(f"asset_list_info_callback -> {dct_quote}")

    def asset_list_info_callback_v2(self, asset_id, name, description, min_order_qtd, max_order_qtd, lote,
                                    security_type, security_sub_type, min_price_increment, contract_multiplier,
                                    valid_date, isin, setor, sub_setor, segmento):
        dct_quote = self._dct_quote.get(asset_id.ticker, {})
        if not dct_quote:
            self._dct_quote[asset_id.ticker] = dct_quote

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
        dct_quote["security_sub_type_desc"] = self._dct_asset_sec_sub_type.get(security_sub_type)

        # logger.debug(f"asset_list_info_callback_v2 -> {dct_quote}")

    def adjust_history_callback(self, asset_id, value, adj_type, observ, dt_ajuste, dt_delib, dt_pagamento,
                                aff_price):
        dct_quote = self._dct_quote.get(asset_id.ticker, {})
        if not dct_quote:
            self._dct_quote[asset_id.ticker] = dct_quote

        dct_quote["ajuste"] = value
        if aff_price:
            dct_quote["last"] = dct_quote.get("last", 0) + value

        # logger.debug(f"adjust_history_callback -> {dct_quote}")

    def adjust_history_callback_v2(self, asset_id, value, adj_type, observ, dt_ajuste, dt_delib, dt_pagamento,
                                   flags,
                                   mult):
        """
            nFlags é um campo de bits b0 a b31, onde o bit 0 indica se o ajuste afeta o preço e o bit 1 indica se é
            um ajuste de Soma.

            dMult é o valor pré-computado que deve ser multiplicado pelo preço para realizar o ajuste, somente é
            utilizado caso o ajuste não seja um ajuste de soma e seja um ajuste que afeta preço, informação
            fornecida no campo nFlags.

            O valor -9999 de dMult indica que o mesmo é inválido e não deve ser utilizado. Caso o valor dMult seja
            inválido, utiliza-se dValue para realizar o cálculo, sendo uma subtração em caso de ajuste de soma e
            divisão caso contrário.
        """
        dct_quote = self._dct_quote.get(asset_id.ticker, {})
        if not dct_quote:
            self._dct_quote[asset_id.ticker] = dct_quote

        dct_quote["ajuste"] = value
        str_flag = bin(flags)

        if str_flag[0] == 1:
            aj_soma = str_flag[1] == 1
            last_prc = dct_quote.get("last", 0)

            if mult != -9999:
                if aj_soma:
                    last_prc += value
                else:
                    last_prc *= mult
            else:
                if aj_soma:
                    last_prc -= value
                else:
                    last_prc /= value

            dct_quote["last"] = round(last_prc, 2)

        # logger.debug(f"adjust_history_callback_v2 -> {dct_quote}")

    def change_state_ticker_callback(self, asset_id, date, state):
        dct_quote = self._dct_quote.get(asset_id.ticker, {})
        if not dct_quote:
            self._dct_quote[asset_id.ticker] = dct_quote

        dct_quote["date"] = date
        dct_quote["state"] = state
        dct_quote["desc_state"] = self._dct_asset_state.get(state)

        # logger.debug(f"change_state_ticker_callback -> {dct_quote}")

    def price_book_callback(self, asset_id, action, position, side, qtd, count, price, array_sell, array_buy):
        pass

    def offer_book_callback(self, asset_id, action, position, side, qtd, agent, offer_id, price, has_price, has_qtd,
                            has_date, has_offer_id, has_agent, date, array_sell, array_buy):
        pass

    def set_theoretical_price_callback(self, asset_id, theoretical_price, theoretical_qtd):
        dct_quote = self._dct_quote.get(asset_id.ticker, {})
        if not dct_quote:
            self._dct_quote[asset_id.ticker] = dct_quote

        dct_quote["theoretical_price"] = theoretical_price
        dct_quote["theoretical_qtd"] = theoretical_qtd

        # logger.debug(f"set_theoretical_price_callback -> {dct_quote}")

    def state_callback(self, type_val, result):
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
                logger.info("Broker: Sem conexao com corretora.")
            else:
                self._b_broker_connected = False
                logger.info(f"Broker: Sem conexao com servidores ({str(result)}).")

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
                logger.info("Ativacao: OK.")
                self._b_ativo = True
            else:
                logger.info(f"Ativacao: {str(result)}.")
                self._b_ativo = False

        if self._b_market_connected and self._b_ativo and self._b_connectado:
            logger.info("Servicos Conectados.")

    def find_lim_ord_pos_book_offer(self, tipo_ordem, status, asset_id, side, price, date, cl_ord_id):
        if (tipo_ordem == "Limit" and status == "New") or (tipo_ordem == "Market" and status == "PartiallyFilled"):

            lst_book = self._dct_lo.get(asset_id.ticker, [])
            if not lst_book:
                return

            lst_side = lst_book[side]
            if not lst_side:
                return

            lst_prc = [prc for prc in lst_side if prc[0] == price]
            if lst_prc:
                lst_offers = list(filter(lambda x: x[4].decode("utf-8") == date, lst_prc))
                if not lst_offers:
                    dt_start = datetime.strptime(date, "%d/%m/%Y %H:%M:%S.%f")
                    dt_end = dt_start + timedelta(milliseconds=500)
                    dt_start = dt_start - timedelta(milliseconds=500)
                    lst_offers = list(filter(
                        lambda x: dt_start <= datetime.strptime(x[4].decode("utf-8"),
                                                                "%d/%m/%Y %H:%M:%S.%f") <= dt_end,
                        lst_prc))

                if lst_offers:
                    lst_offers[-1].append(cl_ord_id)

    def history_callback(self, asset_id, corretora, qtd, traded_qtd, leaves_qtd, side, price, stop_price, avg_price,
                         profit_id, tipo_ordem, conta, titular, cl_ord_id, status, date):

        # is called after any methods which send an order
        self.find_lim_ord_pos_book_offer(tipo_ordem, status, asset_id, side, price, date, cl_ord_id)

        dct = {
            "corretora": corretora, "qtd": qtd, "traded_qtd": traded_qtd, "leaves_qtd": leaves_qtd, "side": side,
            "price": price, "stop_price": stop_price, "avg_price": avg_price, "profit_id": profit_id,
            "tipo_ordem": tipo_ordem, "conta": conta, "titular": titular, "cl_ord_id": cl_ord_id, "status": status,
            "date": date, "symbol": asset_id.ticker
        }
        logger.debug(f"history_callback -> {dct}")

        lst_orders = self._dct_orders.get(asset_id.ticker, [])
        if not lst_orders:
            self._dct_orders[asset_id.ticker] = lst_orders

        order = None
        for ordr in lst_orders:
            if ordr.get("cl_ord_id") == cl_ord_id:
                order = ordr
                break

        if order is None:
            lst_orders.append({
                "corretora": corretora, "qtd": qtd, "traded_qtd": traded_qtd, "leaves_qtd": leaves_qtd,
                "side": side, "price": price, "stop_price": stop_price, "avg_price": avg_price, "profit_id": profit_id,
                "tipo_ordem": tipo_ordem, "conta": conta, "titular": titular, "cl_ord_id": cl_ord_id,
                "status": status, "date": date, "symbol": asset_id.ticker
            })
        else:
            order.update({
                "corretora": corretora, "qtd": qtd, "traded_qtd": traded_qtd, "leaves_qtd": leaves_qtd,
                "side": side, "price": price, "stop_price": stop_price, "avg_price": avg_price, "profit_id": profit_id,
                "tipo_ordem": tipo_ordem, "conta": conta, "titular": titular, "cl_ord_id": cl_ord_id,
                "status": status, "date": date
            })

    def progress_callback(self, asset_id, progress):
        dct_progress = self._dct_progress.get(asset_id.ticker, {})
        if not dct_progress:
            self._dct_progress[asset_id.ticker] = dct_progress

        dct_progress.update({"progress": progress})

    def history_trade_callback(self, asset_id, date, trade_number, price, vol, qtd, buy_agent, sell_agent,
                               trade_type):
        # See: self._dct_trade_type; trade_type = 2: Compra, 3: Venda, 4: Leilão, 12: On Behalf, 13:RLP.
        if trade_type in [2, 3, 4, 12, 13]:
            lst_tt = self._dct_tt.get(asset_id.ticker, [])
            if not lst_tt:
                self._dct_tt[asset_id.ticker] = lst_tt

            lst_tt.append([trade_number, date, price, qtd, buy_agent, sell_agent])

            # TODO: calcular o saldo da agressão total aqui e atualizar valor em dct_quote["saldo_agressao"]
            # TODO: calcular o saldo ranking (novo instrumento) com as seguintes informações:
            #  [time (a cada minuto), agente, qtd_acum, prc_medio, sd_agressao, sd_passivo]

    def order_change_callback(self, asset_id, corretora, qtd, traded_qtd, leaves_qtd, side, price, stop_price,
                              avg_price, profit_id, tipo_ordem, conta, titular, cl_ord_id, status, date,
                              text_message):

        # for GetOrder() and GetOrder()
        self.find_lim_ord_pos_book_offer(tipo_ordem, status, asset_id, side, price, date, cl_ord_id)

        dct = {
            "corretora": corretora, "qtd": qtd, "traded_qtd": traded_qtd, "leaves_qtd": leaves_qtd, "side": side,
            "price": price, "stop_price": stop_price, "avg_price": avg_price, "profit_id": profit_id,
            "tipo_ordem": tipo_ordem, "conta": conta, "titular": titular, "cl_ord_id": cl_ord_id, "status": status,
            "date": date, "text_message": text_message, "symbol": asset_id.ticker
        }
        logger.debug(f"order_change_callback -> {dct}")

        lst_orders = self._dct_orders.get(asset_id.ticker, [])
        if not lst_orders:
            self._dct_orders[asset_id.ticker] = lst_orders

        order = None
        for ordr in lst_orders:
            if ordr.get("cl_ord_id") == cl_ord_id:
                order = ordr
                break

        if order is None:
            lst_orders.append({
                "corretora": corretora, "qtd": qtd, "traded_qtd": traded_qtd, "leaves_qtd": leaves_qtd,
                "side": side, "price": price, "stop_price": stop_price, "avg_price": avg_price, "profit_id": profit_id,
                "tipo_ordem": tipo_ordem, "conta": conta, "titular": titular, "cl_ord_id": cl_ord_id,
                "status": status, "date": date, "text_message": text_message, "symbol": asset_id.ticker
            })
        else:
            order.update({
                "corretora": corretora, "qtd": qtd, "traded_qtd": traded_qtd, "leaves_qtd": leaves_qtd,
                "side": side, "price": price, "stop_price": stop_price, "avg_price": avg_price, "profit_id": profit_id,
                "tipo_ordem": tipo_ordem, "conta": conta, "titular": titular, "cl_ord_id": cl_ord_id,
                "status": status, "date": date, "text_message": text_message
            })

    def account_callback(self, corretora, corretora_nome_completo, account_id, nome_titular):
        dct_account = self._dct_account.get("Corretora", {})
        if not dct_account:
            self._dct_account[corretora] = dct_account

        dct_account.update({"corretora": corretora, "corretora_nome_completo": corretora_nome_completo,
                            "account_id": account_id, "nome_titular": nome_titular
                            })

    def new_trade_callback(self, asset_id, date, trade_number, price, vol, qtd, buy_agent, sell_agent, trade_type,
                           is_edit):
        # See: self._dct_trade_type; trade_type = 2: Compra, 3: Venda, 4: Leilão, 12: On Behalf, 13:RLP.
        if trade_type in [2, 3, 4, 12, 13]:
            lst_tt = self._dct_tt.get(asset_id.ticker, [])
            if not lst_tt:
                self._dct_tt[asset_id.ticker] = lst_tt

            lst_tt.append([trade_number, date, price, qtd, buy_agent, sell_agent])

            # TODO: calcular o saldo da agressão total aqui e atualizar valor em dct_quote["saldo_agressao"]
            # TODO: calcular o saldo ranking (novo instrumento) com as seguintes informações:
            #  [time (a cada minuto), agente, qtd_acum, prc_medio, sd_agressao, sd_passivo]

            # TODO: logica do TTOO.
            '''
            Para implementar a ordem original é só ir de negocio em negocio, se o agressor é o mesmo ele agrega
            se não for o mesmo ele para de agregar
            ele faz isso se for dentro do mesmo segundo
            se passar mais tempo ele nao agrega mais
            '''

    def tiny_book_callback(self, asset_id, price, qtd, side):
        lst_spread = self._dct_spread.get(asset_id.ticker, None)
        if not lst_spread:
            lst_spread = [None, None]
            self._dct_spread[asset_id.ticker] = lst_spread

        if not lst_spread[side]:
            lst_spread[side] = [qtd, price]
            return

        lst_spread[side][0] = qtd
        lst_spread[side][1] = price

    def new_daily_callback(self, asset_id, date, open_val, high, low, close, vol, ajuste, max_limit, min_limit,
                           vol_buyer, vol_seller, qtd, negocios, contratos_open, qtd_buyer, qtd_seller, neg_buyer,
                           neg_seller):
        dct_quote = self._dct_quote.get(asset_id.ticker, {})
        if not dct_quote:
            self._dct_quote[asset_id.ticker] = dct_quote

        dct_quote.update({"date": date, "open_val": open_val, "high": high, "low": low, "close": close, "vol": vol,
                          "ajuste": ajuste, "max_limit": max_limit, "min_limit": min_limit, "vol_buyer": vol_buyer,
                          "vol_seller": vol_seller, "qtd": qtd, "negocios": negocios,
                          "contratos_open": contratos_open,
                          "qtd_buyer": qtd_buyer, "qtd_seller": qtd_seller, "neg_buyer": neg_buyer,
                          "neg_seller": neg_seller
                          })

        # logger.debug(f"new_daily_callback -> {dct_quote}")
