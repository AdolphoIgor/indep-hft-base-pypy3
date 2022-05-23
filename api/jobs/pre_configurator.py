import json
import time

from api.jobs.job import Job


class PreConfiguratorJob(Job):

    def __init__(self, logger, dict_configs, lst_config_pool, lst_thread_pool, **kwargs):
        super().__init__(logger, dict_configs, lst_config_pool, lst_thread_pool)
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
        """
            The pre-configurator has to keep up to date the content of the variable self._dict_configs so every other
            thread in the system can get access to a fresh configuration which means the config.json will act like
            an entirelly configurator class.

            This thread will hold for some amount seconds after each update in order to not disturb the others threads.
        """
        self._logger.info("Initializing the Pre-Configurator...")

        while self._keep_running:

            if len(self._dict_configs) == 0:
                with open(self.__config_file_path, mode='r', encoding=self.__encoder) as json_file:
                    self._dict_configs.update(json.load(json_file))

            else:
                ''' This keeps the systems configurations updated all the time. '''
                with open(self.__config_cmd_file_path, mode='r', encoding=self.__encoder) as json_file:
                    self._dict_configs.update(json.load(json_file))

            time.sleep(self.__sleep_when_done)

            ''' Updates the control config... '''
            self._update_config_cmd()

        self._logger.info("Pre-Configurator was finalized.")
