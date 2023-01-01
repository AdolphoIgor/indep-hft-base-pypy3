from datetime import datetime

from api.bots.hft.bot import Bot
from api.bots.hft.position import PositionMgr
from api.jobs.internal_config_provider import InternalConfigProviders


class Auction(Bot):
    """
        For details on the B3 auction:
        https://www.bmf.com.br/bmfbovespa/pages/boletim1/bd_manual/RegrasPregao.asp
        https://www.bmf.com.br/bmfbovespa/pages/boletim1/bd_manual/Tunel_leilao.asp
        https://www.b3.com.br/pt_br/solucoes/plataformas/puma-trading-system/para-participantes-e-traders/regras-e-parametros-de-negociacao/parametros-dos-tuneis-de-negociacao/
        https://www.b3.com.br/pt_br/solucoes/plataformas/puma-trading-system/para-participantes-e-traders/regras-e-parametros-de-negociacao/tuneis-de-negociacao/

    """

    def __init__(self, name, daemon, algo: dict, config_prov: InternalConfigProviders):
        super().__init__(name, daemon, algo, Bot.ONE_ARM, config_prov)
        self._lst_entry_signal = []

    def execute(self):
        # TODO: preciso saber como detectar o tempo restante do leião e da fase randomica.

        """
            1) Aqui estou assumindo que entrou no leilão, na prorrogação ou fase randômica...
            2) não importa saber o fim do leilão para lançar ordens, não estamos na pre-abertura ou pre-fechamento aqui,
                portanto, o preço teórico deve ficar estável pois se mudar, teremos prorrogações e até a fase randomica.
                2.1) Assim, é seguro lançar ordem e se o preço teorico mudar e a ordem ficar fora dele, basta cancela-la
                2.2) Só vai entrar com outra ordem se os critérios para entrada estiverem de acordo com estabelecido.

            3) A saída vai tratar tanto o Gain quanto o Stop. O Stop sempre será a mercado no fim da fila, se der stop
                tem que cancelar a ordem de gain (que é ordem limite) imediatamente depois.

            order = {
                "corretora": corretora, "qtd": qtd, "traded_qtd": traded_qtd, "leaves_qtd": leaves_qtd,
                "side": side, "price": price, "stop_price": stop_price, "avg_price": avg_price,
                "profit_id": profit_id, "tipo_ordem": tipo_ordem, "conta": conta, "titular": titular,
                "cl_ord_id": cl_ord_id, "status": status, "date": date, "symbol": asset_id.ticker,
            }

            dct_quote["theoretical_price"] = theoretical_price
            dct_quote["theoretical_qtd"] = theoretical_qtd

            1. Em relação as perguntas. A fase randomica dos Leilões recebm qual status? Seria tcsAuctioned?
                O status tcsAuctioned é informado no leilão de abertura e de final de pregão.

            2. E em relação ao status tcsFrozen ou tcsInhibited, quando eles ocorrem?
                O status tcsFrozen ocorre em momentos onde o mercado está pausado, e o status tcsInhibited ocorre em
                momentos onde o horário não está disponível para negociações.

        """

        def get_entry_signal():
            lst_spread = self._dct_inst.get("spread")
            lst_lp = [lst_spread[0], lst_spread[1]]
            qtd = lst_lp[0][0][0] - lst_lp[1][0][0] + lst_lp[0][1][0] - lst_lp[1][1][0]

            qtd = abs(qtd)
            nivel_p_dentro = 2
            lst_niv_menor_liq = None
            side = "B" if qtd > 0 else "S"
            while True:
                if qtd <= 0:
                    break

                try:
                    idx = 1 if side == "B" else 0
                    qtd_nivel = lst_lp[idx][nivel_p_dentro][0]
                    prc_nivel = lst_lp[idx][nivel_p_dentro][1]
                    qtd -= qtd_nivel

                except Exception:
                    break

                if nivel_p_dentro == 2:
                    lst_niv_menor_liq = [nivel_p_dentro, qtd_nivel, prc_nivel]

                elif lst_niv_menor_liq[1] > qtd_nivel:
                    lst_niv_menor_liq[0] = nivel_p_dentro
                    lst_niv_menor_liq[1] = qtd_nivel
                    lst_niv_menor_liq[2] = prc_nivel

                nivel_p_dentro += 1

            return [side, qtd, nivel_p_dentro, lst_niv_menor_liq]

        dct_pos_threads = self._position_mgr.get_pos_arms()

        while self._is_asset_state(["auctioned"]):
            if dct_pos_threads[0].get("position").get("has_ord_rem"):
                self._lst_entry_signal = get_entry_signal()
                if self._lst_entry_signal[2] > 2:
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
                    if self._lst_entry_signal[0] == "B":
                        self._lst_orders_sent.append({"id": timestamp, "cl_ord_id": self._profit_dll.send_buy_order(
                            conta=dct_pos_threads.get("broker").get("account"),
                            broker=dct_pos_threads.get("broker").get("id"),
                            senha=dct_pos_threads.get("broker").get("password"),
                            ativo=dct_pos_threads.get("symbol"),
                            bolsa=dct_pos_threads.get("stock_market"),
                            preco=self._dct_inst.get("quote").get("theoretical_price"),
                            qtd=dct_pos_threads.get("start_param").get("order_op_qty")
                        )})
                    else:
                        self._lst_orders_sent.append({"id": timestamp, "cl_ord_id": self._profit_dll.send_sell_order(
                            conta=dct_pos_threads.get("broker").get("account"),
                            broker=dct_pos_threads.get("broker").get("id"),
                            senha=dct_pos_threads.get("broker").get("password"),
                            ativo=dct_pos_threads.get("symbol"),
                            bolsa=dct_pos_threads.get("stock_market"),
                            preco=self._dct_inst.get("quote").get("theoretical_price"),
                            qtd=dct_pos_threads.get("start_param").get("order_op_qty")
                        )})

            self._position_mgr.proc_positions()

            # Se a ordem nova ficou fora da formação do preço teórico, cancela e espera novo sinal.
            lst_new_ordrs = [
                ordr for pos in self._position_mgr.get_lst_positions([PositionMgr.POS_NEW], [PositionMgr.POS_INIT])
                for ordr in pos.get("open_arms")
                if ordr.get("status") == "bstNew"
            ]

            for ordr in lst_new_ordrs:
                if ordr.get("price") != self._dct_inst.get("quote").get("theoretical_price"):
                    self._lst_orders_sent.append({"id": None, "cl_ord_id": self._profit_dll.send_cancel_order(
                        conta=dct_pos_threads.get("broker").get("account"),
                        broker=dct_pos_threads.get("broker").get("id"),
                        senha=dct_pos_threads.get("broker").get("password"),
                        cl_ord_id=ordr.get("cl_ord_id")
                    )})

        """
            A saída nunca será dentro do leilão, prorrogação ou fase randomica...
        """
        if self._is_asset_state(["opened"]):

            self._position_mgr.proc_positions()

            # se abriu o mercado e a ordem de entrada não foi atendida, cancela a ordem.
            if self._position_mgr.get_pos().get("qtd_open_positions") == 0:
                lst_new_ordrs = [
                    ordr for pos in self._position_mgr.get_lst_positions([PositionMgr.POS_NEW], [PositionMgr.POS_INIT])
                    for ordr in pos.get("open_arms")
                    if ordr.get("status") == "bstNew"
                ]

                for ordr in lst_new_ordrs:
                    self._lst_orders_sent.append({"id": None, "cl_ord_id": self._profit_dll.send_cancel_order(
                        conta=dct_pos_threads.get("broker").get("account"),
                        broker=dct_pos_threads.get("broker").get("id"),
                        senha=dct_pos_threads.get("broker").get("password"),
                        cl_ord_id=ordr.get("cl_ord_id")
                    )})

                return

            """
                pegar a ordem executada e ainda não zerada e já colocar a ordem de saída GAIN no nivel certo...
            """
            lst_exec_ordrs = [
                ordr for pos in self._position_mgr.get_lst_positions(
                    [PositionMgr.POS_OPENED], [PositionMgr.POS_INIT])
                for ordr in pos.get("open_arms")
                if ordr.get("status") in ["bstPartiallyFilled", "bstFilled"]
            ]

            for ordr in lst_exec_ordrs:
                # se a ordem foi executada parcialmente (na abertura), cancelar o saldo restante
                if ordr.get("qtd") != ordr.get("traded_qtd"):
                    self._lst_orders_sent.append({"id": None, "cl_ord_id": self._profit_dll.send_cancel_order(
                        conta=dct_pos_threads.get("broker").get("account"),
                        broker=dct_pos_threads.get("broker").get("id"),
                        senha=dct_pos_threads.get("broker").get("password"),
                        cl_ord_id=ordr.get("cl_ord_id")
                    )})

                if ordr.get("side") == "B":
                    self._lst_orders_sent.append({"id": None, "cl_ord_id": self._profit_dll.send_sell_order(
                        conta=dct_pos_threads.get("broker").get("account"),
                        broker=dct_pos_threads.get("broker").get("id"),
                        senha=dct_pos_threads.get("broker").get("password"),
                        ativo=dct_pos_threads.get("symbol"),
                        bolsa=dct_pos_threads.get("stock_market"),
                        preco=self._lst_entry_signal[3][2],
                        qtd=ordr.get("traded_qtd")
                    )})
                else:
                    self._lst_orders_sent.append({"id": None, "cl_ord_id": self._profit_dll.send_buy_order(
                        conta=dct_pos_threads.get("broker").get("account"),
                        broker=dct_pos_threads.get("broker").get("id"),
                        senha=dct_pos_threads.get("broker").get("password"),
                        ativo=dct_pos_threads.get("symbol"),
                        bolsa=dct_pos_threads.get("stock_market"),
                        preco=self._lst_entry_signal[3][2],
                        qtd=ordr.get("traded_qtd")
                    )})

            """
                monitorar a fila de execução, se chegar a 80% enviar ordem stop e cancelar a ordem de saída GAIN.
            """
            while self._position_mgr.get_pos().get("qtd_open_positions"):
                self._position_mgr.proc_positions()

                lst_new_ordrs = [
                    ordr for pos in self._position_mgr.get_lst_positions(
                        [PositionMgr.POS_OPENED], [PositionMgr.POS_NEW, PositionMgr.POS_PRT_EXEC])
                    for ordr in pos.get("open_arms") if ordr.get("status") in ["bstNew", "bstPartiallyFilled"]
                ]

                '''
                order = {
                    "corretora": corretora, "qtd": qtd, "traded_qtd": traded_qtd, "leaves_qtd": leaves_qtd,
                    "side": side, "price": price, "stop_price": stop_price, "avg_price": avg_price, 
                    "profit_id": profit_id, "tipo_ordem": tipo_ordem, "conta": conta, "titular": titular, 
                    "cl_ord_id": cl_ord_id, "status": status, "date": date, "symbol": asset_id.ticker,
                }
                '''

                lst_sprd = self._dct_inst.get("spread")
                for ordr in lst_new_ordrs:
                    lst_book = lst_sprd[0] if ordr.get("side") == "" "B" else lst_sprd[0]

                    if lst_book[0][1] == ordr.get("price") and (lst_book[0][0] * 3) <= ordr.get("qtd"):
                        self._lst_orders_sent.append({"id": None, "cl_ord_id": self._profit_dll.send_cancel_order(
                            conta=dct_pos_threads.get("broker").get("account"),
                            broker=dct_pos_threads.get("broker").get("id"),
                            senha=dct_pos_threads.get("broker").get("password"),
                            cl_ord_id=ordr.get("cl_ord_id")
                        )})

                        if ordr.get("side") == "B":
                            self._lst_orders_sent.append({"id": None, "cl_ord_id": self._profit_dll.send_buy_order(
                                conta=dct_pos_threads.get("broker").get("account"),
                                broker=dct_pos_threads.get("broker").get("id"),
                                senha=dct_pos_threads.get("broker").get("password"),
                                ativo=dct_pos_threads.get("symbol"),
                                bolsa=dct_pos_threads.get("stock_market"),
                                preco=lst_book[0][1],
                                qtd=ordr.get("leaves_qtd")
                            )})

                        else:
                            self._lst_orders_sent.append({"id": None, "cl_ord_id": self._profit_dll.send_sell_order(
                                conta=dct_pos_threads.get("broker").get("account"),
                                broker=dct_pos_threads.get("broker").get("id"),
                                senha=dct_pos_threads.get("broker").get("password"),
                                ativo=dct_pos_threads.get("symbol"),
                                bolsa=dct_pos_threads.get("stock_market"),
                                preco=lst_book[0][1],
                                qtd=ordr.get("leaves_qtd")
                            )})
