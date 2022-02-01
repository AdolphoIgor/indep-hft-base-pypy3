class Constants:
    SOFTWARE_NAME = 'INDEP SOFTWARE'
    SHORT_SOFTWARE_NAME = 'INDEP'
    SOFTWARE_VERSION = 'v1.0'

    DEFAULT_ENCODER = 'UTF-8'

    EXIT_SUCCESS = 0
    EXIT_ERROR = 1

    BKP_PATH = 'bkp'
    BKP_LOGS = f'{BKP_PATH}/logs/'
    LOG_PATH = 'logs'
    LOG_OMS = f'{LOG_PATH}/oms/'
    LOG_OMS_RAW = f'{LOG_OMS}/raw/'
    LOG_OMS_DATA = f'{LOG_OMS}/data/'
    LOG_OMS_CONFIG = f'{LOG_OMS}/config/'
    LOG_ALGO = f'{LOG_PATH}/algo/'
    LOG_ALGO_RAW = f'{LOG_ALGO}/raw/'
    LOG_ALGO_DATA = f'{LOG_ALGO}/data/'
    LOG_ALGO_CONFIG = f'{LOG_ALGO}/config/'
    LOG_MARKETDATA = f'{LOG_PATH}/marketdata/'
    LOG_MARKETDATA_RAW = f'{LOG_MARKETDATA}/raw/'
    LOG_MARKETDATA_DATA = f'{LOG_MARKETDATA}/data/'
    LOG_MARKETDATA_CONFIG = f'{LOG_MARKETDATA}/config/'

    POSITION_NEW = 0
    POSITION_OPENED = 1
    POSITION_STOPED = 2

    LAYOUT_NOT_FOUND = "The expected layout was not found from the given token. "
    LAYOUT_ITEM_NOT_FOUND = "The item {0} was not found in the provided provider's layout. "
    LAYOUT_ITEM_NOT_PROVIDED = "The item {0} must be provided on order to proceed. "

    PAYLOAD_ITEM_NOT_FOUND = "The expected item: '{0}' was not found from the given payload. "
    PAYLOAD_ITEM_INVALID = "The expected item: '{0}' from the given payload has an invalid value. Reason: {1}."

    LOGOUT_MSG = "Error during logon process to OMS: {0}. Msg:{1}."
    LOGON_MSG = "Logon process to OMS: {0} has success."
