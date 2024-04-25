import json
import logging
import datetime
import email
from collections import Counter
from pathlib import Path
from typing import Any, Dict, Iterable, Iterator, List, Optional

from airlift.utils_exceptions import CriticalError
from airlift.airlift_data_guesser import guess_data_type
from icecream import ic

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
    
