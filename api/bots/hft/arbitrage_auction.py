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
        super().__init__(name, daemon, algo, 2, config_prov)
        self._lst_lps = [self._dct_inst.get("lp")[0], self._dct_inst.get("lp")[1]]

    def execute(self):
        # TODO: preciso saber como detectar o tempo restante do leião e da fase randomica.
        pass
