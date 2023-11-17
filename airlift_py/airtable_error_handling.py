# Using Airtable's Error Codes as reference:
# https://support.airtable.com/docs/airtable-api-common-troubleshooting
# https://airtable.com/developers/web/api/errors

from requests.exceptions import HTTPError
from airlift_py.utils_exceptions import CriticalError, AirtableError

def ClientError(error:HTTPError) -> None:

    if error.response.status_code == 403:
        raise AirtableError("Accessing a protected resource with API credentials that don't have access to that resource!")
    
    elif error.response.status_code == 401:
        raise AirtableError("Accessing a protected resource without authorization or with invalid credentials!")
    
    elif error.response.status_code == 422:
        print(error.response.text)
        raise CriticalError("The request data is invalid!")
