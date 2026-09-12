import datetime
import time as ttime
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Thread

from api.constants import Constants
from api.lft.start.opening import Opening
from api.lft.start.preopening import PreOpening
from api.lft.start.start import Start
from api.lft.stop.perc_trailing_stop import PercTrailingStop
from api.lft.stop.stop import Stop
from api.lft.stop.trailing_stop import TrailingStop


class Bot(Thread):
    _used_classes = [Start, Stop, PercTrailingStop, TrailingStop, PreOpening, Opening, datetime]

    def __init__(self, name=None, daemon=None, *args, **kwargs):
        super().__init__(name=name, daemon=daemon)
        self._keep_running = kwargs.get('keep_running', False)
        self._algo_cfg = kwargs.get('algo_cfg', {})

    def stop(self):
        self._keep_running = False

    @staticmethod
    def _edit_pending_order(basic_prov, msg, ord_type='K', price=0) -> dict:
        dtc_alt_order = basic_prov.get_template("G", [])
        dtc_alt_order['OrigClOrdID'] = msg.get("ClOrdID")
        dtc_alt_order['OrdType'] = ord_type
        if ord_type != 'K':
            dtc_alt_order['Price'] = price
        dtc_alt_order['OrderQty'] = msg.get("LeavesQty")
        dtc_alt_order['Side'] = msg.get("Side")

        return dtc_alt_order

    @staticmethod
    def _cancel_pending_order(basic_prov, msg, thr) -> dict:
        dtc_alt_order = basic_prov.get_template("F", [])
        dtc_alt_order['OrigClOrdID'] = msg.get("ClOrdID")
        dtc_alt_order['NoPartyID'] = 1
        dtc_alt_order['AllocAccount'] = thr.get("broker_id", -1)
        dtc_alt_order['Side'] = msg.get("Side")
        dtc_alt_order['OrderQty'] = msg.get("LeavesQty")

        return dtc_alt_order

    @staticmethod
    def _create_position_order(basic_prov, thr, oms_provider, ord_type='K', price=0) -> dict:
        dct_order = basic_prov.get_template("D", [])
        dct_order['Symbol'] = thr.get("symbol", None)
        dct_order['SecurityID'] = thr.get("symbol", None)
        dct_order['OrdType'] = ord_type
        if ord_type != 'K':
            dct_order['Price'] = price
        dct_order['NoPartyID'] = 1
        dct_order['PartyID'] = oms_provider.get("sender_comp_id")
        dct_order['AllocAccount'] = thr.get("broker_id", -1)
        start_params = thr.get("start_parameters", {})
        dct_order['Side'] = 1 if start_params.get("side", None) == "B" else 2
        dct_order['OrderQty'] = start_params.get("order_qty", None)

        return dct_order

    @staticmethod
    def _request_for_positions(basic_prov) -> dict:
        dtc_alt_order = basic_prov.get_template("AN", [])
        dtc_alt_order['PosReqID'] = basic_prov
        dtc_alt_order['SubscriptionRequestType'] = basic_prov
        dtc_alt_order['OpenQtyFilter'] = basic_prov
        dtc_alt_order['PartyID'] = basic_prov
        dtc_alt_order['Account'] = basic_prov
        dtc_alt_order['MarketID'] = basic_prov
        dtc_alt_order['ClearingBusinessDate'] = basic_prov
        dtc_alt_order['FilterType'] = basic_prov
        return dtc_alt_order


