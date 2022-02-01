import os
import time
import traceback
import zipfile as zf
from os import walk

from api.jobs.job import Job


class BackupJob(Job):

    def __init__(self, logger, dict_configs, lst_config_pool, lst_thread_pool, **kwargs):
        super().__init__(logger, dict_configs, lst_config_pool, lst_thread_pool)
        self.__logs_path = kwargs.get("logs_path")
        self.__bkp_logs_path = kwargs.get("bkp_logs_path")
        self.__sleep_when_done = kwargs.get("sleep_when_done")

    def run(self) -> None:
        self._logger.info("Initializing the Backup...")

        zips = []
        for (dirpath, dirnames, filenames) in walk(self.__logs_path):
            for filename in filenames:
                zip_name = filename.split("_")[0][:8]

                zip_ = {}
                for zp in zips:
                    if zp.get("filename").lower() == zip_name.lower():
                        zip_ = zp
                        break

                f_name = dirpath + '/' + filename
                if len(zip_) == 0:
                    zips.append({"filename": zip_name, "files": [f_name]})
                else:
                    zip_.get("files").append(f_name)

        try:
            for zp in zips:
                zip_name = f'{self.__bkp_logs_path}/{zp.get("filename")}.zip'
                mode = "a" if os.path.exists(zip_name) else "w"
                with zf.ZipFile(zip_name, mode, zf.ZIP_LZMA) as myzip:
                    for f_name in zp.get("files"):
                        myzip.write(f_name)

            for zp in zips:
                for f_name in zp.get("files"):
                    os.remove(f_name)

        except Exception:
            print(f"\n{traceback.format_exc()}")

        time.sleep(self.__sleep_when_done)

        self._logger.info("Backup was finalized.")
