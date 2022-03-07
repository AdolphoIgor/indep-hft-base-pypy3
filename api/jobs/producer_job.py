import threading
import time
from datetime import datetime

from api.jobs.job import Job


class ProducerJob(Job):

    def __init__(self, logger, dict_configs, lst_config_pool, lst_thread_pool, **kwargs):
        super().__init__(logger, dict_configs, lst_config_pool, lst_thread_pool)
        self.__encoder = kwargs.get("encoder")
        self.__sleep_when_done = kwargs.get("sleep_when_done")
        self.__log_market_data_cfg_path = kwargs.get("log_market_data_cfg_path")
        self.__log_oms_cfg_path = kwargs.get("log_oms_cfg_path")

    def run(self) -> None:
        """
            The producer has to get the market data from the provider as fast as possible, in order to do that
            it'll get from self._dict_configs connections established by the congurator thread and subscribed
            by the subscriber thread and start to feed every global_provider_queue variable from each valid connection.

            There is no wait between the loop iterations and the received data will be kept into a Queue object
            (which is tread-safe) to be consumed to the especialized threads.
        """

        def __process_producer(i_conn, i_queue, i_path, i_name, i_encoder, i_keep_running):
            while i_keep_running:
                with open(i_path, mode='a', encoding=i_encoder) as log_file:
                    try:
                        msg = i_conn.read_until(match=b"!").decode(i_encoder)
                        i_queue.put_nowait(msg)
                        log_file.write(msg)
                        log_file.flush()
                        time.sleep(0.001)
                    except (ConnectionResetError, EOFError):
                        pass

            self._logger.info(f"Thread {i_name} was finalized.")

        self._logger.info("Initializing the Producer...")

        while self._keep_running:

            configs = self._dict_configs.get("configs", {})
            if not configs.get("online", False):
                time.sleep(self.__sleep_when_done)
                continue

            level = None
            lst_scheduling = self._dict_configs.get('scheduling')
            for sch in lst_scheduling:
                if sch.get("job", None) == "Producer":
                    level = float(f'{sch.get("order")}.0')
                    break

            if level is None:
                break

            prdr_name = "market_data_providers"
            for provider in configs.get(prdr_name, []):

                lst_md_providers, lst_md_sel_providers, dct_md_prvd = \
                    self._get_internal_provider_data(prdr_name, provider.get("id"))

                if dct_md_prvd.get("connected", False):
                    conn = dct_md_prvd.get("global_provider_conn", None).get_connection()

                    if conn is None:
                        time.sleep(1)
                        continue

                    actives = 0
                    for symbol in dct_md_prvd.get("symbols", []):
                        if symbol.get("registered"):
                            for instrument in symbol.get("instruments", []):
                                if instrument.get("registered", False):
                                    actives = actives + 1
                                    break

                        if actives > 0:
                            break

                    if actives > 0 and not dct_md_prvd.get("producer_running", False):
                        queue = dct_md_prvd.get("global_provider_queue", None)
                        if queue is not None:
                            prov = provider.get("name").replace(" ", '').lower()
                            path = f'{self.__log_market_data_cfg_path}{datetime.now().strftime("%Y%m%d")}' \
                                   f'_{prov}_marketdata_log_raw.txt'

                            name = f"thr_producer_md_{provider.get('id')}_{prov}"
                            thr_ = threading.Thread(
                                target=__process_producer, name=name, args=(conn, queue, path, name, self.__encoder,
                                                                            self._keep_running))
                            self._lst_thread_pool.append({"name": name, "level": level + 0.1, "pointer": thr_})
                            thr_.start()
                            self._logger.info(f"Initializing the thread {name}...")
                            dct_md_prvd["producer_running"] = True

                    time.sleep(0.01)

            time.sleep(self.__sleep_when_done)

        self._logger.info("Producer was finalized.")
