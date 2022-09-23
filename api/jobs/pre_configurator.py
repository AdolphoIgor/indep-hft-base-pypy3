import json
import time

from api.jobs.job import Job
from api.logger import logger


class PreConfiguratorJob(Job):

    def __init__(self, dict_configs, lst_config_pool, **kwargs):
        super().__init__(dict_configs, lst_config_pool)
        self.__encoder = kwargs.get("encoder")
        self.__sleep_when_done = kwargs.get("sleep_when_done")
        self.__config_file_path = kwargs.get("config_file_path")
        self.__config_cmd_file_path = kwargs.get("config_cmd_file_path")

    def __del__(self):
        self._update_config_cmd()

    def _update_config_cmd(self):
        """ Making sure that the config file will be updated. """
        with open(self.__config_cmd_file_path, mode='w', encoding=self.__encoder) as f:
            f.truncate(0)
            f.seek(0)
            json.dump(self._dict_configs, f, ensure_ascii=True, indent=2)

    def run(self) -> None:
        logger.info("Initializing the Pre-Configurator...")

        while self._keep_running:

            if len(self._dict_configs) == 0:
                with open(self.__config_file_path, mode='r', encoding=self.__encoder) as json_file:
                    self._dict_configs.update(json.load(json_file))

            else:
                with open(self.__config_cmd_file_path, mode='r', encoding=self.__encoder) as json_file:
                    self._dict_configs.update(json.load(json_file))

            time.sleep(self.__sleep_when_done)

            self._update_config_cmd()

        logger.info("Pre-Configurator was finalized.")
