from api.bots.hft.bot import Bot
from api.jobs.internal_config_provider import InternalConfigProviders


class ArbitrageAuction(Bot):
    """
        For details on the B3 auction:
        https://www.bmf.com.br/bmfbovespa/pages/boletim1/bd_manual/RegrasPregao.asp
        https://www.bmf.com.br/bmfbovespa/pages/boletim1/bd_manual/Tunel_leilao.asp
        https://www.b3.com.br/pt_br/solucoes/plataformas/puma-trading-system/para-participantes-e-traders/regras-e-parametros-de-negociacao/parametros-dos-tuneis-de-negociacao/
        https://www.b3.com.br/pt_br/solucoes/plataformas/puma-trading-system/para-participantes-e-traders/regras-e-parametros-de-negociacao/tuneis-de-negociacao/

    """

    def __init__(self, name, daemon, algo: dict, config_prov: InternalConfigProviders):
        super().__init__(name, daemon, algo, Bot.TWO_ARM, config_prov)
        self._lst_lps = [self._dct_inst.get("lp")[0], self._dct_inst.get("lp")[1]]

    def execute(self):
        """
            A ideia de arbitrar leilões de ativo e devivativo parece ser interessante, entretanto, de logística
            bem mais complexa que a de um leilão simples.

            Além disso, este algoritmo não poderia rodar concorrentemente com o de leilão simples em uma mesma
            corretora (devido ao fato do risco de uma ordem enviada por ele poder zerar uma operação de leilão
            em andaento)

            Vou deixar esta ideia pausada por enquanto.

        """
        pass
