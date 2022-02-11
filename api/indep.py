import json
import threading
import time

import schedule

from api.constants import Constants
from api.jobs.bkp_job import BackupJob
from api.jobs.calibrator_job import CalibratorJob
from api.jobs.configurator_job import ConfiguratorJob
from api.jobs.distributor_job import DistributorJob
from api.jobs.executor_job import ExecutorJob
from api.jobs.fake_provider_job import FakeProviderJob
from api.jobs.pre_configurator import PreConfiguratorJob
from api.jobs.producer_job import ProducerJob
from api.jobs.subscriber_job import SubscriberJob
from api.logger import logger


class IndepBase:

    def __init__(self, **kwargs):
        logger.name = Constants.SOFTWARE_NAME

        self._test_mode = bool(kwargs.get("test_mode", False))
        self._config_cmd_json = "control/config_cmd.json"

        # Holds the current configuration of the entire system.
        self._dict_configs = {}

        # Holds every configuration created dinamically during the execution.
        self._lst_config_pool = [
            {"type": "market_data_providers", "providers": []},
            {"type": "oms_providers", "providers": []},
            {"type": "algo_providers", "providers": []}
        ]
        '''                                                                                  
            self.__lst_config_pool = [
                {
                    "type": "market_data_providers", 
                    "providers": [
                        {
                            "id": 0, 
                            "connected": False,
                            "global_provider_conn": ConnectionTelnetCedro(),
                            "global_provider_queue": Queue(),
                            "symbols": [
                                {
                                    "symbol": "PETR4", 
                                    "instruments": [
                                        {
                                            "type" : "T",
                                            "instrument": {
                                                dict with values returned by md provider
                                            }
                                        }
                                    ]
                                }
                            ]                                
                        }                        
                    ]
                },
                {
                    "type": "oms_providers", 
                    "providers": [
                        {
                            "id": 0, 
                            "connected": False,                            
                            "global_provider_conn": ConnectionQuickFix(), 
                            "global_provider_decoder": CedroOMSProviderBasic(),                               
                            "orders": [
                                {                           
                                    "algo_id": algo.get("id", -1),
                                    "algo_name": algo.get("name", ""),
                                    "thread_symbol": thread.get("symbol", ""),
                                    "thread_oms_id": thread.get("oms_id", ""),
                                    "thread_broker_id": thread.get("broker_id", ""),                                
                                    "status": "opened",
                                    "orders": {
                                        "new": []
                                        "sent": [],
                                        "received": []
                                    }
                                } -> this would be the reference sended to the algorithm. 
                            ],
                            "positions": [
                                {
                                    "algo_id": algo.get("id", -1),
                                    "algo_name": algo.get("name", ""),
                                    "thread_symbol": thread.get("symbol", ""),
                                    "thread_oms_id": thread.get("oms_id", ""),
                                    "thread_broker_id": thread.get("broker_id", ""),
                                    "order_qtd": 10000, 
                                    "order_price": 23.30,                                    
                                    "exec_qtt": 8000,
                                    "exec_price": 23.35,
                                    "last_price": 23.85,
                                    "position:" 4000.00 
                                }
                            ]                                
                        }                        
                    ]
                },
                {
                    "type": "algos", 
                    "providers": [
                        {
                            "id": 0,
                            "name": "Long-PETR3|Short-PETR4",
                            "enabled": true,
                            "algo_class": "LFT",
                            "threads": [
                            {
                                "symbol": "PETR4",
                                "instruments": ["T"]
                                "market_data_instance" = [{"type": "T", "instrument": {MARKET_DATA}}],	
                                "oms_id": 0,
                                "oms_instance": {
                                    "id": 0, 
                                    "connected": False,
                                    "global_provider_conn": ConnectionTelnetCedro(),                    
                                    "global_provider_queue": Queue(),
                                    "global_provider_decoder": CedroOMSProviderBasic()
                                    "global_provider_lst_brokers_conn": [
                                        {
                                            "broker_id": broker.get("id"),
                                            "broker_name": broker.get("name"), 
                                            "cls_ptr": CedroOMSProvider()
                                        }
                                    ],
                                    "orders": [
                                        {                           
                                            "algo_id": algo.get("id", -1),
                                            "algo_name": algo.get("name", ""),
                                            "thread_symbol": thread.get("symbol", ""),
                                            "thread_oms_id": thread.get("oms_id", ""),
                                            "thread_broker_id": thread.get("broker_id", ""),                                
                                            "status": "opened",
                                            "orders": {
                                                "sent": [],
                                                "received": []
                                            }
                                        } -> this would be the reference sended to the algorithm. 
                                    ],
                                    "positions": [
                                        {
                                            "algo_id": algo.get("id", -1),
                                            "algo_name": algo.get("name", ""),
                                            "thread_symbol": thread.get("symbol", ""),
                                            "thread_oms_id": thread.get("oms_id", ""),
                                            "thread_broker_id": thread.get("broker_id", ""),
                                            "order_qtd": 10000, 
                                            "order_price": 23.30,                                    
                                            "exec_qtt": 8000,
                                            "exec_price": 23.35,
                                            "last_price": 23.85,
                                            "position:" 4000.00 
                                        }
                                    ]                                
                                }
                                "broker_id": 191,
                                "start_class": "Opening",
                                "start_parameters": {
                                    "side": "S",
                                    "order_qty": 10000,
                                    "perc_spread_order_at_market": 0.05
                                }					
                            }
                            "stop_class": "PercTrailingStop",
                                "stop_parameters": {
                                "perc_trailing": 0.02,
                                "inc_trailing": 0.0,
                                "stop_limit": 500.00
                            }
                        }                       
                    ]
                }
            ] 
        '''

        # Holds all live threads used by the system
        self._lst_thread_pool = []

        # If turns true, every thread will have its infinite loop broken and the system will resume.
        self._keep_running = True

        self.start_pre_configurator()

    def start_pre_configurator(self):
        # start the pre-configurator thread.
        config = {
            "encoder": "UTF-8",
            "sleep_when_done": 10,
            "config_file_path": "api/config/config.json",
            "config_cmd_file_path": self._config_cmd_json,
        }

        cls_str = f'PreConfiguratorJob(' \
                  f'logger, ' \
                  f'self._dict_configs, ' \
                  f'self._lst_config_pool, ' \
                  f'self._lst_thread_pool, ' \
                  f'**config ' \
                  f')'

        prt_cls = eval(cls_str)
        prt_cls.setDaemon(True)
        prt_cls.name = "thr_pre_configurator"
        self._lst_thread_pool.append({"name": prt_cls.name, "level": -998.0, "pointer": prt_cls})
        prt_cls.start()

    def set_cmd(self, **kwargs):
        shutdown = kwargs.get("shutdown", False)
        if shutdown:
            self._dict_configs.get('configs')['online'] = False

        md_shtdn = int(kwargs.get("shutdown_md", -1))
        if md_shtdn > -1:
            lst_prov = list(filter(lambda x: x.get('id') == md_shtdn,
                                   self._dict_configs.get("configs").get("market_data_providers", [])))
            if len(lst_prov) > 0:
                lst_prov[0].get("connection")['enabled'] = False

        sb_shtdn = kwargs.get("shutdown_sb", "")
        if len(sb_shtdn) > 0:
            for mdp in self._dict_configs.get("configs").get("market_data_providers", []):
                for sbl in mdp.get('symbols', []):
                    if sbl.get("symbol").upper() == sb_shtdn.upper():
                        sbl['enabled'] = False
                        break

        ''' Updates the control config... '''
        encoder = Constants.DEFAULT_ENCODER
        with open(self._config_cmd_json, mode='w', encoding=encoder) as f:
            f.truncate(0)
            f.seek(0)
            json.dump(self._dict_configs, f, ensure_ascii=True, indent=2)

    def is_all_done(self) -> bool:
        return (not self._keep_running) and all([not thr.get("pointer").isAlive() for thr in self._lst_thread_pool])


