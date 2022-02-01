import time
from datetime import datetime
from queue import Queue

from api.config.providers.oms.cedro.src.oms_cedro import CedroOMSProviderBasic
from api.io.network.connection_factory import ConnectionFactory
from api.jobs.job import Job


class ConfiguratorJob(Job):
    _lst_cls = [CedroOMSProviderBasic]

    def __init__(self, logger, dict_configs, lst_config_pool, lst_thread_pool, **kwargs):
        super().__init__(logger, dict_configs, lst_config_pool, lst_thread_pool)
        self.__encoder = kwargs.get("encoder")
        self.__sleep_when_done = kwargs.get("sleep_when_done")
        self.__log_market_data_cfg_path = kwargs.get("log_market_data_cfg_path")
        self.__log_oms_cfg_path = kwargs.get("log_oms_cfg_path")

    def run(self) -> None:
        """
            The configurator has to keep track of all marketdata, oms, ftp, etc... instances and must terminate them
            when the system has to shut down.
        """
        self._logger.info("Initializing the Configurator...")

        while self._keep_running:

            configs = self._dict_configs.get("configs", {})

            prdr_name = "market_data_providers"
            lst_md_providers = None
            for provider in configs.get(prdr_name, []):

                for connection in provider.get("connection", {}):

                    lst_md_providers, lst_md_sel_providers, dct_md_prvd = \
                        self._get_internal_provider_data(prdr_name, provider.get("id"))

                    ''' If the system was requested to shutdown (online was changed), this will do it smoothly by ending  
                        every thread's infinite loop. 
    
                        If a particular provider connection is disabled (enabled turned false) is necessary to close its
                        conection and eliminate evey queue and lists of instruments, also its important to resume every 
                        thread involved into.                             
                    '''
                    if not configs.get("online", False) or \
                            (dct_md_prvd.get("connected", False) and not connection.get("enabled")):

                        self._keep_running = False

                        if dct_md_prvd.get("connected", False):
                            dct_md_prvd["connected"] = False
                            dct_md_prvd["global_provider_conn"].disconnect()
                            dct_md_prvd["global_provider_queue"] = None

                            for symbol in dct_md_prvd.get("symbols", []):
                                for instrument in symbol.get("instruments", []):
                                    instrument['instrument'] = None
                                    instrument['registered'] = False

                            self._logger.info(f"The connection to MD {provider.get('name')} was terminated.")

                    else:
                        ''' The system turning online. It starts connection, queues and lists. '''
                        if not dct_md_prvd.get("connected", False) and connection.get("enabled"):
                            dct_md_prvd["id"] = provider.get("id")
                            dct_md_prvd["connected"] = False

                            if connection.get("type").lower() == "telnet":
                                for host in connection.get("hosts"):

                                    md_prov = ConnectionFactory.get_connection(
                                        host=host.get("host", None),
                                        port=host.get("port", None),
                                        user=connection.get('username', ''),
                                        pwd=connection.get('password', ''),
                                        conn_type=ConnectionFactory.CONNECTION_TYPE.get("TELNET")
                                    )

                                    dct_md_prvd["connected"] = md_prov.is_connected()

                                    if dct_md_prvd["connected"]:
                                        dct_md_prvd["global_provider_conn"] = md_prov
                                        dct_md_prvd["global_provider_queue"] = Queue()
                                        break

                            if dct_md_prvd.get("connected", False):
                                lst_intrnl_symbol = dct_md_prvd.get("symbols", [])
                                for symbol in provider.get("symbols", []):
                                    if symbol.get("enabled", False):
                                        instr = [
                                            {
                                                "type": instrument.get("type"),
                                                "instrument": {},
                                                "registered": False
                                            }
                                            for instrument in symbol.get("instruments") if
                                            instrument.get("enabled", False)
                                        ]

                                        dct_sbl = {
                                            "symbol": symbol.get("symbol"),
                                            "registered": True,
                                            "instruments": instr
                                        }

                                        lst_intrnl_symbol.append(dct_sbl)
                                        dct_md_prvd["symbols"] = lst_intrnl_symbol

                                lst_md_providers.append(dct_md_prvd)
                                self._logger.info(f"The connection to MD {provider.get('name')} was established.")

                    time.sleep(0.01)

            ''' Writes the current configuration in a report file. '''
            f_path = f'{self.__log_market_data_cfg_path}{datetime.now().strftime("%Y%m%d")}_marketdata_log_config.txt'
            with open(f_path, 'a', encoding=self.__encoder) as f:
                f.truncate(0)
                f.seek(0)
                dt = datetime.now().strftime("%Y%m%d %H%M%S.%f")
                f.write(f"'{dt}': {str(self._dict_configs)}\r\n")
                f.write(f"'{dt}': {str(lst_md_providers)}\r\n")

            prdr_name = "oms_providers"
            lst_oms_providers = None
            for provider in configs.get(prdr_name, []):

                connection = provider.get("connection", {})

                lst_oms_providers, lst_oms_sel_providers, dct_oms_prvd = \
                    self._get_internal_provider_data(prdr_name, provider.get("id"))

                ''' If the system was requested to shutdown (online was changed), this will do it smoothly by ending  
                    every thread's infinite loop.  

                    If a particular provider connection is disabled (enabled turned false) is necessary to close its
                    conection and eliminate evey queue and lists of instruments, also its important to resume every 
                    thread involved into.                            
                '''
                if not configs.get("online", False) or \
                        dct_oms_prvd.get("connected", False) and not connection.get("enabled"):

                    if dct_oms_prvd.get("connected", False):
                        for symbol in dct_oms_prvd.get("running_algos", []):
                            for order in symbol.get("orders", []):
                                pass
                                # TODO: Aqui preciso fechar todas as ordens ainda abertas.

                        lst_brokers = dct_oms_prvd.get("global_provider_lst_brokers_conn", [])
                        for broker in lst_brokers:
                            broker.logout()

                        lst_brokers.clear()

                        dct_oms_prvd["global_provider_decoder"] = None
                        dct_oms_prvd["global_provider_queue"] = None
                        dct_oms_prvd["global_provider_conn"].disconnect()
                        dct_oms_prvd["connected"] = False

                        self._logger.info(f"The connection to OMS {provider.get('name')} was terminated.")

                else:
                    ''' The system turning online. It starts connection, queues and lists. '''
                    if not dct_oms_prvd.get("connected", False) and connection.get("enabled"):
                        dct_oms_prvd["id"] = provider.get("id")
                        dct_oms_prvd["connected"] = False

                        if connection.get("type").lower() == "telnet":
                            oms_prov = None
                            for host in connection.get("hosts"):
                                oms_prov = ConnectionFactory.get_connection(
                                    host=host.get("host", None),
                                    port=host.get("port", None),
                                    user=connection.get('username', ''),
                                    pwd=connection.get('password', ''),
                                    conn_type=ConnectionFactory.CONNECTION_TYPE.get("TELNET")
                                )

                                dct_oms_prvd["connected"] = oms_prov.is_connected()
                                dct_oms_prvd["global_provider_decoder"] = \
                                    eval(f"{provider.get('configurator_class_decoder')}()")

                            if dct_oms_prvd["connected"]:
                                dct_oms_prvd["global_provider_conn"] = oms_prov
                                dct_oms_prvd["global_provider_queue"] = Queue()

                                lst_oms_brkrs_conn = []
                                for broker in dct_oms_prvd.get("brokers"):
                                    if not broker.get("enabled", False):
                                        continue

                                    cls_prv = eval(f"{dct_oms_prvd.get('configurator_class')}("
                                                   f"conn={oms_prov},"
                                                   f"**{broker}).logon()")

                                    # internally, every broker-and-algo message will be distinguished by the
                                    # SenderSubID tag in the received message.
                                    lst_oms_brkrs_conn.append({"broker_id": broker.get("id"),
                                                               "broker_name": broker.get("name"),
                                                               "cls_ptr": cls_prv})

                                # Brokers are only used to send orders with its id tags within, the returned messages
                                # will be decoded by a CedroOMSProviderBasic class then spread in the proper broker's
                                # received list.
                                dct_oms_prvd["global_provider_lst_brokers_conn"] = lst_oms_brkrs_conn
                                self._logger.info(f"The connection to OMS {provider.get('name')} was established.")
                                break

                            lst_oms_providers.append(dct_oms_prvd)

                    time.sleep(0.01)

            ''' Writes the current configuration in a report file. '''
            f_path = f'{self.__log_oms_cfg_path}{datetime.now().strftime("%Y%m%d")}_oms_log_config.txt'
            with open(f_path, 'a', encoding=self.__encoder) as f:
                f.truncate(0)
                f.seek(0)
                dt = datetime.now().strftime("%Y%m%d %H%M%S.%f")
                f.write(f"'{dt}': {str(self._dict_configs)}\r\n")
                f.write(f"'{dt}': {str(lst_oms_providers)}\r\n")

            time.sleep(self.__sleep_when_done)

        self._logger.info("Configurator was finalized.")
