import getopt
import sys
import time
import traceback

from api.constants import Constants
from api.indep import Indep
from api.logger import logger


def main():
    logger.info(f"Starting...")

    _, args = getopt.getopt(sys.argv[1:], "", [])
    test_mode = "test_mode" in args
    platform = Indep(test_mode=test_mode)
    try:
        platform.start()

        while True:
            if platform.is_all_done():
                break

            time.sleep(Constants.MAIN_LOOP_SLEEP)

    except Exception:
        logger.critical(f"Error during execution: {traceback.format_exc()}.")
        sys.exit(Constants.EXIT_ERROR)

    finally:
        platform.stop()
        logger.info(f"Terminated.")
        sys.exit(Constants.EXIT_SUCCESS)


if __name__ == "__main__":
    main()
