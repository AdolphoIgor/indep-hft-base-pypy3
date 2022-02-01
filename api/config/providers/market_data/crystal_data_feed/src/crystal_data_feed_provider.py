from datetime import datetime, date, time

from api.config.providers.market_data.crystal_data_feed.src.constants import Constants as CrystalDataFeedConstants
from api.config.providers.market_data.provider import Provider
from api.constants import Constants as Constants
from api.exceptions import LayoutIndexNotFound
from api.logger import logger


class CrystalDataFeedProvider(Provider):
    __used_classes = [datetime, date, time]

    def __init__(self):
        logger.name = Constants.SOFTWARE_NAME

    @staticmethod
    def get_delimiters() -> list:
        return [CrystalDataFeedConstants.MSG_DELIMITER, CrystalDataFeedConstants.MSG_VALUE_DELIMITER]

    @staticmethod
    def decode(data, **kwargs) -> list:
        data_format = kwargs.get('data_format', CrystalDataFeedConstants.data_format)
        data = str(data)

        msg_filter = ["b\"", "\r\n", "\n\r", "\r", "\n", "\"", "SYN"]
        for f in msg_filter:
            data = data.replace(f, "")

        result_list = []

        if len(data) == 0:
            return result_list

        # split the data into a list of commands
        commands = data.split(CrystalDataFeedConstants.MSG_DELIMITER)
        for command in commands:

            if len(command) > 0:

                # splits the stream into a list
                data_splitted = command.split(CrystalDataFeedConstants.MSG_VALUE_DELIMITER)

                # selects the suitable layout for the register received.
                sel_df = {}
                for df in data_format:
                    if data_splitted[0] == df.get("header").get("type"):
                        sel_df = df
                        break

                if len(sel_df) == 0:
                    raise LayoutIndexNotFound(Constants.LAYOUT_NOT_FOUND)

                # create a dict from the stream received.
                header = data_splitted[:3]
                payload = data_splitted[3:]
                result = {}

                for idx, (key, value) in enumerate(sel_df.get("header").items()):
                    data = header[idx]
                    if value.find("datetime") >= 0:
                        result[key] = eval(value.format(data))
                    else:
                        result[key] = data

                idx = 0
                payload_layout = list(filter(lambda x: x.get("enabled"), sel_df.get("payload")[:]))
                while idx < len(payload):
                    itm = payload[idx]

                    payload.pop(idx)
                    data = payload.pop(idx)

                    lst_layout = list(filter(lambda x: x.get("index") == int(itm), payload_layout))
                    if len(lst_layout) == 0:
                        continue

                    itmlt = lst_layout[0]

                    if itmlt.get("type") == float:
                        data = float(data)
                    elif itmlt.get("type") == int:
                        data = int(data)
                    elif itmlt.get("type") == str:
                        data = str(data)
                    elif itmlt.get("type").find("datetime") >= 0:
                        try:
                            data = eval(itmlt.get("type").format(data))
                        except ValueError:
                            pass

                    result[itmlt.get("name")] = data

                result_list.append(result)

            return result_list
