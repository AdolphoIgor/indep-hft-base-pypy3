import threading
import time
from datetime import datetime

from api.config.providers.market_data.crystal_data_feed.src.crystal_data_feed_provider import CrystalDataFeedProvider
from api.jobs.job import Job


class DistributorJob(Job):
    __lst_imports = [CrystalDataFeedProvider]

    def __init__(self, logger, dict_configs, lst_config_pool, lst_thread_pool, **kwargs):
        super().__init__(logger, dict_configs, lst_config_pool, lst_thread_pool)
        self.__encoder = kwargs.get("encoder")
        self.__sleep_when_done = kwargs.get("sleep_when_done")
        self.__log_market_data_path = kwargs.get("log_market_data_path")
        self.__log_oms_path = kwargs.get("log_oms_path")

    def run(self) -> None:
        """
          The distributor consumes every global_provider_queue from self._dict_configs and distributes each item
          acoordingly of its symbol to its private queue doing so, every private queue will be consumed by a specialized
          thread therefore recriating instruments from the messages received form de market data.

        """

        def __process_md_distributor(i_global_queue, i_dct_md_prvd, i_lst_files, i_f_path, i_configurator,
                                     i_name, i_encoder, i_keep_running):
            while i_keep_running:
                symbol_queue = []
                while not i_global_queue.empty() and i_keep_running:
                    if len(symbol_queue) == 0:
                        for symbol in i_dct_md_prvd.get("symbols", []):
                            lst = symbol.get("instruments", None)
                            if symbol.get("registered", False) and lst is not None:
                                symbol_queue.append((symbol.get("symbol", None), lst))

                    if len(symbol_queue) == 0:
                        time.sleep(1)
                        continue

                    instruments = i_configurator.decode(i_global_queue.get())
                    for instrument in instruments:
                        for symbol, sbl_lst in symbol_queue:
                            ticker = instrument.get("symbol").upper()
                            if ticker == symbol.upper():
                                for to_inst in sbl_lst:
                                    inst_type = to_inst.get("type").upper()
                                    if inst_type == instrument.get("type").upper():
                                        lst_inst_file = list(filter(lambda x:
                                                                    x.get("symbol").upper() == ticker and
                                                                    x.get("type").upper() == inst_type, i_lst_files))

                                        if len(lst_inst_file) == 0:
                                            inst_fl = open(i_f_path.format(ticker, inst_type), 'a', encoding=i_encoder)
                                            i_lst_files.append({"symbol": ticker, "type": inst_type, "file": inst_fl})
                                        else:
                                            inst_fl = lst_inst_file[0].get("file", None)

                                        instr_data = to_inst.get("instrument", {})
                                        instr_data.update(instrument)
                                        to_inst["instrument"] = instr_data
                                        dt = datetime.now().strftime("%Y%m%d %H%M%S.%f")
                                        inst_fl.write(f"'{dt}': {str(instr_data)}\r\n")
                                        inst_fl.flush()
                                        time.sleep(0.01)
                                        break
                                break

                time.sleep(0.1)
            self._logger.info(f"Thread {i_name} was finalized.")

        def __process_oms_distributor(i_dct_md_prvd, i_f_path, i_name, i_encoder, i_keep_running):
            queue = i_dct_md_prvd.get("global_provider_queue", None)
            decoder = i_dct_md_prvd.get("global_provider_decoder", None)
            while i_keep_running:
                with open(i_f_path, 'a', encoding=i_encoder) as fl:
                    while not queue.empty() and i_keep_running:
                        lst_msgs = decoder.decode(queue.get())
                        for msg in lst_msgs:
                            # I'm pushing the error in case the SenderSubID has not present.
                            # pattern: lst_sender = [OMS_NAME, BROKER_ID, (optional: ALGO_NAME)]
                            lst_sender = decoder.decode_sender_id(msg['SenderSubID'])

                            for dct_algo_ordr in i_dct_md_prvd.get('orders', []):
                                if dct_algo_ordr.get("algo_name") == lst_sender[2] and \
                                        dct_algo_ordr.get("thread_broker_id") == lst_sender[1]:
                                    dct_algo_ordr.get("orders", {}).get("received").append(msg)
                                    dt = datetime.now().strftime("%Y%m%d %H%M%S.%f")
                                    fl.write(f"'{dt}': {str(msg)}\r\n")
                                    fl.flush()
                                    time.sleep(0.01)
                                    break

                time.sleep(0.1)
            self._logger.info(f"Thread {i_name} was finalized.")

        self._logger.info("Initializing the Distributor...")

        while self._keep_running:

            configs = self._dict_configs.get("configs", {})
            if len(configs) == 0:
                time.sleep(1)
                continue

            '''
            ---------------------------------------------------------------------------------------    
            Distributor engine for Market data messages.
            --------------------------------------------------------------------------------------- 
            '''
            lst_md_files = []
            prdr_name = "market_data_providers"
            for provider in configs.get(prdr_name, []):
                lst_md_providers, lst_md_sel_providers, dct_md_prvd = \
                    self._get_internal_provider_data(prdr_name, provider.get("id"))

                global_queue = None
                if dct_md_prvd.get("connected", False):
                    global_queue = dct_md_prvd.get("global_provider_queue", None)

                if global_queue is None or global_queue.empty():
                    time.sleep(1)
                    continue

                if not dct_md_prvd.get("distributor_running", False):
                    configurator = eval(f'{provider.get("configurator_class")}()')
                    prov = provider.get("name").replace(" ", '').lower()
                    f_path = f'{self.__log_market_data_path}{datetime.now().strftime("%Y%m%d%H")}' + \
                             f'_{prov}' + '_marketdata_log_data_{0}_{1}.txt'
                    name = f"thr_distributor_md_{provider.get('id')}_{prov}"
                    thr_ = threading.Thread(
                        target=__process_md_distributor, name=name,
                        args=(global_queue, dct_md_prvd, lst_md_files, f_path, configurator, name, self.__encoder,
                              self._keep_running))
                    self._lst_thread_pool.append({"name": name, "level": 3.1, "pointer": thr_})
                    thr_.start()
                    self._logger.info(f"Initializing the thread {name}...")
                    dct_md_prvd["distributor_running"] = True

                time.sleep(0.01)

            '''
            ---------------------------------------------------------------------------------------    
            Distributor engine for OMS messages.
            --------------------------------------------------------------------------------------- 
            '''
            prdr_name = "oms_providers"
            for provider in configs.get(prdr_name, []):

                lst_oms_providers, lst_oms_sel_providers, dct_oms_prvd = \
                    self._get_internal_provider_data(prdr_name, provider.get("id"))

                if dct_oms_prvd.get("connected", False):
                    conn = dct_oms_prvd.get("global_provider_conn", None).get_connection()

                    if conn is None:
                        time.sleep(1)
                        continue

                if not dct_oms_prvd.get("producer_running", False) and \
                        dct_oms_prvd.get("global_provider_queue", None) is not None and \
                        dct_oms_prvd.get("global_provider_decoder", None) is not None:
                    prov = provider.get("name").replace(" ", '').lower()
                    name = f"thr_distributor_md_{provider.get('id')}_{prov}"
                    f_path = f'{self.__log_oms_path}{datetime.now().strftime("%Y%m%d%H")}' + \
                             f'_{prov}' + '_oms_log_data.txt'
                    thr_ = threading.Thread(
                        target=__process_oms_distributor, name=name,
                        args=(dct_oms_prvd, f_path, name, self.__encoder, self._keep_running))
                    self._lst_thread_pool.append({"name": name, "level": 3.2, "pointer": thr_})
                    thr_.start()
                    self._logger.info(f"Initializing the thread {name}...")
                    dct_oms_prvd["distributor_running"] = True

                time.sleep(0.01)

            time.sleep(self.__sleep_when_done)

        self._logger.info("Distributor was finalized.")
