class LayoutIndexNotFound(Exception):
    """ Designed to throw an exception when a particular item was not found into the provider's layout. """


class LayoutRequiredFildNotProvided(Exception):
    """ Designed to throw an exception when a particular required item was not provided. """


class PayloadItemNotFound(Exception):
    """ Designed to throw an exception when a particular item was not found into the payload. """


class PayloadItemNotAsExpected(Exception):
    """ Designed to throw an exception when a particular item was found in an improper way into the payload. """
