import hashlib
from datetime import datetime, date, time, timedelta

from api.config.providers.oms.cedro.src.constants import Constants as CrystalOMSConstants
from api.config.providers.oms.provider import OMSProvider
from api.constants import Constants as Constants
from api.exceptions import LayoutIndexNotFound, LayoutRequiredFildNotProvided, PayloadItemNotFound, \
    PayloadItemNotAsExpected
from api.io.network.connection_telnet import ConnectionTelnetCedro
from api.logger import logger


class CedroOMSProviderBasic(OMSProvider):

    def __init__(self, **kwargs):
        self.__msg_seq_num = -1
        self.__cl_ord_id = -1

        self.__oms_name = kwargs.get("oms_name", "CedroOMS")
        self.__session = {
            "id": kwargs.get("id", -1),
            "name": kwargs.get("name", ""),
            "usr": kwargs.get("usr", ""),
            "pwd": kwargs.get("pwd", ""),
            "token": None
        }

    def get_template(self, msg_type: str, lst_ignore: list) -> dict:
        return CrystalOMSConstants().get_template(msg_type, lst_ignore)

    def __get_sender_id(self, algo_name="") -> str:
        oms_name = self.__oms_name.replace(" ", "").replace("_", "").upper()
        broker_id = self.__session.get("id")

        result = f"{oms_name}{CrystalOMSConstants.MSG_VALUE_DELIMITER}{broker_id}"
        if len(algo_name) > 0:
            algo_name = algo_name.replace(" ", "").replace("_", "").upper()
            result = result + f"{CrystalOMSConstants.MSG_VALUE_DELIMITER}{algo_name}"

        return result

    @staticmethod
    def decode_sender_id(sender_sub_id: str) -> list:
        return sender_sub_id.split(CrystalOMSConstants.MSG_VALUE_DELIMITER)

    def __get_next_msg_seq_num(self) -> int:
        self.__msg_seq_num = self.__msg_seq_num + 1
        return self.__msg_seq_num

    def __get_next_cl_ord_id(self) -> int:
        self.__cl_ord_id = self.__cl_ord_id + 1
        return self.__cl_ord_id

    @staticmethod
    def decode(data) -> list:
        data = str(data)

        msg_filter = ["b\"", "\r\n", "\r", "\n", "\""]
        for f in msg_filter:
            data = data.replace(f, "")

        result_list = []

        if len(data) == 0:
            return result_list

        # split the data into a list of commands
        commands = data.split(CrystalOMSConstants.MSG_DELIMITER)
        for command in commands:
            if len(command) > 0:
                lst_rows = list(filter(lambda x: len(x) > 0, command.split(CrystalOMSConstants.MSG_FIELD_DELIMITER)))
                lst_data = list(map(lambda x: [int(x[0]), x[1]], [row.split(
                    CrystalOMSConstants.MSG_VALUE_DELIMITER) for row in lst_rows]))

                # Find out what MsgType is in the command.
                msg_type = ""
                for itm in lst_data:
                    if itm[0] == 35:
                        msg_type = itm[1]
                        break

                if len(msg_type) == 0:
                    raise LayoutRequiredFildNotProvided(Constants.LAYOUT_ITEM_NOT_PROVIDED)

                # it selects the suitable layout for the register received.
                sel_df = CrystalOMSConstants().get_layout(msg_type)
                if len(sel_df) == 0:
                    raise LayoutIndexNotFound(Constants.LAYOUT_NOT_FOUND)

                # create a dict from the stream received.
                result = {}
                for tag, data in lst_data:
                    dct_layout = {}
                    for itm in sel_df:

                        lst_subtags = itm.get("subtags", [])
                        if len(lst_subtags) == 0:
                            if itm.get("tag") == tag:
                                dct_layout = itm
                                break
                        else:
                            for i_itm in lst_subtags:
                                if i_itm.get("tag") == tag:
                                    dct_layout = itm
                                    break

                    if len(dct_layout) == 0:
                        logger.info(Constants.LAYOUT_ITEM_NOT_FOUND.format(tag))
                        continue

                    if dct_layout.get("datatype") == float:
                        data = float(data)
                    elif dct_layout.get("datatype") == int:
                        data = int(data)
                    elif dct_layout.get("datatype") == str:
                        data = str(data)
                    elif dct_layout.get("datatype") == bool:
                        data = bool(data)
                    elif dct_layout.get("datatype").find("datetime") >= 0:
                        try:
                            data = eval(dct_layout.get("datatype").format(data))
                        except ValueError:
                            pass

                    result[dct_layout.get("name")] = data
                result_list.append(result)

            return result_list


