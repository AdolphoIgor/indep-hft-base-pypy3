from datetime import datetime, date, time, timedelta

from api.config.providers.oms.cedro.src.constants import Constants as CrystalOMSConstants
from api.config.providers.oms.provider import OMSProvider
from api.constants import Constants as Constants
from api.exceptions import LayoutRequiredFildNotProvided, PayloadItemNotFound, \
    PayloadItemNotAsExpected
from api.io.network.connection import Connection


class CedroOMSProviderBasic(OMSProvider):

    def __init__(self, **kwargs):
        self._oms_id = kwargs.get("oms_id")
        self._oms_name = kwargs.get("oms_name")
        self._begin_string = kwargs.get("begin_string")
        self._sender_comp_id = kwargs.get('sender_comp_id')
        self._target_comp_id = kwargs.get('target_comp_id')
        self._session_qualifier = kwargs.get('session_qualifier')
        self._username = kwargs.get('username')
        self._password = kwargs.get('password')
        self._encode_field_delimiter = kwargs.get("encode_field_delimiter")
        self._values_field_delimiter = kwargs.get("values_field_delimiter")

    def _get_sender_id(self, algo_name="") -> str:
        oms_name = self._oms_name.replace(" ", "").replace("_", "").upper()
        result = f"{oms_name}{self._values_field_delimiter}{self._oms_id}"
        if len(algo_name) > 0:
            algo_name = algo_name.replace(" ", "").replace("_", "").upper()
            result = result + f"{self._values_field_delimiter}{algo_name}"

        return result

    def get_template(self, msg_type: str, lst_ignore: list) -> dict:
        return CrystalOMSConstants().get_template(msg_type, lst_ignore)

    def decode_sender_id(self, sender_sub_id: str) -> list:
        return sender_sub_id.split(self._values_field_delimiter)

    def decode(self, data) -> list:

        def processa_lista(i_lst_data, i_sel_df, i_dct_ret):
            for i_tag, i_data in i_lst_data:
                dct_layout = {}
                lst_subtags = None
                for i_itm in i_sel_df:
                    if i_itm.get("tag") == i_tag:
                        dct_layout = i_itm
                        lst_subtags = i_itm.get("subtags", [])
                        break

                if len(dct_layout) == 0:
                    continue

                if dct_layout.get("datatype") == float:
                    i_data = float(i_data)
                elif dct_layout.get("datatype") == int:
                    i_data = int(i_data)
                elif dct_layout.get("datatype") == str:
                    i_data = str(i_data)
                elif dct_layout.get("datatype") == bool:
                    i_data = bool(i_data)
                elif dct_layout.get("datatype").find("datetime") >= 0:
                    try:
                        i_data = eval(dct_layout.get("datatype").format(i_data))
                    except ValueError:
                        pass

                key_name = dct_layout.get("name")
                if key_name not in i_dct_ret:
                    i_dct_ret[key_name] = i_data
                else:
                    key_str = ""
                    for k, _ in i_dct_ret.items():
                        if k.find(key_name) > -1:
                            key_str = k

                    lst_name_lvl = key_str.split("_")
                    count = 0
                    try:
                        count = int(lst_name_lvl[-1]) + 1
                        name = f'{key_name}_{count}'
                    except ValueError:
                        name = f'{key_name}_{count}'

                    i_dct_ret[name] = i_data

                if lst_subtags is not None and len(lst_subtags) > 0:
                    lst_sel_subtags = [dtc.get("tag") for dtc in lst_subtags]
                    lst_sel_data = list(filter(lambda x: x[0] in lst_sel_subtags, i_lst_data))
                    processa_lista(lst_sel_data, lst_subtags, i_dct_ret)

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
                lst_rows = list(filter(lambda x: len(x) > 0, command.split(self._encode_field_delimiter)))
                lst_data = list(map(lambda x: [int(x[0]), x[1]], [row.split(
                    self._values_field_delimiter) for row in lst_rows]))

                # Find out what MsgType is in the command.
                msg_type = ""
                for itm in lst_data:
                    if itm[0] == 35:
                        msg_type = itm[1]
                        break

                if len(msg_type) == 0:
                    print("KD o MSGTYPE?")

                # it selects the suitable layout for the register received.
                sel_df = CrystalOMSConstants().get_layout(msg_type)
                if len(sel_df) == 0:
                    print("Não tem layout para o MSGTYPE informado!")

                # create a dict from the stream received.
                dtc_ret = {}
                processa_lista(lst_data, sel_df, dtc_ret)
                result_list.append(dtc_ret)

        return result_list


