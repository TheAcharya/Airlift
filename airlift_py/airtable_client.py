import logging
from typing import Any, Dict, Iterable, Iterator, List, Optional
from airlift_py.airtable_error_handling import ClientError
from airlift_py.utils_exceptions import AirtableError
from airlift_py.csv_data import CSVRowType
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
        logger.debug("Airtable Client Created")

    def single_upload(self,data:ATDATATYPE) -> None:

        data["typecast"] = True
        response = requests.post(self.single_upload_url, headers=self.headers, data=json.dumps(data))

        if response.status_code == 200:
            pass
            #logger.debug("Request completed successfully!")
        else:
            logger.warning(f"Error creating records: {response}")
            raise AirtableError("Unable to upload data!")
    
    def missing_fields_check(self,data:ATDATATYPE,disable_bypass:bool):
        
        airtable_table_fields = []
        user_csv_fields = []

        url = f"https://api.airtable.com/v0/meta/bases/{self.base}/tables"
        response = requests.get(url,headers=self.headers)
        tables = json.loads(response.text)

        for x in tables['tables']:
            if x['id'] == self.table or x['name'] == self.table:

                for fields in x['fields']:
                    airtable_table_fields.append(fields['name'])

        
        for csv_key,csv_value in data[0]['fields'].items():
            user_csv_fields.append(csv_key)

        missing_columns = list(set(user_csv_fields) - set(airtable_table_fields))

        if missing_columns:
            for column in missing_columns:
                if disable_bypass:
                    self._create_new_field(column)
                else:
                    logger.warning(f"Column {column} would be skipped!")
                    for datas in data:
                        try:
                            del datas['fields'][column]
                        except:
                            print(f"{column} not present in this row")

        else:
            logger.info("All the columns are verified and present in both the file and Airtable!")

        return data
    
    def _create_new_field(self,field_name:str) -> None:
        URL = f"https://api.airtable.com/v0/meta/bases/{self.base}/tables/{self.table}/fields"
        new_field = {"name":field_name,"description":"This is a field created by Airtable","type":"multilineText"}

        response = requests.post(URL,headers=self.headers,data=json.dumps(new_field))

        if response.status_code == 200:
            logger.info(f"Created new column {field_name} in Airtable")
        elif response.status_code == 422:
            logger.warning("Encountered an 422 error in creating a new column in Airtable!")
        
        else:
            logger.warning(f"unknown error : {response.text}")
        
 
            
