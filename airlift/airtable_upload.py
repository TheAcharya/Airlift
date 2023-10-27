import pyairtable.api.table as ATtable
from airlift.csv_data import CSVRowType
from typing import Any, Dict, Iterable, Iterator, List, Optional
from airlift.utils_exceptions import CriticalError
import logging
from requests.exceptions import HTTPError
from airlift.airtable_error_handling import ClientError

logger = logging.getLogger(__name__)

def upload_data(client: ATtable, new_data:List[CSVRowType]) -> None:
    try:
        logger.info("trying to upload data to airtable")
        client.batch_create(new_data)
        logger.info("Upload done ...")
    except HTTPError as e:
        ClientError(e)
    except Exception as e:
        raise CriticalError("An unexpected error occured! please contact the developers")
    #client.batch_create(new_data)