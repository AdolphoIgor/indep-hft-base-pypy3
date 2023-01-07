import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

from api.bots.hft.hft_bot import HFTBot
from api.jobs.internal_config_provider import InternalConfigProviders
from api.logger import logger


class Arbitrage(HFTBot):

    def __init__(self, name, daemon, algo: dict, config_prov: InternalConfigProviders):
        super().__init__(name, daemon, algo, HFTBot.TWO_ARM, config_prov)

        self._arms = self._algo.get("threads")
        self._tpl_arm_0 = (
            self._arms[0].get("broker").get("account"),
            self._arms[0].get("broker").get("id"),
            self._arms[0].get("broker").get("password"),
            self._arms[0].get("symbol"),
            self._arms[0].get("stock_market"),
            self._arms[0].get("start_param").get("order_op_qty")
        )

        self._tpl_arm_1 = (
            self._arms[1].get("broker").get("account"),
            self._arms[1].get("broker").get("id"),
            self._arms[1].get("broker").get("password"),
            self._arms[1].get("symbol"),
            self._arms[1].get("stock_market"),
            self._arms[1].get("start_param").get("order_op_qty")
        )

        self._lst_sides = [
            (self._tpl_arm_0, self._tpl_arm_1),
            (self._tpl_arm_1, self._tpl_arm_0)
        ]

        self._dct_orders = None
        self._lst_orders_0 = None
        self._lst_orders_1 = None

        self._time_limit = datetime.strptime(self._algo.get("time_limit"), "%H:%M:%S")

    def _init_orders_instruments(self):
        if not self._dct_orders:
            dct_orders = {}
            for inst in self._config_prov.get_internal_provider_data("instruments"):
                if inst.get("type") == "orders":
                    dct_orders = inst
                    break

            if not dct_orders:
                return

            if not self._dct_orders:
                self._dct_orders = dct_orders

        if self._lst_orders_0 is not None and self._lst_orders_1 is not None:
            return

        dct_value = self._dct_orders.get("value")
        if not self._lst_orders_0:
            lst_orders_0 = dct_value.get(self._tpl_arm_0[3], [])
            if lst_orders_0:
                self._lst_orders_0 = lst_orders_0

        if not self._lst_orders_1:
            lst_orders_1 = dct_value.get(self._tpl_arm_1[3], [])
            if lst_orders_1:
                self._lst_orders_1 = lst_orders_1

    def _get_signal(self):
        lst_spread = list(self._dct_inst.get("spread").values())
        return [(lst_spread[0][0][1] - lst_spread[1][1][1]) > 0, (lst_spread[1][0][1] - lst_spread[0][1][1]) > 0], \
            lst_spread

    def _execute(self):

        # TODO: impor limite maximo de negociação, apos este momento não abre mais operações e encerra as que tiverem
        # abertas.

        self._init_orders_instruments()

        # if it has been a previous negotiation still opened, must be keep it running in order to finish it.
        if not self._is_asset_state(["opened"]) and self._dct_orders and not (self._lst_orders_0 or self._lst_orders_1):
            return

        b_in_session = datetime.now().time() <= self._time_limit.time()

        # entry point
        if b_in_session and not self._lst_orders_0 and not self._lst_orders_1:
            lst_signal, lst_spread = self._get_signal()
            # TODO: Retirar
            lst_signal = [True, False]
            if any(lst_signal):
                if lst_signal[0]:
                    lst_sides = self._lst_sides[0]
                    lst_prices = [lst_spread[0][0][0], lst_spread[0][0][1], lst_spread[1][1][0], lst_spread[1][1][1]]
                else:
                    lst_sides = self._lst_sides[1]
                    lst_prices = [lst_spread[1][0][0], lst_spread[1][0][1], lst_spread[0][1][0], lst_spread[0][1][1]]

                if lst_prices[0] < lst_sides[0][-1] and lst_prices[1] < lst_sides[1][-1]:
                    return

                self._profit_dll.send_buy_order(
                    conta=lst_sides[0][0], broker=lst_sides[0][1], senha=lst_sides[0][2], ativo=lst_sides[0][3],
                    bolsa=lst_sides[0][4], preco=lst_prices[1], qtd=lst_sides[0][5])

                self._profit_dll.send_sell_order(
                    conta=lst_sides[1][0], broker=lst_sides[1][1], senha=lst_sides[1][2], ativo=lst_sides[1][3],
                    bolsa=lst_sides[1][4], preco=lst_prices[3], qtd=lst_sides[1][5]
                )

        self._init_orders_instruments()

        '''
        {
            "corretora": corretora, "qtd": qtd, "traded_qtd": traded_qtd, "leaves_qtd": leaves_qtd, "side": side,
            "price": price, "stop_price": stop_price, "avg_price": avg_price, "profit_id": profit_id,
            "tipo_ordem": tipo_ordem, "conta": conta, "titular": titular, "cl_ord_id": cl_ord_id, "status": status,
            "date": date, "symbol": asset_id.ticker
        }
        
        _dct_order_status = {
            0: 'New', 1: 'PartiallyFilled', 2: 'Filled', 3: 'DoneForDay', 4: 'Canceled', 5: 'Replaced',
            6: 'PendingCancel', 7: 'Stopped', 8: 'Rejected', 9: 'Suspended', 10: 'PendingNew',
            11: 'Calculated', 12: 'Expired', 13: 'AcceptedForBidding', 14: 'PendingReplace',
            15: 'PartiallyFilledCanceleds', 16: 'Received', 17: 'PartiallyFilledExpired', 200: 'Unknown',
            201: 'HadesCreated', 202: 'BrokerSent', 203: 'ClientCreated', 204: 'OrderNotCreated'
        }
        
        self._tpl_arm_0 = (
            self._arms[0].get("broker").get("account"),
            self._arms[0].get("broker").get("id"),
            self._arms[0].get("broker").get("password"),
            self._arms[0].get("symbol"),
            self._arms[0].get("stock_market"),
            self._arms[0].get("start_param").get("order_op_qty")
        )
        
        lst_spread[side][0] = qtd
        lst_spread[side][1] = price
        '''
        # exit point
        if self._lst_orders_0 and self._lst_orders_1:
            lst_signal, lst_spread = self._get_signal()
            # TODO: Retirar
            lst_signal = [False, False]
            if not any(lst_signal) or not self._is_asset_state(["opened"]):
                with ThreadPoolExecutor(max_workers=1) as executor:
                    lst_thr = [executor.submit(self._proc_orders_list, lst[1], lst[0])
                               for lst in [(self._lst_orders_0, lst_spread[0]), (self._lst_orders_1, lst_spread[1])]]

                    for thr in as_completed(lst_thr):
                        excpt = thr.exception()
                        if excpt:
                            logger.error(excpt)

                        rslt = thr.result()
                        if rslt:
                            logger.info(rslt)

            if not self._lst_orders_0 and not self._lst_orders_1:
                self._print_positions()

    def _proc_orders_list(self, lst_spread: list, lst_orders: list):
        lst_copy = lst_orders[::-1]
        for ordr in lst_copy:
            symbol = ordr.get("symbol")
            arm = self._tpl_arm_0 if ordr.get("symbol") == self._tpl_arm_0[3] else self._tpl_arm_1

            status = ordr.get("status")

            text_message = ordr.get('text_message', '')
            if status == "Rejected" and text_message:
                logger.error(f"Error in Arbitrage. Symbol: {symbol}. Msg: {text_message}.")

            try:
                if status == "New":
                    self._profit_dll.send_cancel_order(conta=arm[0], broker=arm[1], senha=arm[2],
                                                       cl_ord_id=ordr.get("cl_ord_id"))

                # Compra = 1, Venda = 2
                if status == "Filled":
                    if ordr.get("side") == 2:
                        self._profit_dll.send_buy_order(conta=arm[0], broker=arm[1], senha=arm[2],
                                                        ativo=arm[3], bolsa=arm[4], preco=lst_spread[1][1],
                                                        qtd=ordr.get("qtd"))
                    else:
                        self._profit_dll.send_sell_order(conta=arm[0], broker=arm[1], senha=arm[2],
                                                         ativo=arm[3], bolsa=arm[4], preco=lst_spread[0][1],
                                                         qtd=ordr.get("qtd"))
                if status == "PartiallyFilled":
                    self._profit_dll.send_cancel_order(conta=arm[0], broker=arm[1], senha=arm[2],
                                                       cl_ord_id=ordr.get("cl_ord_id"))

                    if ordr.get("side") == 2:
                        self._profit_dll.send_buy_order(conta=arm[0], broker=arm[1], senha=arm[2],
                                                        ativo=arm[3], bolsa=arm[4], preco=lst_spread[1][1],
                                                        qtd=ordr.get("qtd"))
                    else:
                        self._profit_dll.send_sell_order(conta=arm[0], broker=arm[1], senha=arm[2],
                                                         ativo=arm[3], bolsa=arm[4], preco=lst_spread[0][1],
                                                         qtd=ordr.get("qtd"))

                    lst_rem = [rem for rem in lst_orders if rem.get("profit_id") == ordr.get("profit_id")]
                    for rem in lst_rem:
                        lst_orders.remove(rem)

            except Exception:
                logger.error(traceback.format_exc())

            lst_orders.remove(ordr)
            lst_copy = lst_orders[::-1]
