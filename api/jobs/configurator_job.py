import time
from datetime import datetime
from queue import Queue

from api.config.providers.oms.cedro.src.oms_cedro import CedroOMSProviderBasic, CedroOMSProvider
from api.io.network.connection_factory import ConnectionFactory
from api.jobs.job import Job


class ConfiguratorJob(Job):
    _lst_cls = [CedroOMSProviderBasic, CedroOMSProvider]

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
            if not configs.get("online", False):
                time.sleep(self.__sleep_when_done)
                continue

            prdr_name = "market_data_providers"
            lst_md_providers = None
            for provider in configs.get(prdr_name, []):

                for connection in provider.get("connections", {}):

                    lst_md_providers, _, dct_md_prvd = self._get_internal_provider_data(prdr_name, provider.get("id"))

                    ''' If the system was requested to shutdown (online was changed), this will do it smoothly by ending  
                        every thread's infinite loop. 
    
                        If a particular provider connection is disabled (enabled turned false) is necessary to close its
                        conection and eliminate evey queue and lists of instruments, also its important to resume every 
                        thread involved into.                             
                    '''
                    if dct_md_prvd.get("connected", False) and not connection.get("enabled"):

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

                lst_oms_providers, _, dct_oms_prvd = self._get_internal_provider_data(prdr_name, provider.get("id"))

                ''' If the system was requested to shutdown (online was changed), this will do it smoothly by ending  
                    every thread's infinite loop.  

                    If a particular provider connection is disabled (enabled turned false) is necessary to close its
                    conection and eliminate evey queue and lists of instruments, also its important to resume every 
                    thread involved into.                            
                '''
                connections = provider.get("connections", {})
                for conn in connections:
                    for host in conn.get("hosts", []):

                        if dct_oms_prvd.get("connected", False) and not host.get("enabled"):

                            if dct_oms_prvd.get("connected", False):
                                dct_oms_prvd["global_provider_decoder"] = None
                                dct_oms_prvd["global_provider_conn"].logout()
                                dct_oms_prvd["global_provider_conn"] = None
                                dct_oms_prvd["global_provider_queue"] = None
                                dct_oms_prvd["lst_admin_msgs"].clear()
                                dct_oms_prvd["lst_admin_msgs"] = None
                                dct_oms_prvd["lst_senders"].clear()
                                dct_oms_prvd["lst_senders"] = None

                                dct_oms_prvd["connected"] = False

                                self._logger.info(f"The connection to OMS {provider.get('name')} was terminated.")

                        else:
                            ''' The system turning online. It starts connection, queues and lists. '''
                            if not dct_oms_prvd.get("connected", False) and host.get("enabled"):
                                dct_oms_prvd["id"] = provider.get("id")
                                dct_oms_prvd["begin_string"] = host.get("begin_string")
                                dct_oms_prvd["sender_comp_id"] = host.get("sender_comp_id")
                                dct_oms_prvd["target_comp_id"] = host.get("target_comp_id")
                                dct_oms_prvd["session_qualifier"] = host.get("session_qualifier")
                                dct_oms_prvd["connected"] = False

                                if conn.get("type").lower() == "cedro_quickfix":
                                    queue = Queue()

                                    qfix_conn = ConnectionFactory.get_connection(
                                        conn_type=ConnectionFactory.CONNECTION_TYPE.get("QUICKFIX"),
                                        settings_file=host.get("settings_file"),
                                        global_queue=queue,
                                        delimiter=provider.get('encode_field_delimiter', '')
                                    )

                                    str_cls = f"{provider.get('configurator_class')}(" \
                                              f"qfix_conn, " \
                                              f"oms_id=conn.get('id'), " \
                                              f"oms_name=conn.get('name'), " \
                                              f"begin_string=host.get('begin_string'), " \
                                              f"sender_comp_id=host.get('sender_comp_id'), " \
                                              f"target_comp_id=host.get('target_comp_id'), " \
                                              f"session_qualifier=host.get('session_qualifier'), " \
                                              f"username=host.get('username'), " \
                                              f"password=host.get('password'), " \
                                              f"encode_field_delimiter=provider.get('encode_field_delimiter', ''), " \
                                              f"values_field_delimiter=provider.get('values_field_delimiter', '')" \
                                              f")"

                                    oms_prov = eval(str_cls)
                                    oms_prov.logon()
                                    # var_con = oms_prov.is_connected()
                                    # oms_prov.execute(**{"MsgType": "5", "Text": "LOGOUT REQUESTED BY CLIENT."})
                                    # oms_prov.logout()

                                    dct_oms_prvd["connected"] = oms_prov.is_connected()
                                    if dct_oms_prvd["connected"]:
                                        dct_oms_prvd["global_provider_conn"] = oms_prov
                                        dct_oms_prvd["global_provider_queue"] = queue
                                        dct_oms_prvd["lst_admin_msgs"] = []
                                        dct_oms_prvd["lst_senders"] = []
                                        dct_oms_prvd["global_provider_decoder"] = oms_prov

                                        lst_oms_providers.append(dct_oms_prvd)

                                        self._logger.info(f"The connection to OMS {provider.get('name')} was "
                                                          f"established.")
                                        break

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
