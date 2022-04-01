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
        self._cl_ord_id = None
        self._dict_file = dict_file

    def __del__(self):
        self._session_id = None

    def _str(self, msg):
        """ Convert a FIX message to a readable string. """
        msg = msg.toString()
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
            ddict = fix.DataDictionary(self._dict_file)
            msg = fix.Message(message, ddict)
            message = msg

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

    def _process_cl_ord_id(self, message):
        try:
            cl_ord_id = self.get_field_value(fix.ClOrdID(), message)
            if cl_ord_id is not None:
                self._cl_ord_id = int(cl_ord_id)

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
        self._cl_ord_id = None
        logger.info(f"onLogout - Session: {session_id}")

    def toAdmin(self, message, session_id):
        self._process_msg_seq_num(message)
        self._process_cl_ord_id(message)

        msg = self._str(message)
        if self.is_message_to_discard(message):
            self._queue.put_nowait(msg)

        logger.info(f"toAdmin - message: {msg}")

    def toApp(self, message, session_id):
        self._process_msg_seq_num(message)
        self._process_cl_ord_id(message)

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

    def get_cl_ord_id(self):
        return self._cl_ord_id


class ConnectionQuickFix(Connection):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._settings_file = kwargs.get("settings_file")
        self._dictionary_file = kwargs.get("dictionary_file")
        self._queue = kwargs.get("global_queue")
        self._delimiter = kwargs.get("delimiter")

        self._application = QuickFixGenApplication(fix.Session, self._queue, self._delimiter, self._dictionary_file)
        settings = fix.SessionSettings(self._settings_file)
        store_factory = fix.FileStoreFactory(settings)
        log_factory = fix.FileLogFactory(settings)
        self.set_connection(fix.SocketInitiator(self._application, store_factory, settings, log_factory))

    def is_connected(self):
        self._connected = self._application.is_connected()
        return self._connected

    def disconnect(self):
        initiator = self.get_connection()
        if initiator is not None:
            initiator.stop()

        self._connected = False

    def connect(self, **kwargs):
        message = kwargs.get("message", None)
        if message is None:
            return

        try:
            msgtype_field = self._application.get_field_value(fix.MsgType(), message)
            if msgtype_field is None or msgtype_field != "A":
                return

            if msgtype_field == "A" and self._application.is_connected():
                return

        except fix.FieldNotFound:
            return

        initiator = self.get_connection()
        while True:
            if self.is_connected():
                break

            initiator.start()
            self._application.send_message(message)
            time.sleep(2)
            if self.is_connected():
                break

            time.sleep(10)

            if not self.is_connected():
                initiator.stop()

    def execute(self, message):
        if self._application is None:
            return False

        self._application.send_message(message)

    def get_token(self):
        return self._application.get_token()

    def get_msg_seq_num(self):
        return self._application.get_msg_seq_num()

    def get_cl_ord_id(self):
        return self._application.get_cl_ord_id()