class CedroOMSProvider(CedroOMSProviderBasic):
    __used_classes = [datetime, date, time, timedelta]

    def __init__(self, conn: ConnectionTelnetCedro, **kwargs):
        super().__init__(**kwargs)
        logger.name = Constants.SOFTWARE_NAME
        self.__oms_connection = conn
        self.__lst_logon = []
        self.__production_environment = False

    def __del__(self):
        self.__oms_connection.disconnect()

    def get_connection(self):
        return self.__oms_connection

    def is_connected(self) -> bool:
        return self.__session.get("token", None) is not None

    def execute(self, **kwargs) -> dict:
        if not self.is_connected():
            self.logon()

        encoded = self.encode(**kwargs)
        self.__oms_connection.execute(encoded)

        return self.decode(encoded)[0]

    def logon(self) -> bool:
        result = False

        order = {
            "MsgType": "A",
            "Username": self.__session.get("usr", ""),
            "Password": self.__session.get("pwd", ""),
            "ResetSeqNumFlag": "Y"
        }

        self.__oms_connection.execute(self.encode(**order))

        lst_res = []
        tlnt_conn = self.__oms_connection.get_connection()
        int_next_exp_msg_seq = -1
        while len(lst_res) < 2:
            srv_resps = self.decode(tlnt_conn.read_until(tlnt_conn.to_bytes(
                CrystalOMSConstants.MSG_DELIMITER)).decode(Constants.DEFAULT_ENCODER))

            for res in srv_resps:
                if res.get("MsgType", "") in ["A", "BD"]:
                    if res.get("NextExpectedMsgSeqNum", -1) in [-1, int_next_exp_msg_seq]:
                        int_next_exp_msg_seq = res.get("NextExpectedMsgSeqNum", -1)
                        lst_res.append(res)

        if len(lst_res) == 2:
            if len(self.__lst_logon) > 0:
                self.__lst_logon.extend(lst_res)

            for res in lst_res:
                if res.get("MsgType", "") == "A":
                    lst_logon = res.get("RawData", "").split(chr(10))
                    self.__session["token"]: lst_logon[2]
                    self.__production_environment = res.get("TestMessageIndicator", "Y") == "N"
                    self.__msg_seq_num = -1 if res.get("ResetSeqNumFlag", "Y") == "N" else self.__msg_seq_num
                    self.__cl_ord_id = -1 if res.get("ResetSeqNumFlag", "Y") == "N" else self.__cl_ord_id
                    logger.info(Constants.LOGON_MSG.format(self.__oms_name))
                    result = True
                    break

                elif res.get("MsgType", "") == "5":
                    self.__session["token"] = None
                    logger.info(Constants.LOGOUT_MSG.format(self.__oms_name, res.get("Text", "")))
                    break

        return result

    def logout(self):
        order = {
            "MsgType": "5",
            "Text": "LOGOUT REQUESTED BY CLIENT."
        }

        self.__oms_connection.execute(self.encode(**order))

    def update_logout(self, **kwargs) -> bool:
        result = False

        if kwargs.get("MsgType", "") == "5":
            self.__lst_logon.append(kwargs)
            self.__session["token"] = None
            logger.info(Constants.LOGOUT_MSG.format(self.__oms_name, kwargs.get("Text", "")))
            result = True

        return result

    def encode(self, algo_name="", **kwargs) -> bytes:
        """
            :param algo_name: Will be the iaentity of the message's sender. If it's not provided, will return a id
                composed with "OMS_NAME+DELIMITER+BROKER_NAME" which is enough to identify orders such as LOGON/LOGOUT.
            :param kwargs:
            :return: the encoded message in a byte-string format.
        """
        if not self.is_connected():
            return bytes(chr(0), "UTF-8")

        def health_check(i_l_itm, **i_kwargs) -> bool:
            # some calculated fields must be ignored at this time
            if i_l_itm.get("calculated", False):
                # continue
                return False

            # designed to address items not found into the provided payload.
            if i_l_itm.get("required") and i_l_itm.get("name") not in i_kwargs:
                raise PayloadItemNotFound(
                    Constants.PAYLOAD_ITEM_NOT_FOUND.format(str(i_l_itm)))

            # designed to address items whitch it's value is not into the provided domain.
            lst_domain = i_l_itm.get("domain", [])
            if len(lst_domain) > 0 and i_kwargs.get(i_l_itm.get("name")) not in lst_domain:
                raise PayloadItemNotAsExpected(
                    Constants.PAYLOAD_ITEM_INVALID.format(str(i_l_itm), "OUT-OF-DOMAIN"))

            # designed to address items whitch it's value has wrong size length.
            length = i_l_itm.get("lenght", -1)
            if 0 < length < len(i_kwargs.get(i_l_itm.get("name"))):
                raise PayloadItemNotAsExpected(
                    Constants.PAYLOAD_ITEM_INVALID.format(str(i_l_itm), "WRONG SIZE LENGHT"))

            str_default = i_l_itm.get("default", "")
            str_val = i_kwargs.get(i_l_itm.get("name"))
            # items which has an explicit default value and hasn't been procided will be replaced.
            if len(str(str_val)) > 0 and len(str_default) > 0:
                i_kwargs[str_val] = str_default

            return True

        msg_type = str(kwargs.get("MsgType", ""))
        if len(msg_type) == 0:
            raise LayoutRequiredFildNotProvided(Constants.LAYOUT_ITEM_NOT_PROVIDED)

        # selects the suitable layout for the register received.
        sel_df = CrystalOMSConstants().get_layout(msg_type)

        # make sure all parameters expected as required in the layout have been provided as expected
        for l_itm in sel_df:

            lst_subtags = l_itm.get("subtags", [])
            if len(lst_subtags) == 0:
                if not health_check(l_itm, **kwargs):
                    continue
            else:
                for i_l_item in lst_subtags:
                    if not health_check(i_l_item, **kwargs):
                        continue

        """
            Must provide some calculated fields here:
            -----------------------------------------------------------------------------------------------------------            
            e.g. BeginString, MsgSeqNum, SendingTime, SignatureLength, Signature, CheckSum, TransactTime, SenderCompID,
            ApplicationName, ApplicationVersion...
            
            Keep in mind: Every fields with default values will be recovered with that value fullfiled by design so
            the code bellow is a point of opportunity to chance that value if you wish.
            
        """
        # Every order has the following fields.
        kwargs["BeginString"] = "FIX.4.4"
        kwargs["MsgSeqNum"] = self.__get_next_msg_seq_num()
        kwargs["SendingTime"] = datetime.now() + timedelta(seconds=-2)
        kwargs["Signature"] = self.__session.get("token")
        kwargs["SignatureLength"] = len(kwargs["Signature"])
        kwargs["TransactTime"] = datetime.now() + timedelta(seconds=-2)
        kwargs["SenderCompID"] = self.__session["usr"]
        kwargs["ApplicationName"] = Constants.SHORT_SOFTWARE_NAME
        kwargs["ApplicationVersion"] = Constants.SOFTWARE_VERSION
        kwargs["SenderSubID"] = self.__get_sender_id(algo_name)
        kwargs["OrderStrategy"] = "DAYTRADE"

        # Just for the orders that have this fields
        if kwargs.get("ClOrdID", None) is not None:
            kwargs["ClOrdID"] = self.__get_next_cl_ord_id()
        if kwargs.get("PartyID", None) is not None:
            kwargs["PartyID"] = self.__session["usr"]
        if kwargs.get("SourceAddress", None) is not None:
            kwargs["SourceAddress"] = self.__get_sender_id(algo_name)

        # getting the command ready to be sent to the provider.
        str_out = ""
        for key, data in kwargs.items():
            for l_itm in sel_df:
                if key == l_itm.get("name"):
                    str_out = str_out + str(l_itm.get("tag")) + CrystalOMSConstants.MSG_VALUE_DELIMITER + data + \
                              CrystalOMSConstants.MSG_FIELD_DELIMITER
                    break

        # must provide the last calculated fields
        d1 = CrystalOMSConstants.MSG_VALUE_DELIMITER
        d2 = CrystalOMSConstants.MSG_FIELD_DELIMITER
        kwargs["BodyLength"] = len(bytes(str_out, "UTF-8"))
        str_out = str_out + str(9) + d1 + str(kwargs.get("BodyLength")) + d2

        kwargs["CheckSum"] = hashlib.md5(str_out).hexdigest()
        str_out = str_out + str(10) + d1 + str(kwargs.get("CheckSum")) + d2

        return bytes(str_out, "UTF-8")