class AlgoBot(Bot):
    """ This is the base class for every negotiation algorithm class. """

    def __init__(self, name=None, daemon=None, *args, **kwargs):
        super().__init__(name=name, daemon=daemon, *args, **kwargs)
        self._state = Constants.POSITION_NEW
        self._has_rejection = False

    def tick(self) -> bool:
        """
            Defines what is going to happen when a tick is triggered.
        """
        lst_started = []
        if self._state == Constants.POSITION_NEW:
            lst_threads = self._algo_cfg.get("threads", [])
            while self._keep_running:
                for thr in lst_threads:
                    dct_inst = None

                    if thr.get("symbol") in [itm.get("symbol") for item in lst_started for itm in item]:
                        continue

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

                if len(lst_threads) == len(lst_started) and all([item[0].get("opened") for item in lst_started]):
                    break

            while self._keep_running:
                lst_errors = []
                with ThreadPoolExecutor(max_workers=8) as executor:
                    lst_thr = [executor.submit(self._create_position, item[0], item[1])
                               for item in lst_started]

                    for future in as_completed(lst_thr):
                        lst_errors.append(not (future.exception() is not None or self._has_rejection))

                # if everything went right, requests the position report, change the status and exits.
                if len(lst_errors) > 0 and all(lst_errors):
                    with ThreadPoolExecutor(max_workers=8) as executor:
                        [executor.submit(self._request_position, item[1]) for item in lst_started]

                    self._state = Constants.POSITION_OPENED
                    break

                # but if there were at least one rejection during execution, must revert the entire operarion and exits.
                if len(lst_errors) > 0 and any(lst_errors):

                    # TODO: Filtrar a lista pela operaçao que foi executadacorretamente (ela e que tem que ser desfeita)
                    self._has_rejection = False
                    lst_errors.clear()
                    with ThreadPoolExecutor(max_workers=8) as executor:
                        lst_thr = [executor.submit(self._reject_position, item[1])
                                   for item in lst_started]

                        for future in as_completed(lst_thr):
                            lst_errors.append(future.exception() is None or not self._has_rejection)

                if len(lst_errors) > 0 and not all(lst_errors):
                    self._state = Constants.POSITION_REJECTED
                    break

        if self._state == Constants.POSITION_OPENED:
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

                    dct_broker_position = thr.get("oms_instance").get("algo_positions").get(self._algo_cfg.get("name"))
                    dct_broker_position["last_price"] = sel_inst.get("Ultimo", 0.0)

                    if dct_broker_position.get("Side") == 1:
                        position = (sel_inst.get("Ultimo", 0.0) - dct_broker_position.get("AvgPx", 0.0)) * \
                                   dct_broker_position.get("CumQty", 0)
                    else:
                        position = (dct_broker_position.get("AvgPx", 0.0) - sel_inst.get("Ultimo", 0.0)) * \
                                   dct_broker_position.get("CumQty", 0)

                    dct_broker_position["position"] = position
                    g_position = g_position + position

                if evl_ptr.stop_running({"position": g_position}):
                    break

            lst_errors = []
            with ThreadPoolExecutor(max_workers=8) as executor:
                lst_thr = [executor.submit(self._create_position, item[0], item[1])
                           for item in lst_started]

                for future in as_completed(lst_thr):
                    lst_errors.append(future.exception() is None)

            if len(lst_errors) > 0 and all(lst_errors):
                self._state = Constants.POSITION_STOPED

        if self._state in [Constants.POSITION_REJECTED, Constants.POSITION_STOPED]:
            return False
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

    def _create_position(self, dct_start_cfg: dict, thr: dict):
        oms_provider = thr.get("oms_instance")
        basic_prov = oms_provider.get("global_provider_conn", None)

        dct_order = self._create_position_order(basic_prov, thr, oms_provider)
        if not dct_order.get('OrdType') == 'K':
            dct_order['Price'] = dct_start_cfg.get("price")

        algo_name = f"{self._algo_cfg.get('name')}-{thr.get('oms_id')}-{thr.get('symbol')}"
        dct_msg = basic_prov.execute(**{**{"algo_name": algo_name}, **dct_order})

        keep_running = True
        while keep_running:
            # will stop_running another threads if just one of them had a rejection
            if self._has_rejection:
                break

            lst_received = [rec for rec in oms_provider.get("algo_msg_types", {}).get(algo_name, [])
                            if dct_msg.get("MsgType") == "D" and rec.get("MsgType") == "8" and
                            dct_msg.get("ClOrdID") in [rec.get("ClOrdID"), rec.get("OrigClOrdID")]]

            if not lst_received:
                ttime.sleep(0.001)
                continue

            lst_received = sorted(lst_received, key=lambda x: x.get("TransactTime"))
            for msg in lst_received:

                # will stop_running another threads if just one of them had a rejection
                if self._has_rejection:
                    keep_running = False
                    break

                '''
                    if this or any other thread got a rejected msg this will stop_running every thread for the actual robot.

                    (except when)
                    if the order came back rejected because of the late execution of it was right before a change on a 
                    partial executed original order (which turn this last change in the order invalid but not the 
                    whole operation).
                '''
                if msg.get("ExecType") == '8' and msg.get("OrdStatus") == '8' and \
                        msg.get("OrdRejReason") not in [2, 6, 7]:
                    self._has_rejection = True
                    break

                # if the order came back totally executed, nothing else to do here...
                if msg.get("ExecType") == '2' and msg.get("OrdStatus") == '2':
                    break

                # if the order came back partially executed.
                if msg.get("ExecType") == '1' and msg.get("OrdStatus") in ['1', '5']:
                    dtc_alt_order = self._edit_pending_order(basic_prov, dct_msg)
                    basic_prov.execute(**{**{"algo_name": algo_name}, **dtc_alt_order})
                    continue

            ttime.sleep(0.001)

    def _reject_position(self, thr: dict):
        oms_provider = thr.get("oms_instance")
        basic_prov = oms_provider.get("global_provider_conn", None)
        algo_name = f"{self._algo_cfg.get('name')}-{thr.get('oms_id')}-{thr.get('symbol')}"
        lst_orders = oms_provider.get("algo_msg_types", {}).get(algo_name, [])

        # List containing just partially and completelly executed orders from que current thread
        lst_received = [
            rec for rec in lst_orders if rec.get("OrderTag") == algo_name and rec.get("MsgType", "") == "8 "]

        if not lst_received:
            ttime.sleep(0.001)
            return

        lst_received = sorted(lst_received, key=lambda x: x[0].get("TransactTime"), reverse=True)
        for msg in lst_received:
            rec = basic_prov.decode(msg)

            # if the order came back totally executed...
            if rec.get("ExecType") == '2' and rec.get("OrdStatus") == '2':
                dct_order = self._create_position_order(basic_prov, thr, oms_provider)
                dct_order['Side'] = 2 if rec.get("side") == 1 else 1
                basic_prov.execute(**{**{"algo_name": algo_name}, **dct_order})
                break

            # if the order came back partially executed...
            if rec.get("ExecType") == '1' and rec.get("OrdStatus") in ['1', '5']:
                dtc_alt_order = self._cancel_pending_order(basic_prov, rec, thr)
                basic_prov.execute(**{**{"algo_name": algo_name}, **dtc_alt_order})

                dct_order = self._create_position_order(basic_prov, thr, oms_provider)
                dct_order['Side'] = 2 if rec.get("side") == 1 else 1
                dct_order['OrderQty'] = rec.get("CumQty")
                basic_prov.execute(**{**{"algo_name": algo_name}, **dct_order})
                continue

            if rec.get("ExecType") == '8' and rec.get("OrdStatus") == '8' and \
                    rec.get("OrdRejReason") not in [2, 6, 7]:
                self._has_rejection = True
                break

        ttime.sleep(0.001)

    def _request_position(self, thr: dict):
        oms_provider = thr.get("oms_instance")
        basic_prov = oms_provider.get("global_provider_conn", None)
        dct_order = self._request_for_positions(basic_prov)
        basic_prov.execute(**dct_order)

        ttime.sleep(0.001)
