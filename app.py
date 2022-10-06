import getopt
import sys
import time
import traceback

from api.constants import Constants
from api.indep import Indep
from api.logger import logger


def main():
    """ Recebe o parametro e inicia o processo correspondente """
    logger.info(f"Incializando a plataforma de execução...")

    _, args = getopt.getopt(sys.argv[1:], "", [])
    test_mode = "test_mode" in args
    config = {
        "encoder": "UTF-8",
        "sleep_when_done": 0.1,
        "config_file_path": "api/config/config.json",
        "config_cmd_file_path": "control/config_cmd.json",
    }

    platform = Indep(test_mode=test_mode, config=config)
    try:
        platform.start()

        while True:
            if platform.is_all_done():
                break

            time.sleep(Constants.MAIN_LOOP_SLEEP)

    except Exception:
        logger.critical(f"Erro durante a execução do programa: {traceback.format_exc()}.")
        sys.exit(Constants.EXIT_ERROR)

    finally:
        platform.stop()
        logger.info(f"A plataforma de execução foi finalizada com sucesso!")
        sys.exit(Constants.EXIT_SUCCESS)


if __name__ == "__main__":
    main()
