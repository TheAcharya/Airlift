from pyairtable import Api
import pyairtable.api.table as ATtable
import logging
from typing import Any, Dict, Iterable, Iterator, List, Optional
from airlift.airtable_error_handling import ClientError
from airlift.utils_exceptions import AirtableError
from airlift.csv_data import CSVRowType
import json
import requests

ATDATATYPE = Dict[str,Dict[str,str]]

logger = logging.getLogger(__name__)

class new_client:

    def __init__(self,token:str,base:str,table:str):

        self.api = token
        self.base = base
        self.table = table
        self.headers = {
                "Authorization": "Bearer " + self.api,
                "Content-Type": "application/json"
        }

        self.single_upload_url = f"https://api.airtable.com/v0/{self.base}/{self.table}"
        logger.debug("Client Created")

    def single_upload(self,data:ATDATATYPE) -> None:

        response = requests.post(self.single_upload_url, headers=self.headers, data=json.dumps(data))

        if response.status_code == 200:
            pass
            #logger.debug("Record created successfully!")
        else:
            logger.warning(f"Error creating records: {response}")
            raise AirtableError("Unable to upload data!!!")
            
