import logging
import json
from typing import Any, Dict, List
from pyairtable import Api
from airlift.utils_exceptions import CriticalError, AirtableError
from airlift.csv_data import CSVRowType
from tqdm import tqdm

ATDATATYPE = Dict[str, Dict[str, str]]

logger = logging.getLogger(__name__)

class new_client:
    def __init__(self, token: str, base: str, table: str):
        self.api = token
        self.base_id = base
        self.table_id = table
        self.api_client = Api(self.api)
        self.table = self.api_client.table(self.base_id, self.table_id)
        self.base = self.api_client.base(self.base_id)
        # Store headers for direct API calls (same as original)
        self.headers = {
            "Authorization": "Bearer " + self.api,
            "Content-Type": "application/json"
        }
        logger.debug("Airtable Client Created")

    def single_upload(self, data: ATDATATYPE) -> None:
        # pyairtable expects just the fields dict
        record_data = data["fields"] if "fields" in data else data
        try:
            self.table.create(record_data, typecast=True)
        except Exception as e:
            logger.warning(f"Error creating records: {str(e)}")
            raise AirtableError("Unable to upload data!") from e

    def delete_all_records(self) -> int:
        """Delete all records from the Airtable table.
        
        Returns:
            int: Number of records deleted
        """
        try:
            # Get all record IDs from the table
            logger.info("Fetching all records from the table...")
            all_records = self.table.all()
            
            if not all_records:
                logger.info("No records found in the table.")
                return 0
            
            total_records = len(all_records)
            logger.info(f"Found {total_records} records to delete.")
            
            # Extract record IDs
            record_ids = [record["id"] for record in all_records]
            
            # Delete records in batches (Airtable API limit is 10 per request)
            deleted_count = 0
            batch_size = 10
            
            # Create progress bar
            progress_bar = tqdm(total=total_records, desc="Deleting records", leave=False)
            
            for i in range(0, len(record_ids), batch_size):
                batch = record_ids[i:i + batch_size]
                self.table.batch_delete(batch)
                deleted_count += len(batch)
                progress_bar.update(len(batch))
            
            progress_bar.close()
            logger.info(f"Successfully deleted {deleted_count} records from the table.")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error deleting records: {str(e)}")
            raise AirtableError(f"Failed to delete records: {str(e)}") from e

    def missing_field_single(self, field: str):
        airtable_table_fields = []
        tables = self._retreive_table()
        for x in tables:
            if x.id == self.table_id or x.name == self.table_id:
                for f in x.fields:
                    airtable_table_fields.append(f.name)
        return field in airtable_table_fields

    def _missing_fields_check(self, data: ATDATATYPE, args: dict):
        disable_bypass = args.disable_bypass_column_creation
        if args.rename_key_column:
            ignore_columns = [args.rename_key_column[0]]
        else:
            ignore_columns = None
        airtable_table_fields = []
        user_csv_fields = []
        tables = self._retreive_table()
        for x in tables:
            if x.id == self.table_id or x.name == self.table_id:
                for f in x.fields:
                    airtable_table_fields.append(f.name)
        if ignore_columns:
            for column in ignore_columns:
                airtable_table_fields.append(column)
        for csv_key in data[0]["fields"].keys():
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
                            del datas["fields"][column]
                        except Exception:
                            logger.warning(f"{column} not present in this row")
        else:
            logger.info("All the columns are verified and present in both the file and Airtable!")
        return data

    def _retreive_table(self):
        try:
            # Get the base schema which contains all tables
            schema = self.base.schema()
            return schema.tables
        except Exception as e:
            logger.warning(f"Error retrieving tables: {str(e)}")
            raise AirtableError(f"Error retrieving tables: {str(e)}") from e

    def _create_new_field(self, field_name: str) -> None:
        # Use pyairtable's underlying HTTP client to make the same API call as original
        URL = f"https://api.airtable.com/v0/meta/bases/{self.base_id}/tables/{self.table_id}/fields"
        new_field = {"name": field_name, "description": "This is a field created by Airtable", "type": "multilineText"}

        try:
            # Use pyairtable's underlying session to make the request
            response = self.api_client.session.post(URL, headers=self.headers, data=json.dumps(new_field))
            
            if response.status_code == 200:
                logger.info(f"Created new column {field_name} in Airtable")
            elif response.status_code == 422:
                logger.warning("Encountered an 422 error in creating a new column in Airtable!")
            else:
                logger.warning(f"unknown error : {response.text}")
        except Exception as e:
            logger.warning(f"Error creating field {field_name}: {str(e)}")

    def _rename_key_column_check(self, args: dict) -> None:
        if args.rename_key_column[1] == args.rename_key_column[0]:
            raise CriticalError("rename-key-column argument has same column name!")

    def create_uploadable_data(self, data: ATDATATYPE, args: dict):
        data = self._missing_fields_check(data, args)
        all_data = data
        logger.info("Creating airtable compatible data! Please wait")
        for data in all_data:
            # validation and creating new data fields
            if args.rename_key_column:
                self._rename_key_column_check(args=args)
            if args.attachment_columns_map:
                for attachment in args.attachment_columns_map:
                    data["fields"][attachment[1]] = ""
            if args.columns_copy:
                for column in args.columns_copy[1::]:
                    if self.missing_field_single(column):
                        data["fields"][column] = data["fields"][args.columns_copy[0]]
                    else:
                        raise CriticalError(f"The Column {column} is not present in airtable! Please create it and try again")
            if args.rename_key_column:
                if self.missing_field_single(args.rename_key_column[1]):
                    data["fields"][args.rename_key_column[1]] = data["fields"][args.rename_key_column[0]]
                    del data["fields"][args.rename_key_column[0]]
                else:
                    raise CriticalError(f"The Key Column {args.rename_key_column[1]} is not present in airtable! Please create it and try again")
        return all_data

        
 
            
