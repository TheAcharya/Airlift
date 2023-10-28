import csv
import logging
from collections import Counter
from pathlib import Path
from typing import Any, Dict, Iterable, Iterator, List, Optional
import datetime
import email

from airlift.utils_exceptions import CriticalError
from airlift.airlift_data_guesser import guess_data_type
from tqdm import tqdm

CSVRowType = Dict[str, Any]

logger = logging.getLogger(__name__)


def csv_read(file_path: Path) -> List[CSVRowType]:
    try:
        with open(file_path,"r",encoding="utf-8-sig") as csv_file:
            return _csv_read_rows(csv_file)
    except FileNotFoundError as e:
        logger.debug(f"error : {e}")
        raise CriticalError(f"File {file_path} not found") from e

def _csv_read_rows(csv_file:Iterable[str]) -> List[CSVRowType]:
    reader = csv.DictReader(csv_file,restval="")

    if not reader.fieldnames:
        raise CriticalError("CSV file has no columns")
    
    duplicate_columns = _list_duplicates(list(reader.fieldnames))
    if duplicate_columns:
        raise CriticalError(f"Duplicate columns found in csv :{duplicate_columns}")
    
    rows = list(reader)
    
    converted_data = _convert_datatypes(rows)

    return converted_data

def _convert_datatypes(rows:list) -> List[CSVRowType]:

    for row in tqdm(rows):
        for key, value in row.items():
            data_type = guess_data_type(value)
            if data_type == "number":
                row[key] = float(value)
            elif data_type == "date":
                row[key] = datetime.datetime.strptime(value, "%Y-%m-%d")
            elif data_type == "email":
                row[key] = email.utils.parseaddr(value)[1]
            elif data_type == "bool":
                row[key] = False if value.lower() == "false" else True
            

    return list(rows)

def _list_duplicates(lst: List[str]) -> List[str]:
    return [lst_item for lst_item, count in Counter(lst).items() if count > 1]