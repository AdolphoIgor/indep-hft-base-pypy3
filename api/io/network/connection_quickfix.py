import time

import quickfix as fix

from api.constants import Constants
from api.io.network.connection import Connection
from api.logger import logger


class QuickFixGenApplication(fix.Application):
    """
        This is also the actual producer class for messages comming from OMS providers using FIX protocol.
    """

    def __init__(self, session, queue, delimiter="\u0001", dict_file=""):
        super().__init__()
        logger.name = Constants.SOFTWARE_NAME

        self._session = session
        self._session_id = None
        self._queue = queue
        self._delimiter = delimiter
        self._connected = False
        self._token = None

        self._init_msg_seq_num = None
        self._accep_msg_seq_num = None
        self._data_dict_file = fix.DataDictionary(dict_file)

    def __del__(self):
        self._session_id = None

    def _str(self, msg):
        """ Convert a FIX message to a readable string. """
        msg = msg.toString().encode('utf-8', 'surrogateescape').decode('latin_1')
        return msg if self._delimiter == "\u0001" else msg.replace("\u0001", self._delimiter)

    def get_field_value(self, fobj, msg):
        msg = self.str_msg_to_fix_msg(msg)
        if msg.getHeader().isSetField(fobj.getField()):
            msg.getHeader().getField(fobj)
            return fobj.getValue()

        if msg.isSetField(fobj.getField()):
            msg.getField(fobj)
            return fobj.getValue()

        else:
            return None

    def str_msg_to_fix_msg(self, message) -> fix.Message:
        if type(message) is str:
            message = fix.Message(message, self._data_dict_file)

        return message

    def is_message_to_discard(self, message) -> bool:
        msgtype_field = self.get_field_value(fix.MsgType(), message)
        return msgtype_field not in ['0', '1', '2', '4', '5', 'A', 'B', 'U1', 'U2', 'U3']

    def _process_msg_seq_num(self, message):
        try:
            msg_seq_num = self.get_field_value(fix.MsgSeqNum(), message)
            if msg_seq_num is not None:
                self._init_msg_seq_num = msg_seq_num

        except fix.FieldNotFound:
            pass

    def _process_logon_token(self, message):
        msgtype_field = self.get_field_value(fix.MsgType(), message)
        try:
            rawdata_field = self.get_field_value(fix.RawData(), message)
            if msgtype_field == "A" and rawdata_field is not None and len(rawdata_field) > 0:
                self._token = rawdata_field
                logger.info(f"fromAdmin - self._token: {self._token}")

        except fix.FieldNotFound:
            pass

    def onCreate(self, session_id):
        self._session_id = session_id
        logger.info(f"onCreate - Session: {session_id}")

    def onLogon(self, session_id):
        self._connected = True
        logger.info(f"onLogon - Session: {session_id}")

    def onLogout(self, session_id):
        self._connected = False
        self._token = None
        self._init_msg_seq_num = None
        self._accep_msg_seq_num = None
        logger.info(f"onLogout - Session: {session_id}")

    def toAdmin(self, message, session_id):
        msg_type = fix.MsgType()
        message.getHeader().getField(msg_type)
        msg_type = msg_type.getValue()
        if msg_type == fix.MsgType_Logon:
            username = fix.Username('adolpho.igor')
            password = fix.Password('CedroPwd123')

            message.setField(username)
            message.setField(password)
            message.setField(fix.StringField(9933, "INDEP-SOFTWARE"))

        self._process_msg_seq_num(message)

        msg = self._str(message)
        if self.is_message_to_discard(message):
            self._queue.put_nowait(msg)

        logger.info(f"toAdmin - message: {msg}")

    def toApp(self, message, session_id):
        self._process_msg_seq_num(message)

        msg = self._str(message)
        if self.is_message_to_discard(message):
            self._queue.put_nowait(msg)

        logger.info(f"toApp - message: {msg}")

    def fromAdmin(self, message, session_id):
        self._process_msg_seq_num(message)
        self._process_logon_token(message)

        msg = self._str(message)
        if self.is_message_to_discard(message):
            self._queue.put_nowait(msg)

        logger.info(f"fromAdmin - message: {msg}")

    def fromApp(self, message, session_id):
        self._process_msg_seq_num(message)

        msg = self._str(message)
        if self.is_message_to_discard(message):
            self._queue.put_nowait(msg)

        logger.info(f"fromApp - message: {msg}")

    def send_message(self, message):
        self._session.sendToTarget(self.str_msg_to_fix_msg(message), self._session_id)

    def is_connected(self):
        return self._connected

    def get_token(self):
        return self._token

    def get_msg_seq_num(self):
        return self._init_msg_seq_num, self._accep_msg_seq_num


class ConnectionQuickFix(Connection):
    def __init__(self, **kwargs):
        self._application = None
        self._settings_file = kwargs.get("settings_file", None)
        self._dictionary_file = kwargs.get("dictionary_file", None)
        self._queue = kwargs.get("global_queue", None)
        self._delimiter = kwargs.get("delimiter", None)
        super().__init__(**kwargs)

    def is_connected(self):
        return self._application.is_connected()

    def disconnect(self):
        if self._connected:
            self.get_connection().stop()

        self._connected = False

    def connect(self, **kwargs):
        self._application = QuickFixGenApplication(fix.Session, self._queue, self._delimiter, self._dictionary_file)
        settings = fix.SessionSettings(self._settings_file)
        store_factory = fix.FileStoreFactory(settings)
        log_factory = fix.FileLogFactory(settings)
        initiator = fix.SocketInitiator(self._application, store_factory, settings, log_factory)

        while True:
            initiator.start()
            time.sleep(1)
            self._connected = self.is_connected()
            if self._connected:
                self.set_connection(initiator)
                break

            self.disconnect()

    def execute(self, message):
        if not self._connected:
            self.connect()

        self._application.send_message(message)

    def get_token(self):
        return self._application.get_token()

    def get_msg_seq_num(self):
        return self._application.get_msg_seq_num()
