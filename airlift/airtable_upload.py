import pyairtable.api.table as ATtable
from airlift.csv_data import CSVRowType
from typing import Any, Dict, Iterable, Iterator, List, Optional

def upload_data(client: ATtable, new_data:List[CSVRowType]) -> None:
    client.batch_create(new_data)