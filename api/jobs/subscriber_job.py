import time

from api.jobs.job import Job


class SubscriberJob(Job):

    def __init__(self, logger, dict_configs, lst_config_pool, lst_thread_pool, **kwargs):
        super().__init__(logger, dict_configs, lst_config_pool, lst_thread_pool)
        self.__sleep_when_done = kwargs.get("sleep_when_done")

    def run(self) -> None:
        """
            The subscriber has to ask for the provider for every symbol and it's instruments.
        """
        self._logger.info("Initializing the Subscriber...")

        while self._keep_running:

            configs = self._dict_configs.get("configs", {})
            if len(configs) == 0:
                time.sleep(1)
                continue

            prdr_name = "market_data_providers"
            for provider in configs.get(prdr_name, []):

                lst_md_providers, lst_md_sel_providers, dct_md_prvd = \
                    self._get_internal_provider_data(prdr_name, provider.get("id"))

                if dct_md_prvd.get("connected", False):
                    md_prov = dct_md_prvd.get("global_provider_conn", None)
                    conn = md_prov.get_connection()
                    if conn is None:
                        time.sleep(1)
                        continue

                    for symbol in dct_md_prvd.get("symbols", []):
                        if symbol.get("registered"):
                            for instrument in symbol.get("instruments", []):

                                cfg_instr = None
                                for sbl in provider.get("symbols", {}):
                                    if sbl.get("symbol") == symbol.get("symbol"):
                                        for inst in sbl.get("instruments", []):
                                            if instrument.get("type") == inst.get("type"):
                                                cfg_instr = inst
                                                break
                                        break

                                if cfg_instr.get('enabled') and not instrument.get("registered", False):
                                    conn.write(md_prov.to_bytes(
                                        f"{cfg_instr.get('cmd_subscribe')} {symbol.get('symbol')}\r\n"))
                                    instrument["registered"] = True
                                    self._logger.info(f"The symbol to {symbol.get('symbol')} was subscribed.")

                                elif not cfg_instr.get('enabled') and instrument.get("registered", False):
                                    conn.write(md_prov.to_bytes(
                                        f"{cfg_instr.get('cmd_unsubscribe')} {symbol.get('symbol')}\r\n"))
                                    instrument["registered"] = False
                                    self._logger.info(f"The symbol to {symbol.get('symbol')} was unsubscribed.")

                                time.sleep(0.01)

                        time.sleep(0.01)

            time.sleep(self.__sleep_when_done)

        self._logger.info("Subscriber was finalized.")
