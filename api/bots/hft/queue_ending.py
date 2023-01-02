from datetime import datetime

from api.bots.hft.bot import Bot
from api.bots.hft.bot_momentum import BotMomentum
from api.jobs.internal_config_provider import InternalConfigProviders


class QueueEnding(BotMomentum):

    def __init__(self, name, daemon, algo: dict, config_prov: InternalConfigProviders):
        super().__init__(name, daemon, algo, Bot.ONE_ARM, config_prov)

        self._arms = self._position_mgr.get_pos_arms()
        self._tpl_arm = (
            self._arms[0].get("broker").get("account"),
            self._arms[0].get("broker").get("id"),
            self._arms[0].get("broker").get("password"),
            self._arms[0].get("symbol"),
            self._arms[0].get("stock_market"),
            self._arms[0].get("start_param").get("order_op_qty")
        )
        self._qtd_ff = self._arms[0].get("start_param").get("order_op_qty") * 3

    def _execute(self):
        """
           Agredir fim de fila é uma estratégia interessante apenas para ativos com pouca liquidez nas filas, situação
           onde, mesmo pendurando a saída na ultima posição da fila, ainda é possivel ser zerado rapidamente por conta
           da falta de liquidez.

           Desafio: tem qu ler o fluxo de ordens para saber de que lado entrar

           Recomendação: INDICE, MINI-INDICE, DOLAR E MINI-DOLAR (Na situação de dolar @ R$ 4,00~6,00.), ações e opções
           com baixa liquidez.

        """
        # entry point.
        self._arms = self._position_mgr.get_pos_arms()
        if self._is_asset_state(["opened"]) and self._arms[0].get("position").get("has_ord_rem"):
            lst_lp = self._dct_inst.get("lp")
            lst_mm = self._momentum.get_momentum(self._dct_inst.get("tt"))
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")

            # [[[price, qtd, count], [price, qtd, count]], [[price, qtd, count], [price, qtd, count]]]
            # buy
            if lst_mm[3] and lst_lp[0][0][1] <= self._qtd_ff:
                self._lst_orders_sent.append({"id": timestamp, "cl_ord_id": self._profit_dll.send_buy_order(
                    conta=self._tpl_arm[0], broker=self._tpl_arm[1], senha=self._tpl_arm[2], ativo=self._tpl_arm[3],
                    bolsa=self._tpl_arm[4], preco=lst_lp[0][0][0], qtd=self._tpl_arm[5]
                )})
                self._lst_orders_sent.append({"id": timestamp, "cl_ord_id": self._profit_dll.send_sell_order(
                    conta=self._tpl_arm[0], broker=self._tpl_arm[1], senha=self._tpl_arm[2], ativo=self._tpl_arm[3],
                    bolsa=self._tpl_arm[4], preco=lst_lp[0][0][1], qtd=self._tpl_arm[5]
                )})

            # sell
            elif lst_mm[4] and lst_lp[1][1] <= self._qtd_ff:
                self._lst_orders_sent.append({"id": timestamp, "cl_ord_id": self._profit_dll.send_sell_order(
                    conta=self._tpl_arm[0], broker=self._tpl_arm[1], senha=self._tpl_arm[2], ativo=self._tpl_arm[3],
                    bolsa=self._tpl_arm[4], preco=lst_lp[1][0][0], qtd=self._tpl_arm[5]
                )})
                self._lst_orders_sent.append({"id": timestamp, "cl_ord_id": self._profit_dll.send_buy_order(
                    conta=self._tpl_arm[0], broker=self._tpl_arm[1], senha=self._tpl_arm[2], ativo=self._tpl_arm[3],
                    bolsa=self._tpl_arm[4], preco=lst_lp[1][0][1], qtd=self._tpl_arm[5]
                )})

        self._position_mgr.proc_positions()

        # exit point.
        # TODO:
        #  fazer a saida (monitorar fila para zerar no primeiro tick contra.
