import requests
from requests.exceptions import HTTPError
from airlift.utils_exceptions import CriticalError, AirtableError

def ClientError(error:HTTPError) -> None:

    if error.response.status_code == 403:
        raise AirtableError("The Provided Table or Base is not found!")
    
    elif error.response.status_code == 401:
        raise AirtableError("Your Token ID is wrong!")
    
    elif error.response.status_code == 422:
        print(error.response.text)
        raise CriticalError("One or more than one of the data is not of valid data type")
