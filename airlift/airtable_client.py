import logging
import json
import requests
from typing import Any, Dict, Iterable, Iterator, List, Optional
from airlift.airtable_error_handling import ClientError
from airlift.utils_exceptions import CriticalError
from airlift.utils_exceptions import AirtableError
from airlift.csv_data import CSVRowType
from icecream import ic

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
            logger.warning(f"Error creating records: {response.text}")
            raise AirtableError("Unable to upload data!")
        
    def missing_field_single(self,field:str):

        airtable_table_fields = []
        
        tables = self._retreive_table()

        for x in tables['tables']:
            if x['id'] == self.table or x['name'] == self.table:
                for fields in x['fields']:
                    airtable_table_fields.append(fields['name'])
        
        if field in airtable_table_fields:
            return True
        
        return False


    def _missing_fields_check(self,data:ATDATATYPE,args:dict):
        
        disable_bypass = args.disable_bypass_column_creation

        if args.rename_key_column:
            ignore_columns = [args.rename_key_column[0]]
        else:
            ignore_columns = None

        airtable_table_fields = []
        user_csv_fields = []

        
        tables = self._retreive_table()


        for x in tables['tables']:
            if x['id'] == self.table or x['name'] == self.table:

                for fields in x['fields']:
                    airtable_table_fields.append(fields['name'])

        if ignore_columns:
            for column in ignore_columns:
                airtable_table_fields.append(column)
        
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
                            logger.warning(f"{column} not present in this row")

        else:
            logger.info("All the columns are verified and present in both the file and Airtable!")

        return data
    
    def _retreive_table(self):
        url = f"https://api.airtable.com/v0/meta/bases/{self.base}/tables"
        response = requests.get(url,headers=self.headers)
        tables = json.loads(response.text)


        if tables:
            if 'error' in tables:
                logger.warning(f'error:{tables["error"]["message"]}')
                raise AirtableError(f'error:{tables["error"]["message"]}')
            
            else:
                return tables

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
    
    

    def _rename_key_column_check(self,args:dict) -> None:
        
        if args.rename_key_column[1] == args.rename_key_column[0]:
            raise CriticalError("rename-key-column arguement has same column name!")
    
    def create_uploadable_data(self,data:ATDATATYPE,args:dict):
        
        data = self._missing_fields_check(data,args)
        all_data = data

        logger.info("Creating airtable compitable data! Please wait")
        for data in all_data:
        #validation and creating new data fields
            if args.rename_key_column:
                self._rename_key_column_check(args=args)

            if args.attachment_columns_map:
                for attachment in args.attachment_columns_map:
                    data['fields'][attachment[1]] = ""

            if args.columns_copy:
                for column in args.columns_copy[1::]:
                    if self.missing_field_single(column):
                        data['fields'][column] = data['fields'][args.columns_copy[0]]
                    else:
                        raise CriticalError(f"The Column {column} is not present in airtable! Please create it and try again")

            if args.rename_key_column:
                if self.missing_field_single(args.rename_key_column[1]):
                    data['fields'][args.rename_key_column[1]] = data['fields'][args.rename_key_column[0]]
                    del data['fields'][args.rename_key_column[0]]
                else:
                    raise CriticalError(f"The Key Column {args.rename_key_column[1]} is not present in airtable! Please create it and try again")
        return all_data

        
 
            
