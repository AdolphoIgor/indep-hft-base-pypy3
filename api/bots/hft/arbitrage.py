import time
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

        self._tpl_sides = (
            (self._tpl_arm_0, self._tpl_arm_1),
            (self._tpl_arm_1, self._tpl_arm_0)
        )

        self._dct_orders = None
        self._lst_orders_0 = None
        self._lst_orders_1 = None
        self._lst_sprd = None

        self._time_limit = datetime.strptime(self._algo.get("time_limit"), "%H:%M:%S")
        self._first_exec = True
        self._pos_opened = False

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

        if self._first_exec:
            if self._lst_orders_0:
                self._lst_orders_0.clear()

            if self._lst_orders_1:
                self._lst_orders_1.clear()

            self._first_exec = False

    def _get_signal(self):
        return [(self._lst_sprd[0][0][1] - self._lst_sprd[1][1][1]) > 1,
                (self._lst_sprd[1][0][1] - self._lst_sprd[0][1][1]) > 1]

    @staticmethod
    def __get_order_w_status(lst_orders: list, status: str):
        dct_ordr = None
        for ordr in lst_orders[::-1]:
            if ordr.get("status") == status:
                dct_ordr = ordr
                break

        return dct_ordr

    def _execute(self):

        self._init_orders_instruments()

        # if it has been a previous negotiation still opened, must be keep it running in order to finish it.
        if not self._is_asset_state(["opened"]) and self._dct_orders and not (self._lst_orders_0 or self._lst_orders_1):
            return

        if not self._lst_sprd:
            self._lst_sprd = list(self._dct_inst.get("spread_rt").values())

        b_in_session = datetime.now().time() <= self._time_limit.time()

        # entry point --------------------------------------------------------------------------------------------------
        if b_in_session and not self._pos_opened and not self._lst_orders_0 and not self._lst_orders_1:
            lst_signal = self._get_signal()
            # lst_signal = [True, False]

            if any(lst_signal):
                if lst_signal[0]:
                    tpl_sides = self._tpl_sides[0]
                    lst_prices = [self._lst_sprd[0][0][0], self._lst_sprd[0][0][1],
                                  self._lst_sprd[1][1][0], self._lst_sprd[1][1][1]]
                else:
                    tpl_sides = self._tpl_sides[1]
                    lst_prices = [self._lst_sprd[1][0][0], self._lst_sprd[1][0][1],
                                  self._lst_sprd[0][1][0], self._lst_sprd[0][1][1]]

                multpl = 3
                if lst_prices[0] < (tpl_sides[0][-1] * multpl) or lst_prices[2] < (tpl_sides[1][-1] * multpl):
                    return

                print(f"lst_signal:{lst_signal}")
                print(f"lst_sprd:{self._lst_sprd}")
                print(f"tpl_sides:{tpl_sides}")
                print(f"lst_prices:{lst_prices}")

                lst_conf_signal = self._get_signal()
                if lst_signal == lst_conf_signal:
                    self._profit_dll.send_sell_order(
                        conta=tpl_sides[0][0], broker=tpl_sides[0][1], senha=tpl_sides[0][2], ativo=tpl_sides[0][3],
                        bolsa=tpl_sides[0][4], preco=lst_prices[1] - HFTBot.AGR_DOL_ADJ, qtd=tpl_sides[0][5]
                    )

                    self._profit_dll.send_buy_order(
                        conta=tpl_sides[1][0], broker=tpl_sides[1][1], senha=tpl_sides[1][2], ativo=tpl_sides[1][3],
                        bolsa=tpl_sides[1][4], preco=lst_prices[3] + HFTBot.AGR_DOL_ADJ, qtd=tpl_sides[1][5]
                    )

                print(f"lst_conf_signal:{lst_conf_signal}")
                print(f"lst_sprd:{self._lst_sprd}")

                self._pos_opened = True

        self._init_orders_instruments()

        # exit point ---------------------------------------------------------------------------------------------------
        if self._pos_opened:

            b_tried = False
            dct_ord_0, dct_ord_1 = None, None

            while not dct_ord_0 or not dct_ord_1:
                dct_ord_0 = self.__get_order_w_status(self._lst_orders_0, "Filled")
                dct_ord_1 = self.__get_order_w_status(self._lst_orders_1, "Filled")

                if dct_ord_0 and dct_ord_1:
                    # Compra = 1, Venda = 2
                    if dct_ord_0.get("side") == 1:
                        tpl_sides = self._tpl_sides[0]

                    else:
                        tpl_sides = self._tpl_sides[1]

                    while True:
                        if dct_ord_0.get("side") == 1:
                            res = (self._lst_sprd[0][0][1] - dct_ord_0.get("avg_price")) + \
                                  (dct_ord_1.get("avg_price") - self._lst_sprd[1][1][1])
                            lst_ord = [self._lst_sprd[0][0][1], self._lst_sprd[1][1][1]]

                        else:
                            res = (self._lst_sprd[1][0][1] - dct_ord_1.get("avg_price")) + \
                                  (dct_ord_0.get("avg_price") - self._lst_sprd[0][1][1])
                            lst_ord = [self._lst_sprd[1][0][1], self._lst_sprd[0][1][1]]

                        if res > 1:
                            break

                    self._profit_dll.send_sell_order(
                        conta=tpl_sides[0][0], broker=tpl_sides[0][1], senha=tpl_sides[0][2], ativo=tpl_sides[0][3],
                        bolsa=tpl_sides[0][4], preco=lst_ord[0] - HFTBot.AGR_DOL_ADJ, qtd=tpl_sides[0][5]
                    )

                    self._profit_dll.send_buy_order(
                        conta=tpl_sides[1][0], broker=tpl_sides[1][1], senha=tpl_sides[1][2], ativo=tpl_sides[1][3],
                        bolsa=tpl_sides[1][4], preco=lst_ord[1] + HFTBot.AGR_DOL_ADJ, qtd=tpl_sides[1][5]
                    )

                    self._pos_opened = False

                    break

                if b_tried:
                    break

                if not dct_ord_0 or not dct_ord_1:
                    time.sleep(5)
                    b_tried = True

            with ThreadPoolExecutor(max_workers=2) as executor:
                lst_thr = [executor.submit(self._proc_orders_list, lst[1], lst[0])
                           for lst in [(self._lst_orders_0, self._lst_sprd[0]),
                                       (self._lst_orders_1, self._lst_sprd[1])]]

                for thr in as_completed(lst_thr):
                    excpt = thr.exception()
                    if excpt:
                        logger.error(excpt)

                    rslt = thr.result()
                    if rslt:
                        logger.info(rslt)

            self._pos_opened = not self._lst_orders_0 and not self._lst_orders_1

    def _proc_orders_list(self, lst_spread: list, lst_orders: list):
        lst_copy = lst_orders[::-1]
        for ordr in lst_copy:
            symbol = ordr.get("symbol")
            arm = self._tpl_arm_0 if symbol == self._tpl_arm_0[3] else self._tpl_arm_1

            status = ordr.get("status")

            text_message = ordr.get('text_message', '')
            if status in ["Rejected", "OrderNotCreated"] and text_message:
                logger.error(f"Error in Arbitrage. Symbol: {symbol}. Msg: {text_message}.")

            try:
                if status == "New":
                    self._profit_dll.send_cancel_order(conta=arm[0], broker=arm[1], senha=arm[2],
                                                       cl_ord_id=ordr.get("cl_ord_id"))

                if status == "PartiallyFilled":
                    self._profit_dll.send_cancel_order(conta=arm[0], broker=arm[1], senha=arm[2],
                                                       cl_ord_id=ordr.get("cl_ord_id"))

                    if ordr.get("side") == 2:
                        self._profit_dll.send_buy_order(conta=arm[0], broker=arm[1], senha=arm[2],
                                                        ativo=arm[3], bolsa=arm[4],
                                                        preco=lst_spread[1][1] - HFTBot.AGR_DOL_ADJ,
                                                        qtd=ordr.get("qtd"))
                    else:
                        self._profit_dll.send_sell_order(conta=arm[0], broker=arm[1], senha=arm[2],
                                                         ativo=arm[3], bolsa=arm[4],
                                                         preco=lst_spread[0][1] + HFTBot.AGR_DOL_ADJ,
                                                         qtd=ordr.get("qtd"))

                    lst_rem = [rem for rem in lst_orders if rem.get("profit_id") == ordr.get("profit_id")]
                    for rem in lst_rem:
                        lst_orders.remove(rem)

            except Exception:
                logger.error(traceback.format_exc())

            lst_orders.remove(ordr)
            lst_copy = lst_orders[::-1]
