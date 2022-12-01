from api.bots.hft.bot import Bot
from api.indep import InternalConfigProviders


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
        lst_lps = [self._dct_inst.get("lp")[0], self._dct_inst.get("lp")[1]]

    def execute(self):
        # TODO: preciso saber como detectar o tempo restante do leião e da fase randomica.

        # Aqui estou assumindo que entrou no leilão, na prorrogação ou fase randômica...
        if self._is_asset_state(["auctioned"]):
            if self._algo.get("threads")[0].get("has_ord_rem") and self._algo.get("threads")[1].get("has_ord_rem"):
                pass

        # A saída nunca será dentro do leilão, prorrogação ou fase randomica...
        if self._is_asset_state(["opened"]):
            lst_orders = self._get_lst_ord_cfg()
            if len(lst_orders) > 0:
                for ordr in lst_orders:
                    pass

        '''
            exemplo de calculo do saldo teórico remanecente do leilão. 
                        
            ADAPTAR PARA DOIS LIVROS DE PREÇOS (AQUI SÃO DOIS ATIVOS!).
        '''
        lst_lpc = [[1500, "Leilão"], [7000, 1575.5], [280, 1575.0], [200, 1574.5]]
        lst_lpv = [[1700, "Leilão"], [12000, 1575.5], [100, 1576.0], [300, 1576.5]]
        lst_lp = [lst_lpc, lst_lpv]

        qtd = lst_lp[0][0][0] - lst_lp[1][0][0] + lst_lp[0][1][0] - lst_lp[1][1][0]

        side = "B" if qtd > 0 else "S"
        qtd = abs(qtd)
        i = 2
        while True:

            if qtd <= 0:
                break

            try:
                if side == "B":
                    qtd -= lst_lp[1][i][0]
                else:
                    qtd -= lst_lp[0][i][0]
            except Exception:
                break

            i += 1

        print(f"side: {side} saldo final: {qtd} niveis p/ dentro: {i}")
