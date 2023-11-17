import json
import logging
from collections import Counter
from pathlib import Path
from typing import Any, Dict, Iterable, Iterator, List, Optional
import datetime
import email

from airlift_py.utils_exceptions import CriticalError
from airlift_py.airlift_data_guesser import guess_data_type

CSVRowType = Dict[str, Any]

logger = logging.getLogger(__name__)


def json_read(file_path: Path,fail_on_dup:bool) -> List[CSVRowType]:
    try:
        with open(file_path,"r",encoding="utf-8-sig") as json_file:
            return _json_read_rows(json_file,fail_on_dup)
    except FileNotFoundError as e:
        logger.debug(f"error : {e}")
        raise CriticalError(f"File {file_path} not found") from e

def _json_read_rows(json_file:Iterable[str],fail_on_dup:bool) -> List[CSVRowType]:
    reader = json.load(json_file)
    
    if not reader:
        raise CriticalError("JSON file has no data")
    
    records = []
    for each_data in reader:
        
        records.append({"fields":each_data})
    
    return records
    
