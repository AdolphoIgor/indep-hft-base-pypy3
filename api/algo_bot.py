import datetime
import time as ttime
from concurrent.futures import ThreadPoolExecutor
from threading import Thread

from api.constants import Constants
from api.lft.start.opening import Opening
from api.lft.start.preopening import PreOpening
from api.lft.start.start import Start
from api.lft.stop.perc_trailing_stop import PercTrailingStop
from api.lft.stop.stop import Stop
from api.lft.stop.trailing_stop import TrailingStop


class Bot(Thread):
    _lst_cls = [PreOpening, Opening, TrailingStop, PercTrailingStop, datetime]

    def __init__(self, name=None, daemon=None, *args, **kwargs):
        super().__init__(name=name, daemon=daemon)
        self._keep_running = kwargs.get('keep_running', False)

    def stop(self):
        self._keep_running = False

    @staticmethod
    def _get_market_data(lst_started, symbol: str) -> dict:
        dct_start_cfg = None
        for itm in lst_started:
            if itm.get("symbol", None) == symbol:
                dct_start_cfg = itm
                break
        return dct_start_cfg

    @staticmethod
    def _get_oms_broker_provider(oms, broker_id: int) -> dict:
        provider = None
        for prov in oms:
            if prov.get("id", -1) == broker_id:
                provider = prov
                break

        return provider

    @staticmethod
    def _get_oms_thread_dct_orders(oms_broker_provider: dict, algo_name: str) -> dict:
        return oms_broker_provider.get("algo_msg_types").get(algo_name)

    @staticmethod
    def _get_oms_thread_dct_positions(oms_broker_provider: dict, algo_name: str):
        return oms_broker_provider.get("'algo_positions'").get(algo_name)

    @staticmethod
    def _execute_order(oms_broker_provider: dict, dtc_order: dict) -> dict:
        dct_msg = oms_broker_provider.get("cls_ptr").execute(dtc_order)
        return dct_msg

    def _execute_order_comp(self, oms, broker_id: int, dtc_order: dict) -> dict:
        provider = self._get_oms_broker_provider(oms, broker_id)
        dct_msg = provider.get("cls_ptr").execute(dtc_order)
        return dct_msg

    @staticmethod
    def _set_thr_position(algo_cfg, oms, thr, msg_ret):

        if msg_ret.get("Side") == 1:
            position = (msg_ret.get("LastPx", 0.0) - msg_ret.get("AvgPx", 0.0)) * msg_ret.get("CumQty", 0)
        else:
            position = (msg_ret.get("AvgPx", 0.0) - msg_ret.get("LastPx", 0.0)) * msg_ret.get("CumQty", 0)

        oms.get("positions", []).append(
            {
                "algo_id": algo_cfg.get("id", -1),
                "algo_name": algo_cfg.get("name", ""),
                "thread_symbol": thr.get("symbol", ""),
                "thread_oms_id": thr.get("oms_id", ""),
                "thread_broker_id": thr.get("broker_id", ""),
                "order_id": msg_ret.get("ClOrdID"),
                "side": "B" if msg_ret.get("Side") == 1 else "S",
                "symbol": msg_ret.get("Symbol"),
                "average_price": msg_ret.get("AvgPx"),
                "exec_qtt": msg_ret.get("CumQty"),
                "last_price": msg_ret.get("LastPx", 0.0),
                "position": position
            }
        )


