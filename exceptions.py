class AllaweeBotError(Exception): pass
class InvalidStateCodeError(AllaweeBotError): pass
class InsufficientAllaweeError(AllaweeBotError): pass
class ExpenseParseError(AllaweeBotError): pass
class ExternalServiceError(AllaweeBotError): pass
