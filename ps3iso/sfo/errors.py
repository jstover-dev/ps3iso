class SfoUnknownParameterError(Exception):
    """Named Exception raised when a reference to an invalid parameter name is encountered"""


class SfoMissingParameterError(Exception):
    """Named Exception raised when an SfoFile is missing a required parameter"""


class SfoDuplicateParameterError(Exception):
    """Named Exception raised when a duplicate SFO parameter is encountered in an SfoFile"""


class SfoParameterNotFoundError(Exception):
    """Named Exception raised when a user-supplied attribute is not found"""


class SfoParseError(Exception):
    """Named Exception raised when a general parsing error occurs"""
    def __init__(self, message, filepath=None):
        if filepath is not None:
            message = 'Error while parsing file "%s": %s' % (filepath, message)
        super().__init__(message)


class SfoIndexTableParseError(SfoParseError):
    """Named Exception raised when an parsing an invalid SfoIndexTable is attempted"""


class SfoIndexTableEntryParseError(SfoParseError):
    """Named Exception raised when an parsing an invalid SfoIndexTableEntry is attempted"""


class SfoHeaderParseError(SfoParseError):
    """Named Exception raised when an parsing an invalid SfoHeader is attempted"""
