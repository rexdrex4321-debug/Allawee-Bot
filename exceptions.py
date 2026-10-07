class InvalidStateCodeError(ValueError):
    """Raised when an NYSC state code is invalid."""


class ExpenseParseError(ValueError):
    """Raised when an expense sentence cannot be parsed."""
