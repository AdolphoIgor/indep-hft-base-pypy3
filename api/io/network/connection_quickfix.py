import time

import quickfix as fix

from api.constants import Constants
from api.io.network.connection import Connection
from api.logger import logger


class QuickFixGenApplication(fix.Application):
    """
        This is also the actual producer class for messages comming from OMS providers using FIX protocol.
    """

    def __init__(self, session, queue, delimiter="|"):
        super().__init__()
        logger.name = Constants.SOFTWARE_NAME

        self._session = session
        self._session_id = None
        self._queue = queue
        self._delimiter = delimiter
        self._connected = False
        self._token = {}

    def __del__(self):
        self._session_id = None

    def _str(self, msg):
        """ Convert a FIX message to a readable string. """
        return msg.toString().replace('\x01', self._delimiter)

    @staticmethod
    def get_field_value(fobj, msg):
        if msg.getHeader().isSetField(fobj.getField()):
            msg.getHeader().getField(fobj)
            return fobj.getValue()

        if msg.isSetField(fobj.getField()):
            msg.getField(fobj)
            return fobj.getValue()

        else:
            return None

    @staticmethod
    def str_msg_to_fix_msg(message) -> fix.Message:
        if type(message) is str:
            msg = fix.Message()
            msg.setString(message)
            message = msg

        return message

    def onCreate(self, session_id):
        self._session_id = session_id
        logger.info(f"onCreate - Session: {session_id}")

    def onLogon(self, session_id):
        self._connected = True
        logger.info(f"onLogon - Session: {session_id}")

    def onLogout(self, session_id):
        self._connected = False
        self._token = {}
        logger.info(f"onLogout - Session: {session_id}")

    def toAdmin(self, message, session_id):
        logger.info(f"toAdmin - message: {self._str(message)}")
        self._queue.put_nowait(message)

    def fromAdmin(self, message, session_id):
        logger.info(f"fromAdmin - message: {self._str(message)}")
        self._queue.put_nowait(message)

        msgtype_field = self.get_field_value(fix.MsgType(), message)
        try:
            rawdata_field = self.get_field_value(fix.RawData(), message)
            # keeping the logon credentials
            if msgtype_field == "A" and rawdata_field is not None and len(rawdata_field) > 0:
                lst_ret = rawdata_field.split("\t")
                self._token['usr'] = lst_ret[0]
                self._token['pwd'] = lst_ret[1]
                self._token['token'] = lst_ret[2]
                logger.info(f"fromAdmin - self._token: {self._token}")

        except fix.FieldNotFound:
            pass

    def toApp(self, message, session_id):
        logger.info(f"toApp - self._token: {self._str(message)}")
        self._queue.put_nowait(message)

    def fromApp(self, message, session_id):
        logger.info(f"fromApp - message: {self._str(message)}")
        self._queue.put_nowait(message)

    def send_message(self, message):
        self._session.sendToTarget(self.str_msg_to_fix_msg(message), self._session_id)

    def is_connected(self):
        return self._connected

    def get_token(self):
        return self._token

    def get_msg_queue(self):
        return self._queue


class ConnectionQuickFix(Connection):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._settings_file = kwargs.get("settings_file")
        self._lst_orders = kwargs.get("lst_orders")
        self._lst_positions = kwargs.get("lst_positions")
        self._queue = kwargs.get("queue")
        self._delimiter = kwargs.get("delimiter")

        self._application = QuickFixGenApplication(fix.Session, self._queue, self._delimiter)
        settings = fix.SessionSettings(self._settings_file)
        store_factory = fix.FileStoreFactory(settings)
        log_factory = fix.FileLogFactory(settings)
        self.set_connection(fix.SocketInitiator(self._application, store_factory, settings, log_factory))

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
            message = self._application.str_msg_to_fix_msg(message)
            msgtype_field = self._application.get_field_value(fix.MsgType(), message)
            if msgtype_field is None or msgtype_field != "A":
                return

            if msgtype_field == "A" and self._application.is_connected():
                return

        except fix.FieldNotFound:
            return

        initiator = self.get_connection()
        while True:
            if self._application.is_connected():
                break

            initiator.start()
            self._application.send_message(message)

            time.sleep(2)
            if not self._application.is_connected():
                initiator.stop()

            time.sleep(0.5)

    def execute(self, message):
        if self._application is None:
            return False

        if not self.is_connected:
            self.connect()

        self._application.send_message(message)
