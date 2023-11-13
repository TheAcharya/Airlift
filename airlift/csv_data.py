import csv
import logging
from collections import Counter
from pathlib import Path
from typing import Any, Dict, Iterable, Iterator, List, Optional
import datetime
import email
import os
from airlift.dropbox_client import dropbox_client
from tqdm import tqdm
from queue import Queue, Empty
import multiprocessing
import concurrent.futures

from airlift.utils_exceptions import CriticalError
from airlift.airlift_data_guesser import guess_data_type

CSVRowType = Dict[str, Any]

logger = logging.getLogger(__name__)


def csv_read(file_path: Path,fail_on_dup:bool,attachment_columns:List[str],dropbox_token:str) -> List[CSVRowType]:
    dirname = os.path.dirname(file_path)
    try:
        with open(file_path,"r",encoding="utf-8-sig") as csv_file:
            return _csv_read_rows(csv_file,fail_on_dup,dirname,attachment_columns,dropbox_token)
    except FileNotFoundError as e:
        logger.debug(f"error : {e}")
        raise CriticalError(f"File {file_path} not found") from e

def _csv_read_rows(csv_file:Iterable[str],fail_on_dup:bool,dirname:str,attachment_columns:List[str],dropbox_token:str) -> List[CSVRowType]:

    if dropbox_token:
        dbx = dropbox_client(dropbox_token)
    else:
        dbx = None

    reader = csv.DictReader(csv_file,restval="")

    if not reader.fieldnames:
        raise CriticalError("CSV file has no columns")
    
    rows = list(reader)
    #print(list(reader.fieldnames))
    duplicate_columns = _list_duplicates(list(reader.fieldnames))

    if duplicate_columns:
        if fail_on_dup:
            raise CriticalError(f"Duplicate columns found in csv :{duplicate_columns}")
        else:
            rows = _remove_duplicates(rows)

    converted_data = _convert_datatypes(rows,dirname,attachment_columns,dbx)

    records = []

    for x in converted_data:
        records.append({"fields":x})
    
    return records

def _convert_datatypes(rows:List[Dict],dirname:str,attachment_columns:List[str],dbx:dropbox_client) -> List[CSVRowType]:

    manager = multiprocessing.Manager()
    shared_list = manager.list()

    if dbx:
        print("Uploading image to dropbox!")

    with tqdm(total = len(rows)) as progress_bar:
        data_queue = Queue()
        for row in rows:
            data_queue.put(row)

        with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
            futures = [executor.submit(_worker,dirname,attachment_columns,dbx,data_queue,shared_list,progress_bar) for _ in range(6)]
            concurrent.futures.wait(futures,timeout=None) 


    return list(shared_list)

def _worker(dirname:str,attachment_columns:List[str],dbx:dropbox_client,data_queue:Queue,shared_list,progress_bar):
    while True:
        try:
            row = data_queue.get_nowait()
            try:
                for key, value in row.items():

                    data_type = guess_data_type(value)
                    if attachment_columns:
                        if dbx:
                            if key in attachment_columns:
                                if dirname:
                                    row[key] = [{"url":dbx.upload_to_dropbox(f"{dirname}/{value}")}]
                                else:
                                    row[key] = [{"url":dbx.upload_to_dropbox(f"{dirname}/{value}")}]
                        else:
                            raise CriticalError("dropbox token not provided! aborting the upload")
                    if data_type == "number":
                        row[key] = float(value)
                    elif data_type == "date":
                        row[key] = datetime.datetime.strptime(value, "%Y-%m-%d")
                    elif data_type == "email":
                        row[key] = email.utils.parseaddr(value)[1]
                    elif data_type == "bool":
                        row[key] = False if value.lower() == "false" else True

                shared_list.append(row)
                progress_bar.update(1)
            except Exception as e:
                raise CriticalError(e)
        except Empty:
            break
            

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
