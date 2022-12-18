import json
import sys


class PositionMgr:
    POS_INIT = -1
    POS_NEW = 0
    POS_PRT_OPENED = 1
    POS_OPENED = 2
    POS_PRT_EXEC = 3
    POS_EXECUTED = 4
    POS_REJECTED = 5
    POS_CANCELED = 6

    # holds every opened positions
    _lst_opened_positions = []

    # for backup purposes only
    _lst_closed_positions = []

    # for every processed cl_ord_id
    _lst_used_clordid = []

    def __init__(self, lst_orders: list, lst_sent_orders: list, algo: dict, dct_ord_status: dict):
        self._lst_orders = lst_orders
        self._dct_ord_status = dct_ord_status
        self._lst_sent_orders = lst_sent_orders

        # position summary
        self._dct_pos_mgr = algo.copy()
        self._dct_pos_mgr.update(
            {
                "position": {
                    "qtd_open_positions": 0,
                    "fin_result": 0.0,
                    "positions": {}
                }
            }
        )

        self._lst_threads = self._dct_pos_mgr.get("threads", [])
        for thr in self._lst_threads:
            thr.update(
                {
                    "position": {
                        "limit_qty_order_used": 0,
                        "has_ord_rem": True
                    }
                }
            )

    def __print_state(self):
        print("---------------------------------------------------------------")
        print("-->> _lst_opened_positions")
        json_formatted_str = json.dumps(self._lst_opened_positions, indent=2)
        print(json_formatted_str)
        print("")
        print("-->> _lst_closed_positions")
        json_formatted_str = json.dumps(self._lst_closed_positions, indent=2)
        print(json_formatted_str)
        print("")
        print("-->> _lst_used_clordid")
        json_formatted_str = json.dumps(self._lst_used_clordid, indent=2)
        print(json_formatted_str)
        print("")
        print("-->> self._lst_orders")
        json_formatted_str = json.dumps(self._lst_orders, indent=2)
        print(json_formatted_str)
        print("")
        print("-->> self._lst_sent_orders")
        json_formatted_str = json.dumps(self._lst_sent_orders, indent=2)
        print(json_formatted_str)
        print("")
        print("---------------------------------------------------------------")

    def __update_arm(self, symbol, qtd_traded):
        # updates the arm/thread position data
        thr = [thr for thr in self._lst_threads if thr.get("symbol") == symbol][0]
        if qtd_traded > 0:
            thr.get("position")["limit_qty_order_used"] = qtd_traded
        else:
            thr.get("position")["limit_qty_order_used"] += qtd_traded

        thr.get("position")["has_ord_rem"] = \
            thr.get("start_param").get("limit_qty_order") > thr.get("position")["limit_qty_order_used"]

        gettrace = getattr(sys, 'gettrace', None)
        if not gettrace() is None:
            print("---------------------------------------------------------------")
            print("-->> __update_arm")
            print(f"{symbol} - {thr.get('position')}")
            print("---------------------------------------------------------------")

    def __get_updated_status(self, lst_status: list, lst_open_arms_status: list, bol_closing=False) -> int:
        if 'bstRejected' in lst_status:
            return self.POS_REJECTED
        elif 'bstCanceled' in lst_status:
            return self.POS_CANCELED
        elif 'bstPartiallyFilled' in lst_status:
            return self.POS_PRT_EXEC if bol_closing else self.POS_PRT_OPENED
        elif all([True if i == 'bstFilled' else False for i in lst_status]) and len(lst_status) >= len(
                lst_open_arms_status):
            return self.POS_EXECUTED if bol_closing else self.POS_OPENED
        elif 'bstFilled' in lst_status:
            return self.POS_PRT_EXEC if bol_closing else self.POS_PRT_OPENED

        return self.POS_NEW

    def _proc_lated_orders(self):
        # remove from self._lst_orders every late update of its arm's orders.
        bol_found = False
        for ordr in self._lst_orders:
            for pos in self._lst_closed_positions:
                for arm in pos.get("open_arms"):
                    if ordr.get("cl_ord_id") == arm.get("id"):
                        bol_found = True
                        break

                if not bol_found:
                    for arm in pos.get("close_arms"):
                        if ordr.get("cl_ord_id") == arm.get("id"):
                            bol_found = True
                            break

                if bol_found:
                    self._lst_orders.remove(ordr)
                    break

    def _proc_new_positions(self):
        if not self._lst_orders:
            return

        lst_ordrs = [ordr for ordr in self._lst_sent_orders if ordr.get("id") is not None]
        if not lst_ordrs:
            return

        # creates and manage positions.
        lst_arms = []
        lst_status = []
        lst_arms_ordrs = []

        for ord_id in set([i.get("id") for i in lst_ordrs]):
            for cl_ord_id in [i.get("cl_ord_id") for i in lst_ordrs if i.get("id") == ord_id]:
                dct_arm = {}

                lst_ord_id = [ordr for ordr in self._lst_orders if ordr.get("cl_ord_id") == cl_ord_id]
                item = lst_ord_id[-1]

                dct_arm["id"] = cl_ord_id
                dct_arm["symbol"] = item.get("symbol")
                dct_arm["status"] = item.get("status")
                dct_arm["side"] = item.get("side")
                dct_arm["qtd"] = item.get("qtd")
                dct_arm["traded_qtd"] = item.get("traded_qtd")
                dct_arm["orders"] = lst_ord_id

                # updates the arm/thread position data
                self.__update_arm(item.get("symbol"), item.get("traded_qtd"))

                lst_arms_ordrs.extend(lst_ord_id)
                lst_arms.append(dct_arm)
                lst_status.append(item.get("status"))
                self._lst_used_clordid.append(cl_ord_id)

            self._lst_opened_positions.append(
                {
                    "id": ord_id,
                    "open_status": self.__get_updated_status(lst_status, lst_open_arms_status=[]),
                    "open_arms_status": lst_status,
                    "open_arms": lst_arms,
                    "close_status": self.POS_INIT,
                    "close_arms_status": [],
                    "close_arms": []
                }
            )

            # updates the global position data
            self._dct_pos_mgr.get("position")["qtd_open_positions"] += 1

        for sor in lst_ordrs:
            self._lst_sent_orders.remove(sor)

        for ordr in lst_arms_ordrs:
            self._lst_orders.remove(ordr)

    def _proc_upd_new_positions(self):
        if not self._lst_orders or not self._lst_opened_positions:
            return

        lst_arms_ordrs = []
        for pos in [pos for pos in self._lst_opened_positions if pos.get("open_status") == self.POS_PRT_OPENED]:
            for arm in pos.get("open_arms"):
                for ordr in self._lst_orders:
                    if ordr.get("cl_ord_id") == arm.get("id"):

                        status = ordr.get("status")

                        if status not in ["bstCanceled", "bstRejected"]:
                            arm["traded_qtd"] = ordr.get("traded_qtd")

                        if status in ["bstPartiallyFilled", "bstFilled", "bstRejected", "bstCanceled"]:
                            arm["status"] = status
                            lst_arms_ordrs.append(ordr)

                        if arm["qtd"] == arm.get("traded_qtd"):
                            arm["status"] = "bstFilled"

                        arm.get("orders").append(ordr)

        if len(lst_arms_ordrs) > 0:
            for ordr in lst_arms_ordrs:
                self.__update_arm(ordr.get("symbol"), ordr.get("traded_qtd"))
                self._lst_orders.remove(ordr)

            lst_status = [arm.get("status") for arm in pos.get("open_arms")]
            pos["open_arms_status"] = lst_status
            pos["open_status"] = self.__get_updated_status(lst_status, lst_open_arms_status=pos.get("open_arms_status"))

    def _proc_close_positions(self):
        if not self._lst_orders or not self._lst_opened_positions:
            return

        for pos in [pos for pos in self._lst_opened_positions
                    if pos.get("close_status") in [self.POS_INIT, self.POS_PRT_EXEC]]:

            lst_arms_ordrs = []

            for arm in pos.get("open_arms"):
                side = "B" if arm.get("side") == "S" else "S"
                symbol = arm.get("symbol")

                lst_sel_ordrs = [
                    ordr for ordr in self._lst_orders
                    if ordr.get("symbol") == symbol and ordr.get("side") == side and
                       ordr.get("status") in ["bstPartiallyFilled", "bstFilled", "bstCanceled", "bstRejected"]]

                if pos.get("close_status") == self.POS_INIT:
                    lst_sel_ordrs = [
                        ordr for ordr in lst_sel_ordrs if ordr.get("cl_ord_id") not in self._lst_used_clordid]

                if len(lst_sel_ordrs) == 0:
                    continue

                qtd = arm.get("qtd")
                if pos.get("close_status") == self.POS_INIT:
                    dct_arm = {
                        "symbol": symbol,
                        "qtd": qtd,
                        "side": side,
                        "orders": [],
                        "status": "",
                        "traded_qtd": 0
                    }
                else:
                    dct_arm = [ca for ca in pos.get("close_arms") if ca.get("symbol") == symbol][0]

                qtd -= dct_arm.get("traded_qtd")
                orig_qtd_traded = dct_arm.get("traded_qtd")
                lst_filter = [ordr for ordr in lst_sel_ordrs if ordr.get("qtd") == qtd]

                if len(lst_filter) == 0:
                    lst_filter = [ordr for ordr in lst_sel_ordrs if ordr.get("qtd") < qtd]

                if len(lst_filter) == 0:
                    continue

                lst_traded = []
                for item in lst_filter:
                    if item.get("status") in ["bstPartiallyFilled", "bstFilled"]:
                        if dct_arm["traded_qtd"] >= arm["traded_qtd"]:
                            break

                        cl_ord_id = item.get("cl_ord_id")
                        traded_qtd = item.get("traded_qtd")

                        if self._lst_used_clordid[-1] != cl_ord_id:
                            if dct_arm["traded_qtd"] + item.get("qtd") > arm["traded_qtd"]:
                                continue

                            self._lst_used_clordid.append(cl_ord_id)
                            dct_arm["id"] = cl_ord_id

                            dct_arm["traded_qtd"] += traded_qtd

                            if item.get("status") == "bstFilled":
                                lst_traded.append(traded_qtd)

                        else:
                            lst_traded.append(traded_qtd)
                            dct_arm["traded_qtd"] = sum(lst_traded)

                        dct_arm["orders"].append(item)

                    lst_arms_ordrs.append(item)

                    # updates the arm/thread position data
                self.__update_arm(symbol, -(dct_arm["traded_qtd"] - orig_qtd_traded))

                dct_arm["status"] = "bstFilled" if dct_arm["traded_qtd"] == arm["qtd"] else "bstPartiallyFilled"

                if pos.get("close_status") == self.POS_INIT:
                    pos["close_arms"].append(dct_arm)

            for ordr in lst_arms_ordrs:
                self._lst_orders.remove(ordr)

            for ord_id in set([ordr.get("cl_ord_id") for ordr in lst_arms_ordrs]):
                dct_ordr = {"id": None, "cl_ord_id": ord_id}
                if dct_ordr in self._lst_sent_orders:
                    self._lst_sent_orders.remove(dct_ordr)

            # updates position status
            lst_status = []
            for arm in pos.get("close_arms"):
                lst_status.append(arm.get("status"))

            pos["close_arms_status"] = lst_status
            pos["close_status"] = self.__get_updated_status(lst_status, bol_closing=True,
                                                            lst_open_arms_status=pos.get("open_arms_status"))

        for pos in [pos for pos in self._lst_opened_positions if pos.get("close_status") == self.POS_EXECUTED]:
            # updates the global position data
            self._dct_pos_mgr.get("position")["qtd_open_positions"] -= 1
            self._lst_closed_positions.append(pos)
            self._lst_opened_positions.remove(pos)

    def proc_positions(self):
        self._proc_new_positions()
        self._proc_upd_new_positions()
        self._proc_close_positions()
        self._proc_lated_orders()

        gettrace = getattr(sys, 'gettrace', None)
        if not gettrace() is None:
            self.__print_state()

    def update_fin_result(self):
        lst_whole = [pos for pos in self._lst_opened_positions]
        lst_whole.extend(self._lst_closed_positions)

        dct_arms = self._dct_pos_mgr.get("position").get("positions")
        for pos in lst_whole:
            # opening orders.
            for opn in pos.get("open_arms"):
                symbol = opn.get("symbol")
                dct_pos = dct_arms.get(symbol, {})
                if not dct_pos:
                    dct_arms[symbol] = dct_pos
                    dct_pos["side"] = opn.get("side")

                dct_pos["PMO"] = 0
                for ordr in opn.get("orders"):
                    dct_pos["PMO"] += ordr.get("traded_qtd") * ordr.get("avg_price")

                    # closing orders.
            for cls in pos.get("close_arms"):
                dct_pos = dct_arms.get(cls.get("symbol"), {})

                dct_pos["PMC"] = 0
                for ordr in cls.get("orders"):
                    dct_pos["PMC"] += ordr.get("traded_qtd") * ordr.get("avg_price")

                if dct_pos["side"] == 'S':
                    dct_pos["PM"] = dct_pos["PMC"] - dct_pos["PMO"]
                else:
                    dct_pos["PM"] = dct_pos["PMO"] - dct_pos["PMC"]

        self._dct_pos_mgr.get("position")["fin_result"] = sum([v.get("PM") for k, v in dct_arms.items()])

    def get_pos(self):
        return self._dct_pos_mgr.copy()

    def get_pos_arms(self):
        return self._lst_threads.copy()

    def get_lst_positions(self, lst_open_arms_status: list, close_arms_status: list):
        return [pos.copy() for pos in self._lst_opened_positions
                if pos.get("open_status") in lst_open_arms_status and pos.get("close_status") in close_arms_status]
