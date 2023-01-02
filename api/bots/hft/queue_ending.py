from api.bots.hft.bot import Bot
from api.bots.hft.bot_momentum import BotMomentum
from api.jobs.internal_config_provider import InternalConfigProviders


class QueueEnding(BotMomentum):

    def __init__(self, name, daemon, algo: dict, config_prov: InternalConfigProviders):
        super().__init__(name, daemon, algo, Bot.ONE_ARM, config_prov)

    def execute(self):
        """
           Agredir fim de fila é uma estratégia interessante apenas para ativos com pouca liquidez nas filas, situação
           onde, mesmo pendurando a saída na ultima posição da fila, ainda é possivel ser zerado rapidamente por conta
           da falta de liquidez.

           Desafio: tem qu ler o fluxo de ordens para saber de que lado entrar

           Recomendação: INDICE, MINI-INDICE, DOLAR E MINI-DOLAR (Na situação de dolar @ R$ 4,00~6,00.), ações e opções
           com baixa liquidez.

        """

        lst_lp = self._dct_inst.get("lp")
        self._momentum.get_momentum(lst_lp)

        # lst_tt.append([trade_number, date, price, qtd, buy_agent, sell_agent])
