import threading
import time
from datetime import datetime

from api.jobs.job import Job


class OmsSenderJob(Job):

    def __init__(self, logger, dict_configs, lst_config_pool, lst_thread_pool, **kwargs):
        super().__init__(logger, dict_configs, lst_config_pool, lst_thread_pool)
        self.__encoder = kwargs.get("encoder")
        self.__sleep_when_done = kwargs.get("sleep_when_done")
        self.__log_oms_raw_path = kwargs.get("log_oms_raw_path")

    def run(self) -> None:
        """
            OMS sender just read every oms_providers->provider to find orders in orders->send[] and push then into
            the OMS's connection. Keep in mind that the orders are placed in send[] by the bots/algo/lft/hft.
        """

        def __process_oms_sender(i_dct_md_prvd, i_f_path, i_name, i_encoder, i_keep_running):
            lst_brokers = i_dct_md_prvd.get("global_provider_lst_brokers_conn", [])
            with open(i_f_path, 'a', encoding=i_encoder) as fl:
                while i_keep_running:
                    for dct_algo_ordr in i_dct_md_prvd.get('orders', []):
                        lst_send = dct_algo_ordr.get("orders", {}).get("send", [])
                        for ordr in lst_send:
                            for brkr in lst_brokers:
                                if brkr.get("broker_id", "") == dct_algo_ordr.get("thread_broker_id", ""):
                                    brkr.get("cls_ptr").execute(ordr)
                                    dct_algo_ordr.get("orders", {}).get("sent").append(ordr)
                                    lst_send.remove(ordr)
                                    dt = datetime.now().strftime("%Y%m%d %H%M%S.%f")
                                    fl.write(f"'{dt}': {str(ordr)}\r\n")
                                    fl.flush()
                                    time.sleep(0.01)
                                    break

                        time.sleep(0.01)
                    time.sleep(0.01)

            self._logger.info(f"Thread {i_name} was finalized.")

        self._logger.info("Initializing the OMS Sender...")

        while self._keep_running:

            configs = self._dict_configs.get("configs", {})
            if len(configs) == 0:
                time.sleep(1)
                continue

            prdr_name = "oms_providers"
            for provider in configs.get(prdr_name, []):

                lst_oms_providers, lst_oms_sel_providers, dct_oms_prvd = \
                    self._get_internal_provider_data(prdr_name, provider.get("id"))

                if dct_oms_prvd.get("connected", False):
                    conn = dct_oms_prvd.get("global_provider_conn", None).get_connection()

                    if conn is None:
                        time.sleep(1)
                        continue

                if not dct_oms_prvd.get("oms_provider_running", False) and \
                        dct_oms_prvd.get("global_provider_queue", None) is not None and \
                        len(dct_oms_prvd.get("global_provider_lst_brokers_conn", [])) > 0:
                    prov = provider.get("name").replace(" ", '').lower()
                    name = f"thr__oms_sender_{provider.get('id')}_{prov}"
                    path = f'{self.__log_oms_raw_path}{datetime.now().strftime("%Y%m%d")}_{prov}_oms_log_raw_sent.txt'
                    thr_ = threading.Thread(
                        target=__process_oms_sender, name=name,
                        args=(dct_oms_prvd, path, name, self.__encoder, self._keep_running))
                    self._lst_thread_pool.append({"name": name, "level": 4.1, "pointer": thr_})
                    thr_.start()
                    self._logger.info(f"Initializing the thread {name}...")
                    dct_oms_prvd["oms_provider_running"] = True

                time.sleep(0.01)

            time.sleep(self.__sleep_when_done)

        self._logger.info("OMS Sender was finalized.")
