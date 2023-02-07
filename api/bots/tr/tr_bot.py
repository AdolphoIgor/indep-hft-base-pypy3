import threading

from api.bots.bot import Bot
from api.jobs.internal_config_provider import InternalConfigProviders


class TRBot(Bot):

    def __init__(self, name, daemon, algo: dict, qtd_exp: int, config_prov: InternalConfigProviders):
        super().__init__(name, daemon, algo, qtd_exp, config_prov)

        self._lst_threads = []
        self._dct_threads = {}

    def _execute(self):
        """
            Manages the whole operation. Calls the callback methods to give the subclass the ability to do what
            they need. Subclass has no need to implement this method.
        :return:
        """
        def create_thread(thr_name, thr_target):
            thr = threading.Thread(target=thr_target, name=thr_name, daemon=True, args=(thr_name,))
            self._lst_threads.append(thr)
            thr.start()

        create_thread("0_MANGR_SPREAD", self._thr_spread)
        create_thread("1_MANGR_BOOK", self._thr_book)
        create_thread("2_MANGR_ORD_FLOW", self._thr_order_flow)
        create_thread("3_MANGR_NEWS", self._thr_scheduled_news)
        create_thread("4_MANGR_BRK_NEWS", self._thr_breaking_news)

    def _thr_spread(self, name):
        """
            Manages the operations on the top of the book (only), so, gets the highest priority of any other threads.
        :return:
        """
        pass

    def _thr_book(self, name):
        """
            Manages to find the best queue place at the closer prices as possible.
        :return:
        """
        pass

    def _thr_order_flow(self, name):
        """
            Manages to alert the main thread to cancel and or exit current operations if an unusual strong income flow
            in the correlated assets were detected;
        :return:
        """
        pass

    def _thr_scheduled_news(self, name):
        """
            Manages to alert the main thread to cancel and or exit current operations when a high volatility scheduled
            report is about to be announced.
        :return:
        """
        pass

    def _thr_breaking_news(self, name):
        """
            Manages to alert the main thread to cancel and or exit current operations when important breakiung news
            is announced.
        :return:
        """
        pass
