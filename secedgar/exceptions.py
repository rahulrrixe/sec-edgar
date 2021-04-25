class EDGARQueryError(Exception):
    """This error is thrown when a query receives a response that is not a 200 response."""
    pass


class CIKError(Exception):
    """This error is thrown when an invalid CIK is given."""
    pass


class FilingTypeError(Exception):
    """This error is thrown when an invalid filing type is given."""
    pass


class NoFilingsError(Exception):
    """This error is thrown when no filings are found."""
    pass
