class CriticalError(Exception):
    """Exception raised when a generic critical error occurs."""


class AirtableError(Exception):
    """Exception raised when a Notion related critical error occurs."""


class TypeConversionError(Exception):
    """Exception raised when a type conversion error occurs."""