from api.bots.bot import Bot
from api.bots.tr.position import PositionMgr
from api.jobs.internal_config_provider import InternalConfigProviders


class TRBot(Bot):

    _lst_orders_sent = []

    def __init__(self, name, daemon, algo: dict, qtd_exp: int, config_prov: InternalConfigProviders):
        super().__init__(name, daemon, algo, qtd_exp, config_prov)

        self._position_mgr = PositionMgr(self._lst_orders_sent, algo, self._dct_ord_status, config_prov)
