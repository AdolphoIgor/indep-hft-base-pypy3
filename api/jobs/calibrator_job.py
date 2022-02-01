import time

from api.jobs.job import Job


class CalibratorJob(Job):

    def __init__(self, logger, dict_configs, lst_config_pool, lst_thread_pool, **kwargs):
        super().__init__(logger, dict_configs, lst_config_pool, lst_thread_pool)
        self.__encoder = kwargs.get("encoder")
        self.__sleep_when_done = kwargs.get("sleep_when_done")
        self.__log_min_sample_days = kwargs.get("min_sample_days")
        self.__log_min_tunner_days = kwargs.get("min_tunner_days")
        self.__log_proc_samples_inverted = kwargs.get("proc_samples_inverted")
        self.__log_calibrator_md_files = kwargs.get("log_calibrator_md_files")
        self.__log_calibrator_historical_files = kwargs.get("log_calibrator_historical_files")
        self.__log_calibrator_reports_files = kwargs.get("log_calibrator_reports_files")
        self.__backtest_filename = kwargs.get("backtest_filename")
        self.__lst_cnf_symbol = kwargs.get("lst_cnf_symbol")
        self.__delimiter = kwargs.get("delimiter")
        self.__dct_market_data = kwargs.get("market_data")
        self.__dct_backtest = {}

    def run(self) -> None:
        self._logger.info("Initializing the Calibrator...")

        while self._keep_running:

            lst_algos = self._dict_configs.get("algos", {})
            if len(lst_algos) == 0:
                time.sleep(1)
                continue
