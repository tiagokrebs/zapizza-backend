class Error(Exception):
    """Base class for exceptions in this module."""
    pass


class InputError(Error):
    """Exception raised for errors in the input.

    Attributes:
        status -- retuning HTTP integer status
        message -- explanation of the error
    """

    def __init__(self, status, message):
        self.status = status
        self.message = message
