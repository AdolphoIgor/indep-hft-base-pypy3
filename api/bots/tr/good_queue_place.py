from api.bots.bot import Bot

from api.bots.tr.tr_bot import TRBot
from api.jobs.internal_config_provider import InternalConfigProviders


class GoodQueuePlace(TRBot):

    def __init__(self, name, daemon, algo: dict, config_prov: InternalConfigProviders):
        super().__init__(name, daemon, algo, Bot.ONE_ARM, config_prov)

    def _execute(self):
        def get_smaller_level():
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

            lst_lp = self._dct_inst.get("lp")
            return [find_level(lst_lp[0]), find_level(lst_lp[1])]

        # entry point.
        self._arms = self._position_mgr.get_pos_arms()
        if not self._is_asset_state(["opened"]) and self._position_mgr.get_pos().get("qtd_open_positions") == 0:
            return
        '''
        if self._arms[0].get("position").get("has_ord_rem"):
            
            lst_levels = get_smaller_level()
            
            # TODO: À cada passada, mesmo que haja ordem pendurada, deve verificar se há uma vaga melhor e mais
            #  perto do preço, se houver, deve muda-la de lugar. Isso sifnifica que deve manter historico fácil e rapido
            #  de onde eventual ordem pendurada anteriormente está! No Livro de Ofertas dá pra saber a posicao atual
            #  da ordem.

            # TODO: A melhor estratégia é colocar uma ordem de cada lado no book.

            if lst_mm[3] and lst_lp[1][0][1] <= self._qtd_ff:
                lst_sides = [lst_lp[1][0][0], lst_lp[1][1][0], lst_lp[0][0][0]]

                self._lst_orders_sent.append({"id": timestamp, "cl_ord_id": self._profit_dll.send_buy_order(
                    conta=self._tpl_arm[0], broker=self._tpl_arm[1], senha=self._tpl_arm[2], ativo=self._tpl_arm[3],
                    bolsa=self._tpl_arm[4], preco=lst_sides[0], qtd=self._tpl_arm[5])})

                # sell
            elif lst_mm[4] and lst_lp[0][0][1] <= self._qtd_ff:
                lst_sides = [lst_lp[0][0][0], lst_lp[0][1][0], lst_lp[1][0][0]]

                self._lst_orders_sent.append({"id": timestamp, "cl_ord_id": self._profit_dll.send_sell_order(
                    conta=self._tpl_arm[0], broker=self._tpl_arm[1], senha=self._tpl_arm[2], ativo=self._tpl_arm[3],
                    bolsa=self._tpl_arm[4], preco=lst_sides[0], qtd=self._tpl_arm[5])})


        else:

            #TODO: é preciso ficar atento ao momentum de modo a saber que lado pendurar a ordem da saída e
            # que lado cancelar a ordem pendurada caso ela esteja muito perto do topo do book e na direção
            # oposta do momentum.
            pass
        '''