class CedroOMSProvider(CedroOMSProviderBasic):
    __used_classes = [datetime, date, time, timedelta]

    def __init__(self, conn: Connection, **kwargs):
        super().__init__(**kwargs)
        self._oms_connection = conn

    def __del__(self):
        self._oms_connection.disconnect()

    def _get_next_msg_seq_num(self) -> int:
        msg_seq_number = self._oms_connection.get_msg_seq_num()[0]
        if msg_seq_number is None:
            msg_seq_number = 0
        return msg_seq_number + 1

    def _get_next_cl_ord_id(self) -> int:
        cl_ord_id = self._oms_connection.get_cl_ord_id()
        if cl_ord_id is None:
            cl_ord_id = 0
        return cl_ord_id + 1

    def get_connection(self):
        return self._oms_connection

    def is_connected(self) -> bool:
        return self._oms_connection.is_connected()

    def execute(self, **kwargs):
        if not self.is_connected():
            self.logon()

        self._oms_connection.execute(self.encode(**kwargs))

    def logon(self) -> bool:
        if not self.is_connected():
            order = {
                "MsgType": "A",
                "Username": self._username,
                "Password": self._password
            }

            self._oms_connection.connect(message=self.encode(**order))

        return self._oms_connection.is_connected()

    def logout(self):
        if self.is_connected():
            order = {
                "MsgType": "5",
                "Text": "LOGOUT REQUESTED BY CLIENT."
            }

            self._oms_connection.execute(self.encode(**order))

    def encode(self, algo_name="", **kwargs) -> str:
        """
            :param algo_name: Will be the iaentity of the message's sender. If it's not provided, will return a id
                composed with "OMS_NAME+DELIMITER+BROKER_NAME" which is enough to identify orders such as LOGON/LOGOUT.
            :param kwargs:
            :return: the encoded message in a byte-string format.
        """
        def prepare_date_fields(str_date_value) -> str:
            return str(str_date_value).replace("-", "").replace(" ", "-")[:21]

        def get_encoded_str(lst_sel_df: list, i_kwargs: dict) -> str:
            i_str_out = ""
            for itm in lst_sel_df:
                i_name = itm.get("name")
                if i_name in i_kwargs:
                    i_str_out = i_str_out + str(itm.get("tag")) + self._values_field_delimiter + \
                              str(i_kwargs.get(i_name)) + self._encode_field_delimiter

                    subtags = itm.get("subtags", [])
                    if subtags:
                        i_str_out = i_str_out + get_encoded_str(subtags, i_kwargs)

            return i_str_out

        def get_checksum(str_message):
            i_sum = 0
            for c in str_message:
                i_sum += ord(c)

            return str(i_sum % 256).zfill(3)

        def health_check(i_l_itm, i_kwargs: dict) -> bool:
            # some calculated fields must be ignored at this time
            if i_l_itm.get("calculated", False):
                return False

            str_default = i_l_itm.get("default")
            str_val = i_kwargs.get(i_l_itm.get("name"))
            # items which has an explicit default value, and it hasn't been provided, then will be replaced.
            if str_val is None and str_default is not None:
                i_kwargs[i_l_itm.get("name")] = str_default

            # designed to address items not found into the provided payload.
            if i_l_itm.get("required") and i_l_itm.get("name") not in i_kwargs:
                raise PayloadItemNotFound(
                    Constants.PAYLOAD_ITEM_NOT_FOUND.format(str(i_l_itm)))

            # designed to address items whitch it's value is not into the provided domain.
            lst_domain = i_l_itm.get("domain", [])
            str_val = i_kwargs.get(i_l_itm.get("name"))
            if len(lst_domain) > 0 and str_val is not None and i_l_itm.get("required") and str_val not in lst_domain:
                raise PayloadItemNotAsExpected(
                    Constants.PAYLOAD_ITEM_INVALID.format(str(i_l_itm), "OUT-OF-DOMAIN"))

            # designed to address items whitch it's value has wrong size length.
            length = i_l_itm.get("lenght", -1)
            if 0 < length < len(i_kwargs.get(i_l_itm.get("name"), "")):
                raise PayloadItemNotAsExpected(
                    Constants.PAYLOAD_ITEM_INVALID.format(str(i_l_itm), "WRONG SIZE LENGHT"))

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
                if not health_check(l_itm, kwargs):
                    continue
            else:
                for i_l_item in lst_subtags:
                    if not health_check(i_l_item, kwargs):
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
        kwargs["BeginString"] = self._begin_string if len(self._begin_string) > 0 else kwargs["BeginString"]
        kwargs["MsgSeqNum"] = self._get_next_msg_seq_num()
        kwargs["SendingTime"] = prepare_date_fields(datetime.now() + timedelta(seconds=-2))
        kwargs["TransactTime"] = prepare_date_fields(datetime.now() + timedelta(seconds=-2))
        kwargs["SenderCompID"] = self._sender_comp_id if len(self._sender_comp_id) > 0 else kwargs["SenderCompID"]
        kwargs["TargetCompID"] = self._target_comp_id if len(self._target_comp_id) > 0 else kwargs["TargetCompID"]
        kwargs["ApplicationName"] = Constants.SHORT_SOFTWARE_NAME
        kwargs["ApplicationVersion"] = Constants.SOFTWARE_VERSION
        kwargs["OrderStrategy"] = "DAYTRADE"

        token = self._oms_connection.get_token()
        if token is not None:
            kwargs["Signature"] = token
            kwargs["SignatureLength"] = len(kwargs["Signature"])

        if len(algo_name) > 0:
            kwargs["SenderSubID"] = self._get_sender_id(algo_name)

        if kwargs.get("ClOrdID", None) is not None:
            kwargs["ClOrdID"] = self._get_next_cl_ord_id()

        if kwargs.get("PartyID", None) is not None:
            kwargs["PartyID"] = self._username

        if kwargs.get("SourceAddress", None) is not None:
            kwargs["SourceAddress"] = self._get_sender_id(algo_name)

        lst_fields = ['BodyLength', 'CheckSum', 'SenderSubID']
        for fld in lst_fields:
            if fld in kwargs and kwargs.get(fld) == 'will be calculated':
                kwargs.pop(fld)

        # getting the command ready to be sent to the provider.
        str_out = get_encoded_str(sel_df, kwargs)

        # must provide the last calculated fields
        str_out = str_out[str_out.find(kwargs["BeginString"]) + len(kwargs["BeginString"]) + 1:]
        kwargs["BodyLength"] = len(bytes(str_out, "UTF-8"))

        str_out = get_encoded_str(sel_df, kwargs)

        # adding the checksum.
        str_out += '10=' + get_checksum(str_out) + self._encode_field_delimiter

        return str_out

