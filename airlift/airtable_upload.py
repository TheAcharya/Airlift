import pyairtable.api.table as ATtable
from airlift.csv_data import CSVRowType

def upload_data(client: ATtable, new_data:list[CSVRowType]) -> None:
    client.batch_create(new_data)