class Indep(IndepBase):
    __used_classes = [PreConfiguratorJob, ConfiguratorJob, DistributorJob, ExecutorJob, FakeProviderJob, ProducerJob,
                      SubscriberJob, BackupJob, CalibratorJob]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def start(self):
        name = "thr_scheduling"
        thr_ = threading.Thread(target=self.run, name=name)
        self._lst_thread_pool.append({"name": name, "level": -999.0, "pointer": thr_})
        thr_.setDaemon(True)
        thr_.start()

    def run(self):
        lst_scheduling = self._dict_configs.get('scheduling')

        for shc in lst_scheduling:
            if shc.get("enabled") and not shc.get("running", False):
                lst_threads = shc.get("threads")
                for thr in lst_threads:
                    if thr.get("enabled"):
                        cls_str = f'{thr.get("target")}(' \
                                  f'logger, ' \
                                  f'self._dict_configs, ' \
                                  f'self._lst_config_pool, ' \
                                  f'self._lst_thread_pool, ' \
                                  f'**{thr.get("config")} ' \
                                  f')'

                        prt_cls = eval(cls_str)
                        prt_cls.setDaemon(thr.get("daemon"))
                        name = thr.get("thread_name")
                        prt_cls.name = name
                        level = float(f'{shc.get("order")}.{thr.get("order")}')
                        self._lst_thread_pool.append({"name": name, "level": level, "pointer": prt_cls})

                        if not self._test_mode:
                            schedule.every().monday.at(shc.get("dateteime")).do(prt_cls.start)
                            schedule.every().tuesday.at(shc.get("dateteime")).do(prt_cls.start)
                            schedule.every().wednesday.at(shc.get("dateteime")).do(prt_cls.start)
                            schedule.every().thursday.at(shc.get("dateteime")).do(prt_cls.start)
                            schedule.every().friday.at(shc.get("dateteime")).do(prt_cls.start)
                        else:
                            prt_cls.start()

                shc["running"] = True

        while self._keep_running and not self._test_mode:
            schedule.run_pending()
            time.sleep(1)

    def stop(self):
        # This will interrupt the run method (scheduling part).
        schedule.clear()
        self._keep_running = False

        lst_sorted = list(filter(lambda x: x.get("level") >= -998, self._lst_thread_pool))
        lst_sorted = sorted(lst_sorted, key=lambda x: x.get("level"), reverse=True)
        for thr in lst_sorted:
            pointer = thr.get("pointer")
            if 'stop' in dir(pointer):
                pointer.stop()

        time.sleep(1)
        lst_sorted = list(filter(lambda x: x.get("level") <= -999, self._lst_thread_pool))
        for thr in lst_sorted:
            pointer = thr.get("pointer")
            if 'stop' in dir(pointer):
                pointer.stop()
