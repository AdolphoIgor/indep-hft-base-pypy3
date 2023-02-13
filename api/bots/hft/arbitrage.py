import time
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta

from api.bots.bot import Bot
from api.jobs.internal_config_provider import InternalConfigProviders
from api.logger import logger


class Arbitrage(Bot):

    def __init__(self, name, daemon, algo: dict, config_prov: InternalConfigProviders):
        super().__init__(name, daemon, algo, Bot.ARM_TWO, config_prov)

        self._threshold_opening = self._algo.get("start_param").get("threshold")["opening_value"]
        self._threshold_opening = 0 if self._threshold_opening < 0 else self._threshold_opening

        self._arms = self._algo.get("threads")
        self._tpl_arm_0 = None
        self._tpl_arm_1 = None
        self._tpl_sides = None

        self._lst_sprd_rt = None
        self._ord_time_limit = None

    def _initilize(self):
        self._test_qtd_assets()

        # get the arms configuration ready
        self._tpl_arm_0 = (
            self._arms[0].get("broker").get("account"),
            self._arms[0].get("broker").get("id"),
            self._arms[0].get("broker").get("password"),
            self._arms[0].get("symbol"),
            self._arms[0].get("stock_market"),
            self._arms[0].get("start_param").get("order_op_qty") * self._arms[0].get("lote"),
            self._arms[0].get("agr_adj"),
            self._arms[0].get("tick_value")
        )

        self._tpl_arm_1 = (
            self._arms[1].get("broker").get("account"),
            self._arms[1].get("broker").get("id"),
            self._arms[1].get("broker").get("password"),
            self._arms[1].get("symbol"),
            self._arms[1].get("stock_market"),
            self._arms[1].get("start_param").get("order_op_qty") * self._arms[1].get("lote"),
            self._arms[1].get("agr_adj"),
            self._arms[1].get("tick_value")
        )

        self._tpl_sides = (
            (self._tpl_arm_0, self._tpl_arm_1),
            (self._tpl_arm_1, self._tpl_arm_0)
        )

        # get instruments made-up in our side (not provided)
        self._lst_sprd_rt = list(self._dct_inst.get("spread_rt").values())

    def _execute(self):

        if self._pos_stopped:
            return

        # if it has been a previous negotiation still opened, must be keep it running in order to finish it.
        if not self._is_asset_state(["opened"]) and not self._pos_opened:
            return

        # entry point --------------------------------------------------------------------------------------------------
        if self._b_in_session and not self._pos_opened:

            # S1B2
            if (self._lst_sprd_rt[0][0][1] - self._lst_sprd_rt[1][1][1]) > self._threshold_opening:
                self._profit_dll.send_sell_order(
                    conta=self._tpl_sides[0][0][0], broker=self._tpl_sides[0][0][1], senha=self._tpl_sides[0][0][2],
                    ativo=self._tpl_sides[0][0][3], bolsa=self._tpl_sides[0][0][4],
                    preco=self._lst_sprd_rt[0][0][1] - self._tpl_sides[0][0][6], qtd=self._tpl_sides[0][0][5]
                )

                self._profit_dll.send_buy_order(
                    conta=self._tpl_sides[0][1][0], broker=self._tpl_sides[0][1][1], senha=self._tpl_sides[0][1][2],
                    ativo=self._tpl_sides[0][1][3], bolsa=self._tpl_sides[0][1][4],
                    preco=self._lst_sprd_rt[1][1][1] + self._tpl_sides[0][1][6], qtd=self._tpl_sides[0][1][5]
                )

                self._pos_opened = True

                logger.debug(f"ENTRADA->SIDES: {[self._tpl_sides[0][0], self._tpl_sides[0][1]]}")
                logger.debug(f"ENTRADA->SPREAD: {[self._lst_sprd_rt[0][0][1], self._lst_sprd_rt[1][1][1]]}")

            # S2B1
            elif (self._lst_sprd_rt[1][0][1] - self._lst_sprd_rt[0][1][1]) > self._threshold_opening:
                self._profit_dll.send_sell_order(
                    conta=self._tpl_sides[1][0][0], broker=self._tpl_sides[1][0][1], senha=self._tpl_sides[1][0][2],
                    ativo=self._tpl_sides[1][0][3], bolsa=self._tpl_sides[1][0][4],
                    preco=self._lst_sprd_rt[1][0][1] - self._tpl_sides[1][0][6], qtd=self._tpl_sides[1][0][5]
                )

                self._profit_dll.send_buy_order(
                    conta=self._tpl_sides[1][1][0], broker=self._tpl_sides[1][1][1], senha=self._tpl_sides[1][1][2],
                    ativo=self._tpl_sides[1][1][3], bolsa=self._tpl_sides[1][1][4],
                    preco=self._lst_sprd_rt[0][1][1] + self._tpl_sides[1][1][6], qtd=self._tpl_sides[1][1][5]
                )

                self._pos_opened = True

                logger.debug(f"ENTRADA->SIDES: {[self._tpl_sides[1][0], self._tpl_sides[1][1]]}")
                logger.debug(f"ENTRADA->SPREAD: {[self._lst_sprd_rt[1][0][1], self._lst_sprd_rt[0][1][1]]}")

            return

        # exit point ---------------------------------------------------------------------------------------------------
        if self._pos_opened:

            b_tried = False
            dct_ord_0, dct_ord_1 = None, None

            while not dct_ord_0 or not dct_ord_1:
                lst_orders_0 = self._dct_inst.get("orders").get(self._lst_sbl[0], None)
                lst_orders_1 = self._dct_inst.get("orders").get(self._lst_sbl[1], None)

                dct_ord_0 = self._get_order_w_status(lst_orders_0, "Filled")
                dct_ord_1 = self._get_order_w_status(lst_orders_1, "Filled")

                if dct_ord_0 and dct_ord_1:
                    # Compra = 1, Venda = 2
                    if dct_ord_0.get("side") == 1:
                        tpl_sides = self._tpl_sides[0]

                    else:
                        tpl_sides = self._tpl_sides[1]

                    dcr_thshhld_cfg = self._algo.get("stop_param").get("threshold")
                    closing_mode = dcr_thshhld_cfg.get("closing_mode", "manual")
                    closing_limit = dcr_thshhld_cfg.get("closing_limit")
                    while True:
                        time.sleep(0.00001)

                        if dct_ord_0.get("side") == 1:
                            res = (self._lst_sprd_rt[0][0][1] - dct_ord_0.get("avg_price")) + \
                                  (dct_ord_1.get("avg_price") - self._lst_sprd_rt[1][1][1])
                            lst_ord = [self._lst_sprd_rt[0][0][1], self._lst_sprd_rt[1][1][1]]

                        else:
                            res = (self._lst_sprd_rt[1][0][1] - dct_ord_1.get("avg_price")) + \
                                  (dct_ord_0.get("avg_price") - self._lst_sprd_rt[0][1][1])
                            lst_ord = [self._lst_sprd_rt[1][0][1], self._lst_sprd_rt[0][1][1]]

                        if self._b_in_session and closing_mode == "auto":
                            if not self._ord_time_limit:
                                start_date = min((dct_ord_0.get("date"), dct_ord_1.get("date")))
                                self._ord_time_limit = datetime.strptime(start_date, '%d/%m/%Y %H:%M:%S.%f') + \
                                    timedelta(minutes=closing_limit)

                            self._thrshld_value_limit = abs(dct_ord_0.get("avg_price") - dct_ord_1.get("avg_price"))
                            if datetime.now().time() < self._ord_time_limit.time():
                                self._thrshld_value_limit += tpl_sides[0][7]

                        if res > self._thrshld_value_limit:
                            break

                    self._profit_dll.send_sell_order(
                        conta=tpl_sides[0][0], broker=tpl_sides[0][1], senha=tpl_sides[0][2], ativo=tpl_sides[0][3],
                        bolsa=tpl_sides[0][4], preco=lst_ord[0] - tpl_sides[0][6], qtd=tpl_sides[0][5]
                    )

                    self._profit_dll.send_buy_order(
                        conta=tpl_sides[1][0], broker=tpl_sides[1][1], senha=tpl_sides[1][2], ativo=tpl_sides[1][3],
                        bolsa=tpl_sides[1][4], preco=lst_ord[1] + tpl_sides[1][6], qtd=tpl_sides[1][5]
                    )

                    logger.debug(f"SAIDA->SIDES: {tpl_sides}")
                    logger.debug(f"SAIDA->SPREAD: {lst_ord}")

                    time.sleep(5)

                    with ThreadPoolExecutor(max_workers=Bot.ARM_TWO) as executor:
                        lst_thr = [executor.submit(self._proc_orders_list, lst[1], lst[0])
                                   for lst in [(lst_orders_0, self._lst_sprd_rt[0]),
                                               (lst_orders_1, self._lst_sprd_rt[1])]]

                        for thr in as_completed(lst_thr):
                            excpt = thr.exception()
                            if excpt:
                                logger.error(excpt)

                            rslt = thr.result()
                            if rslt:
                                logger.info(rslt)

                    self._pos_opened = False
                    self._ord_time_limit = None
                    break

                if b_tried:
                    break

                if not dct_ord_0 or not dct_ord_1:
                    time.sleep(5)
                    b_tried = True

            # TODO: Reduzir apos testar.
            lst_pos = self._get_position()
            print(lst_pos)
            if lst_pos[3]:
                self._pos_stopped = True

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
                                                        preco=lst_spread[1][1] - arm[6],
                                                        qtd=ordr.get("qtd"))
                    else:
                        self._profit_dll.send_sell_order(conta=arm[0], broker=arm[1], senha=arm[2],
                                                         ativo=arm[3], bolsa=arm[4],
                                                         preco=lst_spread[0][1] + arm[6],
                                                         qtd=ordr.get("qtd"))

                    lst_rem = [rem for rem in lst_orders if rem.get("profit_id") == ordr.get("profit_id")]
                    for rem in lst_rem:
                        lst_orders.remove(rem)

            except Exception:
                logger.error(traceback.format_exc())

            lst_orders.remove(ordr)
            lst_copy = lst_orders[::-1]
