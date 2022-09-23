class OMSProvider:

    def execute(self, **kwargs):
        """ Every subclass must provide a way to send an order to the de provider. """

    def logon(self) -> bool:
        """ Every subclass must provide a way to logon on the provider. """

    def logout(self):
        """ Every subclass must provide a way to logout of the provider. """

    def is_connected(self) -> bool:
        """ Verifies if the provider has sent an token, thus this client is connected. """

    def get_connection(self):
        """ Return the internal connection. """

    def get_template(self, msg_type: str, lst_ignore: list) -> dict:
        """ Return templates for every possible message used by a provider. """