class AlgoBot(Bot):
    """ This is the base class for every negotiation algorithm class. """

    _used_classes = [Start, Stop, PercTrailingStop, TrailingStop]

    def __init__(self, name=None, daemon=None, *args, **kwargs):
        super().__init__(name=name, daemon=daemon, *args, **kwargs)
        self._state = Constants.POSITION_NEW
        self._algo_cfg = kwargs.get('algo_cfg', {})
        self._lst_oms = [thr.get("oms_instance", []) for thr in self._algo_cfg.get("threads")]
        self._shutdown = False

    def tick(self):
        """
            Defines what is going to happen when a tick is triggered.
        """
        lst_started = []
        if self._state == Constants.POSITION_NEW:
            while self._keep_running:
                for thr in self._algo_cfg.get("threads", []):
                    dct_inst = None
                    for inst in thr.get("market_data_instance", {}).get('instruments', []):
                        if inst.get("type") == 'T' and inst.get('registered'):
                            dct_inst = inst.get('instrument', None)
                            break

                    if dct_inst is None or len(dct_inst) == 0:
                        continue

                    evl_str = f'{thr.get("start_class")}(' \
                              f'mkt_dt={thr.get("market_data_instance", None)}, ' \
                              f'side="{thr.get("start_parameters", {}).get("side")}"' \
                              f')'
                    lst_res = eval(evl_str).start()
                    lst_res.append(thr)
                    lst_started.append(lst_res)

                if len(lst_started) > 0 and all([item[0].get("opened") for item in lst_started]):
                    break

            if self._keep_running:
                with ThreadPoolExecutor(max_workers=8) as executor:
                    for item in lst_started:
                        executor.submit(self._create_position, item[0], item[1], self._lst_oms)

                self._state = Constants.POSITION_OPENED

        elif self._state == Constants.POSITION_OPENED:
            evl_str = f'{self._algo_cfg.get("stop_class")}(**{self._algo_cfg.get("stop_parameters", {})})'
            evl_ptr = eval(evl_str)

            while self._keep_running:
                g_position = 0.0
                for thr in self._algo_cfg.get("threads", []):

                    sel_inst = None
                    for inst in thr.get("market_data_instance", None).get("instruments"):
                        if inst.get("type", "") == "T":
                            sel_inst = inst.get("instrument", {})
                            break

                    oms_provider = self._get_oms_broker_provider(self._lst_oms, thr.get("broker_id", -1))
                    dct_broker_position = self._get_oms_thread_dct_positions(oms_provider, self._algo_cfg.get("name"))

                    dct_broker_position["last_price"] = sel_inst.get("Ultimo", 0.0)

                    if dct_broker_position.get("Side") == 1:
                        position = (sel_inst.get("Ultimo", 0.0) - dct_broker_position.get("AvgPx", 0.0)) * \
                                   dct_broker_position.get("CumQty", 0)
                    else:
                        position = (dct_broker_position.get("AvgPx", 0.0) - sel_inst.get("Ultimo", 0.0)) * \
                                   dct_broker_position.get("CumQty", 0)

                    dct_broker_position["position"] = position
                    g_position = g_position + position

                if evl_ptr.stop({"position": g_position}):
                    break

            with ThreadPoolExecutor(max_workers=8) as executor:
                for item in lst_started:
                    executor.submit(self._create_position, item[0], item[1], self._lst_oms)

            self._state = Constants.POSITION_STOPED

    '''
    --------------------------------------------------------------------------------------------------------------------
    Getting the order ready.
        Fields setted with defaults configuration will return fullfield right now but fields setted with calculated 
        configuration, will be fullfield right before que order be sent. 
        Every other kind of fields must have their values changed right here.
    --------------------------------------------------------------------------------------------------------------------
        ----------------------------------------------------------------------------------------------------------------
        ORDERS TYPES:
        ----------------------------------------------------------------------------------------------------------------
        MsgType = 8 - Execution Report.
        MsgType = D - New Single Order.
        MsgType = 3 - Reject.
        MsgType = G - Order Cancel/Replace.
        MsgType = F - Order Cancel Request.
        MsgType = 9 - Order Cancel Reject.
        
        ----------------------------------------------------------------------------------------------------------------
        ORDERS FLOW:
        ----------------------------------------------------------------------------------------------------------------
        MsgType=D + (OrdType=2 - Limite): 
            |--> MsgType=3 --> END.
            |
            |--> MsgType=8 --> ExecType=R - Received + (UMA DAS MSGS ABAIXO):
                    |      /--> ExecType=A = Pending New (Pendente – resultado de envio de nova ordem com mercado 
                    |-----E/OU                 ainda fechado para negociação) - Se em Leilão;
                           \--> ExecType=0 = New (Nova) - em fila.
                           
        --- 
                           
        MsgType=D + (OrdType=K = Market with leftover as limit): 
            |--> MsgType=3 --> END.
            |
            |--> MsgType=8 --> ExecType=R - Received + (UMA DAS MSGS ABAIXO):
                    |      /--> ExecType=1 - Partial (Parcialmente Executada) ... --> ExecType=1 - Partial ...
                    |-----E/OU                 
                           \--> ExecType=2 - Filled (Completamente Executada)  
  

        ----------------------------------------------------------------------------------------------------------------
        ExecType (execution report):
        ----------------------------------------------------------------------------------------------------------------
        0 = New (Nova)
        1 = Partial (Parcialmente Executada)
        2 = Filled (Completamente Executada)
        4 = Canceled (Cancelamento)
        5 = Replaced (Edição)
        6 = Pending Cancel (Cancelamento Pendente, resultado de Order Cancel Request(MsgType = F) e que ainda não 
            recebeu confirmação do mercado)
        8 = Rejected (Rejeição)
        9 = Suspended
        A = Pending New (Pendente – resultado de envio de nova ordem com mercado ainda fechado para negociação)
        C = Expired (Expiração)
        D = Restated (Reconfirmação)
        E = Pending Replace (Edição ainda não confirmada pelo mercado)
        F = Trade (Negócio)
        H = Canceled (Negócio)
        I = Order Status (Status de Ordem – Resultado de uma mensagem de Order Mass Status Request(MsgType=AF))
        R = Received by OMS
        L = Triggered
        
        ----------------------------------------------------------------------------------------------------------------
        OrdStatus(execution report):
        ----------------------------------------------------------------------------------------------------------------
        0 = New (Recebida)
        1 = Partially Filled (Parcialmente Executada)
        2 = Filled (Completamente Executada)
        4 = Canceled (Cancelada)
        5 = Replaced (Editada)
        6 = Pending Cancel (Cancelamento Pendente)
        8 = Rejected (Rejeitada)
        9 = Suspended
        A = Pending New (Pendente - esperando abertura do mercado para ser enviada)
        C = Expired (Expirada)
        E = Pending Replace (Esperando Edição)
        R = Received

        ----------------------------------------------------------------------------------------------------------------
        CxlRejReason = Código que identifica o motivo de rejeição. 
        ----------------------------------------------------------------------------------------------------------------
        370 = Muito tarde para ser cancelada
        1 = Ordem desconhecida
        2 = Broker Option
        3 = Order already in Pending Cancel.
        99 = Outro                         

        ----------------------------------------------------------------------------------------------------------------
        CxlRejResponseTo: Identifica o tipo de requisição que gerou essa mensagem de rejeição.
        ----------------------------------------------------------------------------------------------------------------
        1 = Order Cancel Request
        2 = Order Cancel/Replace Request

        ----------------------------------------------------------------------------------------------------------------
        CxlRejSource: Local em que a mensagem esta sendo rejeitada.
        ----------------------------------------------------------------------------------------------------------------
        2 = Crystal Broker (OMS)
        3 = BOVESPA
        4 = ManagedOrderAdmin

        ----------------------------------------------------------------------------------------------------------------
        ExecRestatementReason: Indica o motivo do cancelamento da ordem
        ----------------------------------------------------------------------------------------------------------------
        103 = cancelamento da oferta agressora
        107 = cancelamento da oferta agredida
        203 = cancelamento da oferta conforme solicitação do participante (sem considerar erro operacional da bolsa) 
        204 = cancelamento da oferta por erro operacional da bolsa
        205 = cancelamento da oferta via Firmsoft (conforme solicitação do participante e sem considerar erro 
              operacional da bolsa)
        206 = cancelamento da oferta via Firmsoft (por erro operacional da bolsa)
        
        ----------------------------------------------------------------------------------------------------------------
        OrdRejReason: Código que identifica o motivo de rejeição da ordem
        ----------------------------------------------------------------------------------------------------------------
        0 = Opção do servidor 
        1 = Símbolo Desconhecido
        2 = Pregão fechado
        3 = Ordem excedeu limite
        4 = Tarde demais para entrar
        5 = Ordem desconhecida
        6 = Ordem duplicada (e.g. ClOrdID duplicado)
        7 = Duplicate of a verbally communicated order
        8 = Stale Order
        11 = Característica da ordem não suportada
        13 = Quantidade incorreta
        15 = Conta desconhecida
        99 = Outro (erro genérico, ver campo Text para mais informações)

        ----------------------------------------------------------------------------------------------------------------
        Text:
        ----------------------------------------------------------------------------------------------------------------
        Descrição do erro no caso de CxlRejReason 99 = (Outro).
        
        ----------------------------------------------------------------------------------------------------------------
        OrdType: Tipo da ordem
        ----------------------------------------------------------------------------------------------------------------
        A = OnClose
        1 = Mercado + cancela o que sobrar (Deprecated)
        2 = Limite
        4 = Stop Limit
        K = Market with leftover as limit (deixa saldo na fila do que sobrar)
        S = Start

    '''

    def _create_position(self, dct_start_cfg: dict, thr: dict, oms) -> dict:
        """
        param dct_start_cfg:
        :param thr:
        :param oms:
        :return:
        """
        ''' msg_type="D"
            {
                "BeginString": "will be calculated",
                "BodyLength": "will be calculated",
                "MsgType": "D",
                "MsgSeqNum": "will be calculated",
                "PossDupFlag": "Not required <class 'bool'>",
                "SenderCompID": "will be calculated",
                "TargetCompID": "CRYSTAL_BROKER",
                "SenderSubID": "will be calculated",
                "SendingTime": "will be calculated",
                "PossResend": "Not required bool",
                "ClOrdID": "will be calculated",
                "ClOrdLinkID": "Not required <class 'str'>",
                "Symbol": "Not required <class 'str'>",
                "SecurityID": "Not required <class 'str'>",
                "SecurityIDSource": "Not required <class 'str'>",
                "SecurityExchange": "Not required <class 'str'>",
                "MaturityDate": "Not required datetime.strptime('{0}', '%Y%m%d-%H%M%S %f').time()",
                "Issuing": "Not required <class 'str'>",
                "ApplicationDays": "Not required <class 'int'>",
                "RewardDescription": "Not required <class 'str'>",
                "AvailableQuantity": "Not required <class 'int'>",
                "UnitPrice": "Not required <class 'float'>",
                "AvailablePrice": "Not required <class 'float'>",
                "MinimumApplicationPrice": "Not required <class 'float'>",
                "TradedRate": "Not required <class 'float'>",
                "TradedRateT": "Not required <class 'float'>",
                "IssuanceDate": "Not required datetime.strptime('{0}', '%Y%m%d-%H%M%S %f').time()",
                "LiquidityDate": "Not required datetime.strptime('{0}', '%Y%m%d-%H%M%S %f').time()",
                "SecurityIndex": "Not required <class 'str'>",
                "PercentIndex": "Not required <class 'float'>",
                "IssuanceRate": "Not required <class 'float'>",
                "Side": "Not required <class 'str'>",
                "OrderQty": "Not required <class 'int'>",
                "MinQty": "Not required <class 'int'>",
                "MaxFloor": "Not required <class 'int'>",
                "OrdType": "Not required <class 'str'>",
                "OrderRestrictions": "Not required <class 'str'>",
                "Price": "Not required <class 'float'>",
                "StopPx": "Not required <class 'float'>",
                "StopGainPx": "Not required <class 'float'>",
                "Price2": "Not required <class 'float'>",
                "MovingStart": "Not required <class 'float'>",
                "InitialChangeType": "Not required <class 'int'>",
                "InitialChange": "Not required <class 'int'>",
                "PricePercentage": "Not required <class 'float'>",
                "TimeInForce": "Not required <class 'str'>",
                "BrokerID": "Not required <class 'str'>",
                "NoAllocs": "Not required <class 'str'>",
                "AllocAccount": "Not required <class 'str'>",
                "AllocAcctIDSource": "Not required <class 'int'>",
                "NoPartyID": "Not required <class 'int'>",
                "PartyID": "will be calculated",
                "PartyIDSource": "D",
                "PartyRole": "Not required <class 'int'>",
                "TransactTime": "will be calculated",
                "PositionEffect": "Not required <class 'str'>",
                "TradeAllocIndicator": "Not required <class 'int'>",
                "OrderStrategy": "Not required <class 'str'>",
                "HandlInst": "Not required <class 'str'>",
                "OrderTag": "Not required <class 'str'>",
                "TargetStrategy": "Not required <class 'int'>",
                "TargetStrategyParameters": "Not required <class 'str'>",
                "SourceAddress": "will be calculated",
                "IsStopToMarket": "Not required <class 'str'>",
                "FullFilled": "Not required <class 'bool'>",
                "NoLegs": "Not required <class 'int'>",
                "PegOffsetType": "Not required <class 'int'>",
                "OrderPercent": "Not required <class 'float'>",
                "PegOffsetValue": "Not required <class 'float'>",
                "SignatureLength": "will be calculated",
                "Signature": "will be calculated",
                "CheckSum": "will be calculated"
            }
        '''

        def prep_exec_at_market(i_dct_st_cfg, i_start_params, i_dtc_order) -> float:
            sprd = round(i_dct_st_cfg.get("price") * i_start_params.get("perc_spread_order_at_market", 0.0), 2)
            return i_dct_st_cfg.get("price") + sprd if i_dtc_order['Side'] == 1 else i_dct_st_cfg.get("price") - sprd

        # Return every sent msg before a given message.
        def find_prev_sent_order(actual_msg: dict) -> list:
            # list containing every subsequent order after que original one.
            lst_sent = []
            for sent in orders.get("sent", []):
                if dct_msg.__ne__(sent):
                    if sent.get("TransactTime") > actual_msg.get("TransactTime"):
                        lst_sent.append(sent)

            return lst_sent

        basic_prov = thr.get("oms_instance").get("global_provider_decoder", None)
        start_params = thr.get("start_parameters", {})

        dtc_order = self._create_position_order(basic_prov, thr)
        dtc_order['Price'] = prep_exec_at_market(dct_start_cfg, start_params, dtc_order)

        oms_provider = self._get_oms_broker_provider(oms, thr.get("broker_id", -1))
        orders = self._get_oms_thread_dct_orders(oms_provider, self._algo_cfg.get("name"))
        dct_msg = self._execute_order(oms_provider, dtc_order)

        lst_processed = []
        msg_ret = None
        while msg_ret is None:

            lst_received = []
            for rec in orders.get("received", []):
                if rec.get("TransactTime") not in lst_processed:
                    lst_received.append((rec.get("TransactTime"), rec))

            lst_received = sorted(lst_received, key=lambda x: x[0])

            for rec in lst_received:
                if rec[1].get("MsgType", "") == "8" and \
                        ((dct_msg.get("ClOrdID") == rec[1].get("ClOrdID")) or
                         (dct_msg.get("ClOrdID") == rec[1].get("OrigClOrdID"))):

                    # if this or any other thread got a rejected msg this will stop every thread for the robot.
                    if rec[1].get("ExecType") == '8' and rec[1].get("OrdStatus") == '8' and \
                            rec[1].get("OrdRejReason") not in [4, 6, 7]:
                        self._shutdown = True

                    if not self._shutdown:
                        # if the order came back totally executed.
                        if rec[1].get("ExecType") in ['2', 'F'] and rec[1].get("OrdStatus") == '2':
                            msg_ret = rec[1]
                            break

                        # if the order came back partially executed.
                        if rec[1].get("ExecType") in ['1', 'F'] and rec[1].get("OrdStatus") == '1':
                            price = prep_exec_at_market(dct_start_cfg, start_params, dtc_order)
                            dtc_alt_order = self._edit_pending_order(basic_prov, dct_msg, price)
                            self._execute_order(oms_provider, dtc_alt_order)
                            lst_processed.append(rec[0])

                        # if the order came back rejected because the partial order was completely executed right
                        # before it was changed and submitted from here (which turn this order invalid).
                        if rec[1].get("ExecType") == '8' and rec[1].get("OrdStatus") == '8' and \
                                rec[1].get("OrdRejReason") in [4, 6, 7]:
                            lst_processed.append(rec[0])

                    else:
                        # if the order came back rejected.
                        if rec[1].get("ExecType") == '8' and rec[1].get("OrdStatus") == '8' and \
                                rec[1].get("OrdRejReason") not in [4, 6, 7]:
                            msg_ret = rec[1]
                            break

                        # if the order wasn't executed or was partially executed.
                        lst_not_exec = ['0', '1', '5', 'A', 'E', 'R']
                        if rec[1].get("ExecType") in lst_not_exec and rec[1].get("OrdStatus") in lst_not_exec:

                            dtc_alt_order = self._cancel_pending_order(basic_prov, dct_msg)
                            self._execute_order(oms_provider, dtc_alt_order)

                            if rec[0] not in lst_processed:
                                lst_processed.append(rec[0])

                        lst_prev_order = find_prev_sent_order(rec[1])

                        # if the order came back partially executed or totally executed.
                        if (rec[1].get("ExecType") in ['1', 'F'] and rec[1].get("OrdStatus") == '1') or \
                                (rec[1].get("ExecType") in ['2', 'F'] and rec[1].get("OrdStatus") == '2'):

                            # the original order was completelly executed and this one too
                            msg = lst_prev_order[-1]
                            if msg.get("MsgType") == "D" and msg.get('Side') != rec[1].get('Side') and \
                                    msg.get('OrderQty') == rec[1].get('OrderQty') and \
                                    msg.get('Price') == rec[1].get('Price'):
                                msg_ret = rec[1]
                                break

                            dtc_alt_order = self._create_position_order(basic_prov, thr)
                            dtc_alt_order['Side'] = 2 if rec[1].get('Side') == 1 else 1
                            dtc_alt_order['OrderQty'] = rec[1].get("CumQty")
                            dtc_alt_order['Price'] = prep_exec_at_market(dct_start_cfg, start_params, rec)

                            self._execute_order(oms_provider, dtc_alt_order)

                            if rec[0] not in lst_processed:
                                lst_processed.append(rec[0])

                        # if the order came back canceled and the one of the lastest msg was to cancel...
                        if rec[1].get("ExecType") == '4' and rec[1].get("OrdStatus") == '4':

                            # if the last sent order was a cancel order.
                            msg = lst_prev_order[-1]
                            if msg.get("MsgType") == "F":
                                msg_ret = rec[1]
                                break
                            else:
                                lst_processed.append(rec[0])

                            if msg_ret is not None:
                                break

            if msg_ret is not None:
                break

            ttime.sleep(0.001)

        self._set_thr_position(self._algo_cfg, oms, thr, msg_ret)

        return msg_ret

    @staticmethod
    def _edit_pending_order(basic_prov, msg, price) -> dict:
        """

        :return:
        """
        ''' msg_type="G"
            {
                "BeginString": "will be calculated",
                "BodyLength": "will be calculated",
                "MsgType": "G",
                "MsgSeqNum": "will be calculated",
                "PossDupFlag": "Not required <class bool>",
                "SenderCompID": "will be calculated",
                "TargetCompID": "CRYSTAL_BROKER",
                "SenderSubID": "will be calculated",
                "SendingTime": "will be calculated",
                "PossResend": "Not required bool",
                "OrigClOrdID": "Not required <class str>",
                "OrderID": "Not required <class str>",
                "Symbol": "Not required <class str>",
                "SecurityID": "Not required <class str>",
                "SecurityIDSource": "Not required <class str>",
                "SecurityExchange": "Not required <class str>",
                "MaturityDate": "Not required datetime.time()",
                "Issuing": "Not required <class str>",
                "ApplicationDays": "Not required <class int>",
                "RewardDescription": "Not required <class str>",
                "AvailableQuantity": "Not required <class int>",
                "UnitPrice": "Not required <class float>",
                "AvailablePrice": "Not required <class float>",
                "MinimumApplicationPrice": "Not required <class float>",
                "TradedRate": "Not required <class float>",
                "TradedRateT": "Not required <class float>",
                "IssuanceDate": "Not required datetime.time()",
                "LiquidityDate": "Not required datetime.time()",
                "SecurityIndex": "Not required <class str>",
                "PercentIndex": "Not required <class float>",
                "IssuanceRate": "Not required <class float>",
                "ClOrdID": "will be calculated",
                "Side": "Not required <class str>",
                "OrderQty": "Not required <class int>",
                "MaxFloor": "Not required <class int>",
                "OrdType": "Not required <class str>",
                "OrderRestrictions": "Not required <class str>",
                "Price": "Not required <class float>",
                "StopPx": "Not required <class float>",
                "StopGainPx": "Not required <class float>",
                "Price2": "Not required <class float>",
                "MovingStart": "Not required <class float>",
                "InitialChangeType": "Not required <class int>",
                "InitialChange": "Not required <class float>",
                "PricePercentage": "Not required <class float>",
                "NoAllocs": "Not required <class int>",
                "AllocAccount": "Not required <class str>",
                "AllocAcctIDSource": "Not required <class int>",
                "NoPartyID": "Not required <class int>",
                "PartyID": "Not required <class str>",
                "PartyIDSource": "Not required <class str>",
                "PartyRole": "Not required <class int>",
                "HandlInst": "Not required <class str>",
                "TransactTime": "will be calculated",
                "OrderTag": "Not required <class str>",
                "TargetStrategy": "Not required <class int>",
                "TargetStrategyParameters": "Not required <class str>",
                "SourceAddress": "will be calculated",
                "SignatureLength": "will be calculated",
                "Signature": "will be calculated",
                "CheckSum": "will be calculated"
            }
        '''

        dtc_alt_order = basic_prov.get_template("G", [])
        dtc_alt_order['OrigClOrdID'] = msg.get("ClOrdID")
        dtc_alt_order['OrdType'] = 'K'

        dtc_alt_order['OrderQty'] = msg.get("LeavesQty")
        dtc_alt_order['Price'] = price

        return dtc_alt_order

    @staticmethod
    def _cancel_pending_order(basic_prov, msg) -> dict:
        """

        :return:
        """
        '''  
            MsgType = F      
            {
                "BeginString": "will be calculated",
                "BodyLength": "will be calculated",
                "MsgType": "F",
                "MsgSeqNum": "will be calculated",
                "PossDupFlag": "Not required <class bool>",
                "SenderCompID": "will be calculated",
                "TargetCompID": "CRYSTAL_BROKER",
                "SenderSubID": "will be calculated",
                "SendingTime": "will be calculated",
                "PossResend": "Not required bool",
                "OrigClOrdID": "Not required <class str>",
                "OrderID": "Not required <class str>",
                "Symbol": "Not required <class str>",
                "SecurityID": "Not required <class str>",
                "SecurityIDSource": "Not required <class str>",
                "SecurityExchange": "Not required <class str>",
                "MaturityDate": "Not required datetime.time()",
                "Issuing": "Not required <class str>",
                "ApplicationDays": "Not required <class int>",
                "RewardDescription": "Not required <class str>",
                "AvailableQuantity": "Not required <class int>",
                "UnitPrice": "Not required <class float>",
                "AvailablePrice": "Not required <class float>",
                "MinimumApplicationPrice": "Not required <class float>",
                "TradedRate": "Not required <class float>",
                "TradedRateT": "Not required <class float>",
                "IssuanceDate": "Not required datetime.time()",
                "LiquidityDate": "Not required datetime.time()",
                "SecurityIndex": "Not required <class str>",
                "PercentIndex": "Not required <class float>",
                "IssuanceRate": "Not required <class float>",
                "ClOrdID": "will be calculated",
                "Side": "Not required <class str>",
                "OrderRestrictions": "Not required <class str>",
                "OrderQty": "Not required <class int>",
                "NoPartyID": "Not required <class int>",
                "PartyID": "Not required <class str>",
                "PartyIDSource": "Not required <class str>",
                "PartyRole": "Not required <class int>",
                "HandlInst": "Not required <class str>",
                "TransactTime": "will be calculated",
                "OrderTag": "Not required <class str>",
                "TargetStrategy": "Not required <class int>",
                "TargetStrategyParameters": "Not required <class str>",
                "SignatureLength": "will be calculated",
                "Signature": "will be calculated",
                "CheckSum": "will be calculated"
            }
        '''
        dtc_alt_order = basic_prov.get_template("F", [])
        dtc_alt_order['OrigClOrdID'] = msg.get("ClOrdID")
        dtc_alt_order['NoPartyID'] = 1
        dtc_alt_order['PartyRole'] = 36
        dtc_alt_order['AllocAccount'] = msg.get("broker_id", -1)

        dtc_alt_order['Side'] = 2 if msg.get("side", None) == "B" else 1
        dtc_alt_order['OrderQty'] = msg.get("OrderQty") if msg.get("CumQty") == 0 else msg.get("CumQty")

        return dtc_alt_order

    @staticmethod
    def _create_position_order(basic_prov, thr) -> dict:
        """

        :return:
        """
        dct_order = basic_prov.get_template("D", [])
        dct_order['Symbol'] = thr.get("symbol", None)
        dct_order['SecurityID'] = thr.get("symbol", None)
        dct_order['OrdType'] = 'K'
        dct_order['NoPartyID'] = 1
        dct_order['PartyRole'] = 36
        dct_order['AllocAccount'] = thr.get("broker_id", -1)

        start_params = thr.get("start_parameters", {})
        dct_order['Side'] = 1 if start_params.get("side", None) == "B" else 2
        dct_order['OrderQty'] = start_params.get("order_qty", None)

        return dct_order
