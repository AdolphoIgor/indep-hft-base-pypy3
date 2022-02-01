import getopt
import sys

from api.constants import Constants
from api.indep import Indep


def start_platform(test_mode):
    """ Starts the INDEP Platform. """

    platform = Indep(test_mode=test_mode)
    try:
        platform.start()

        while True:
            if not platform.is_all_done():
                cmd = input("").split(" ")
            else:
                break

            if cmd[0].find("shutdown") >= 0:
                if cmd[1] in ['now', 'True', '1']:
                    platform.set_cmd(shutdown=True)

                elif cmd[1] in ['md']:
                    if len(cmd[2]) > 0:
                        platform.set_cmd(shutdown_md=cmd[2])

                elif cmd[1] in ['sb']:
                    if len(cmd[2]) > 0:
                        platform.set_cmd(shutdown_sb=cmd[2])

    except Exception as e:
        print("Erro: ", e)

    finally:
        platform.stop()


def main():
    """ Recebe o parametro e inicia o processo correspondente """
    opts: any

    try:
        opts, args = getopt.getopt(sys.argv[1:], "", [])
        test_mode = "test_mode" in args
        start_platform(test_mode)
        sys.exit(Constants.EXIT_SUCCESS)

    except getopt.GetoptError as err:
        print("Erro: ", err)
        sys.exit(Constants.EXIT_ERROR)


if __name__ == "__main__":
    main()
