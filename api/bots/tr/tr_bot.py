from api.bots.bot import Bot
from api.bots.tr.position import PositionMgr
from api.jobs.internal_config_provider import InternalConfigProviders


class TRBot(Bot):

    _lst_orders_sent = []

    def __init__(self, name, daemon, algo: dict, qtd_exp: int, config_prov: InternalConfigProviders):
        super().__init__(name, daemon, algo, qtd_exp, config_prov)

    def _execute(self):
        """
            Manages the whole operation. Calls the callback methods to give the subclass the ability to do what
            they need. Subclass has no need to implement this method.
        :return:
        """
        pass

    def _thr_spread(self):
        """
            Manages the operations on the top of the book (only), so, gets the highest priority of any other threads.
        :return:
        """
        pass

    def _thr_book(self):
        """
            Manages to find the best queue place at the closer prices as possible.
        :return:
        """
        pass

    def _thr_order_flow(self):
        """
            Manages to alert the main thread to cancel and or exit current operations if an unusual strong income flow
            in the correlated assets were detected;
        :return:
        """
        pass

    def _thr_scheduled_news(self):
        """
            Manages to alert the main thread to cancel and or exit current operations when a high volatility scheduled
            report is about to be announced.
        :return:
        """
        pass

    def _thr_breaking_news(self):
        """
            Manages to alert the main thread to cancel and or exit current operations when important breakiung news
            is announced.
        :return:
        """
        pass
