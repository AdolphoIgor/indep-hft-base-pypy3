import json
import time

from api.indep import InternalConfigProviders
from api.jobs.job import Job
from api.logger import logger


class PreConfiguratorJob(Job):

    def __init__(self, config_prov: InternalConfigProviders, **kwargs):
        super().__init__(config_prov)
        self.__encoder = kwargs.get("encoder")
        self.__sleep_when_done = kwargs.get("sleep_when_done")
        self.__config_file_path = kwargs.get("config_file_path")
        self.__config_cmd_file_path = kwargs.get("config_cmd_file_path")

    def __del__(self):
        self._update_config_cmd()

    def _update_config_cmd(self):
        """ Making sure that the config file will be updated. """
        with open(self.__config_cmd_file_path, mode="w", encoding=self.__encoder) as f:
            f.truncate(0)
            f.seek(0)
            json.dump(self._config_prov.get_dict_configs(), f, ensure_ascii=True, indent=2)

    def run(self) -> None:
        logger.info("Initializing the Pre-Configurator...")

        dict_configs = self._config_prov.get_dict_configs()
        while self._config_prov.is_running():

            if len(dict_configs) == 0:
                with open(self.__config_file_path, mode="r", encoding=self.__encoder) as json_file:
                    dict_configs.update(json.load(json_file))

            else:
                with open(self.__config_cmd_file_path, mode="r", encoding=self.__encoder) as json_file:
                    dict_configs.update(json.load(json_file))

            if dict_configs.get("run_app", False):
                self._config_prov.start_running()
            else:
                self._config_prov.stop_running()

            time.sleep(self.__sleep_when_done)

            self._update_config_cmd()

        logger.info("Pre-Configurator was finalized.")
