import csv
import logging
from collections import Counter
from pathlib import Path
from typing import Any, Dict, Iterable, Iterator, List, Optional
import os

from airlift_py.utils_exceptions import CriticalError

CSVRowType = Dict[str, Any]

logger = logging.getLogger(__name__)


def csv_read(file_path: Path,fail_on_dup:bool) -> List[CSVRowType]:
    dirname = os.path.dirname(file_path)
    try:
        with open(file_path,"r",encoding="utf-8-sig") as csv_file:
            return _csv_read_rows(csv_file,fail_on_dup)
    except FileNotFoundError as e:
        logger.debug(f"error : {e}")
        raise CriticalError(f"File {file_path} not found") from e

def _csv_read_rows(csv_file:Iterable[str],fail_on_dup:bool) -> List[CSVRowType]:


    reader = csv.DictReader(csv_file,restval="")

    if not reader.fieldnames:
        raise CriticalError("CSV file has no columns")
    
    rows = list(reader)
    #print(list(reader.fieldnames))
    duplicate_columns = _list_duplicates(list(reader.fieldnames))

    if duplicate_columns:
        if fail_on_dup:
            raise CriticalError(f"Duplicate columns found in CSV :{duplicate_columns}")
        else:
            rows = _remove_duplicates(rows)

    records = []

    for x in rows:
        records.append({"fields":x})
    
    return records

def _list_duplicates(lst: List[str]) -> List[str]:
    return [lst_item for lst_item, count in Counter(lst).items() if count > 1]

def _remove_duplicates(rows:List[Dict]) -> List[Dict]:
    final_list = []
    for row in rows:
        new_dict = {}
        for key,value in row.items():
            if key:
                new_dict[key] = value
        final_list.append(new_dict)
    return final_list
