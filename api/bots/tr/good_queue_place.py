from api.bots.bot import Bot
from api.jobs.internal_config_provider import InternalConfigProviders


class GoodQueuePlace(Bot):

    def __init__(self, name, daemon, algo: dict, config_prov: InternalConfigProviders):
        super().__init__(name, daemon, algo, Bot.ARM_ONE, config_prov)

        self._lst_lp = list(self._dct_inst.get("lp").values())
        self._lst_tt = list(self._dct_inst.get("tt").values())

    def _get_smaller_level(self):
        def find_level(lst_price_book: list):
            last_level_val = -1
            last_level_price = -1
            last_level_index = -1
            for i in range(len(lst_price_book) - 1):
                if last_level_val == -1 or lst_price_book[i][0] < last_level_val:
                    last_level_val = lst_price_book[i][0]
                    last_level_price = lst_price_book[i][1]
                    last_level_index = i

            return [last_level_val, last_level_price, last_level_index]

        return [find_level(self._lst_lp[0]), find_level(self._lst_lp[1])]

    def _execute(self):
        pass
        # entry point.
        """
        lst_lpc = [[7000, 1575.5], [280, 1575.0], [200, 1574.5], [50, 1574.0], [125, 1573.5], [160, 1573.0]]
        lst_lpv = [[12000, 1575.5], [100, 1576.0], [300, 1576.5], [200, 1577.0], [250, 1577.5], [125, 1578.0]]
        lst_lp = [lst_lpc, lst_lpv]
        
        def get_smaller_level(lst_lp: list):
            last_level_val = -1
            last_level_price = -1
            last_level_index = -1
            for i in range(len(lst_lp) - 1):
                if last_level_val == -1 or lst_lp[i][0] < last_level_val:
                    last_level_val = lst_lp[i][0]
                    last_level_price = lst_lp[i][1]
                    last_level_index = i
        
            return [last_level_val, last_level_price, last_level_index]
        
        lst_result = [get_smaller_level(lst_lpc), get_smaller_level(lst_lpv)]
        print(lst_result)
        
        
        qtd = lst_lp[0][0][0] - lst_lp[1][0][0] + lst_lp[0][1][0] - lst_lp[1][1][0]
        
        lst_niv_menor_liq = None
        side = "B" if qtd > 0 else "S"
        qtd = abs(qtd)
        nivel_p_dentro = 2
        while True:
            if qtd <= 0:
                break
        
            try:
                qtd_nivel = lst_lp[1][nivel_p_dentro][0] if side == "B" else lst_lp[0][nivel_p_dentro][0]
                qtd -= qtd_nivel
        
            except Exception:
                break
        
            if nivel_p_dentro == 2:
                lst_niv_menor_liq = [nivel_p_dentro, qtd_nivel]
        
            elif lst_niv_menor_liq[1] > qtd_nivel:
                lst_niv_menor_liq[0] = nivel_p_dentro
                lst_niv_menor_liq[1] = qtd_nivel
        
            nivel_p_dentro += 1
        
        print(f"side: {side} saldo final: {qtd} niveis p/ dentro: {nivel_p_dentro}")

        """

    def _thr_spread(self):
        pass

    def _thr_book(self):
        pass

    def _thr_order_flow(self):
        pass

    def _thr_scheduled_news(self):
        pass

    def _thr_breaking_news(self):
        pass
