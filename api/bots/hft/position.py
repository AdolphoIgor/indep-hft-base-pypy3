class Position:

    def __init__(self, lst_orders: list, lst_sent_orders: list, lst_threads: list, lst_spread: list,
                 dct_ord_status: dict):
        self._lst_orders = lst_orders
        self._lst_sent_orders = lst_sent_orders
        self._lst_threads = eval(str(lst_threads))
        self._lst_spread = lst_spread
        self._dct_ord_status = dct_ord_status

        for thr in self._lst_threads:
            thr["qtd_exec_operations"] = 0
            thr["order_limit_qty_used"] = 0
            thr["open_positions"] = 0
            thr["gain_positions_opened"] = 0.0
            thr["gain"] = 0.0
            thr["has_ord_rem"] = True

    def get_position(self):
        """
            essa deve retornar a quantidade de pontas abertas junto com os cl_ord_id delas além de retornar dados
            globais
            como: Qtd max por operação, qtd max limite, qtd limite usada, qtd op abertas, ganhos nas operacoes até o
            momento, qtd operações executada, etc...

            order = {
                "corretora": corretora, "qtd": qtd, "traded_qtd": traded_qtd, "leaves_qtd": leaves_qtd,
                "side": side, "price": price, "stop_price": stop_price, "avg_price": avg_price,
                "profit_id": profit_id, "tipo_ordem": tipo_ordem, "conta": conta, "titular": titular,
                "cl_ord_id": cl_ord_id, "status": status, "date": date, "symbol": asset_id.ticker,
            }
        """

        def get_thread(order, spread):
            i = 0
            for f_thr in self._lst_threads:
                if f_thr.get("symbol") == order.get("symbol"):
                    return f_thr, spread[i]

                i += 1

        # Recupera todas as ordens deste algo e ainda não processadas.
        set_cl_ord_ids = set([ordr.get("cl_ord_id") for ordr in self._lst_orders])
        lst_ord_ids = [ordr for ordr in self._lst_orders
                       if ordr.get("cl_ord_id") in set_cl_ord_ids and not ordr.get("proc", False)]
        lst_ord_ids.sort(key=(lambda x: x.get("date")), reverse=True)

        for ordr in lst_ord_ids:
            # Recupera a estrutura da posição da ponta da ordem.
            sel_thr, sel_lp = get_thread(ordr, self._lst_spread)

            if self._dct_ord_status.get(ordr.get("status")) in ["bstNew"]:
                sel_thr["order_limit_qty_used"] = sel_thr["order_limit_qty_used"] + ordr.get("qtd")
                ordr["proc"] = True

            elif self._dct_ord_status.get(ordr.get("status")) in ["bstFilled", "bstPartiallyFilled"]:
                lst_ord_new = [n_ordr for n_ordr in self._lst_orders
                               if n_ordr.get("cl_ord_id") == ordr.get("cl_ord_id") and
                               self._dct_ord_status.get(n_ordr.get("status")) == "bstNew" and n_ordr.get("proc")]

                if len(lst_ord_new) > 0:
                    sel_thr["order_limit_qty_used"] = sel_thr.get("order_limit_qty_used", 0) - lst_ord_new[0].get("qtd")

                sel_thr["order_limit_qty_used"] = sel_thr["order_limit_qty_used"] + ordr.get("traded_qtd")

                lst_ord_part_exec = [
                    n_ordr for n_ordr in self._lst_orders
                    if n_ordr.get("cl_ord_id") == ordr.get("cl_ord_id") and
                       self._dct_ord_status.get(n_ordr.get("status")) in ["bstFilled", "bstPartiallyFilled"] and
                       n_ordr.get("proc")]

                if len(lst_ord_part_exec) == 0:
                    sel_thr["qtd_exec_operations"] = sel_thr.get("qtd_exec_operations", 0) + 1

                lst_ord_exec = [
                    n_ordr for n_ordr in self._lst_orders
                    if self._dct_ord_status.get(n_ordr.get("status")) in ["bstFilled", "bstPartiallyFilled"] and
                       n_ordr.get("cl_ord_id") not in ordr.get("lst_closed_pos", []) and
                       n_ordr.get("side") != ordr.get("side") and not n_ordr.get("proc")]

                for ex_ordr in lst_ord_exec:
                    entry_pos = round(abs(ordr.get("avg_price") - ex_ordr.get("avg_price")) * ordr.get("traded_qtd"), 2)

                    partial_pos = 0
                    if self._dct_ord_status.get(ex_ordr.get("status")) == "bstPartiallyFilled":
                        price = sel_lp[0][1] if ex_ordr.get("side") == "B" else sel_lp[1][1]
                        partial_pos = round(abs(ordr.get("avg_price") - price) * ordr.get("leaves_qtd"), 2)
                        sel_thr["open_positions"] = sel_thr.get("open_positions") + 1

                    sel_thr["gain_positions_opened"] = entry_pos + partial_pos

                    if ordr.get("qtd") == ex_ordr.get("traded_qtd"):
                        sel_thr["open_positions"] = sel_thr.get("open_positions") - 1
                        sel_thr["gain"] = sel_thr["gain"] + entry_pos + partial_pos
                        sel_thr["gain_positions_opened"] = sel_thr["gain_positions_opened"] - entry_pos + partial_pos
                        sel_thr["order_limit_qty_used"] = sel_thr["order_limit_qty_used"] - ordr.get("traded_qtd")

                    ex_ordr["proc"] = True
                    ordr.get("lst_closed_pos", []).append(ex_ordr.get("cl_ord_id"))

            sel_thr["has_ord_rem"] = sel_thr["order_op_qty"] > sel_thr["order_limit_qty_used"]

            ordr["proc"] = True

        return self._lst_threads

    def get_filtered_orders(self, lst_exc_status: list):
        """Retorna extritamente as ordens de acordo com filtro."""
        return [order for order in self._lst_orders
                if order.get("cl_ord_id") in self._lst_sent_orders and
                self._dct_ord_status.get(order.get("status")) in lst_exc_status]
