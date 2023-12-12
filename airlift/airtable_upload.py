import logging
import concurrent.futures
from airlift.airtable_client import new_client
from typing import Any, Dict, Iterable, Iterator, List, Optional
from queue import Queue, Empty
from airlift.dropbox_client import dropbox_client
from tqdm import tqdm


logger = logging.getLogger(__name__)
ATDATA = List[Dict[str, Dict[str, str]]]


def upload_data(client: new_client, new_data: ATDATA, workers: int, dbx: str, dirname: str,
                attachment_columns: List[str], attachment_columns_map: List[str], columns_copy: List[str], rename_key_column: List[str]) -> None:
    logger.info("Uploding data now!")
    progress_bar = tqdm(total=len(new_data))
    
    try:
        data_queue = Queue()
        for data in new_data:
            data_queue.put(data)

        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
            futures = [executor.submit(_worker, client, data_queue, progress_bar, dbx,
                                        attachment_columns, dirname, attachment_columns_map, columns_copy,rename_key_column) for _ in
                        range(workers)]
            concurrent.futures.wait(futures, timeout=None)

    except Exception as e:
        logger.error('Something went wrong while uploading the data: %s', str(e))
    


def _worker(client: new_client, data_queue: Queue, progress_bar, dbx: dropbox_client, attachment_columns: List[str],
            dirname: str, attachment_columns_map: List[str], columns_copy: List[str], rename_key_column:List[str]) -> None:
    while True:
        try:
            data = data_queue.get_nowait()
            if attachment_columns_map:
                data['fields'][attachment_columns_map[1]] = ""

            if columns_copy:
                for column in columns_copy[1::]:
                    if client.missing_field_single(column):
                        data['fields'][column] = data['fields'][columns_copy[0]]
                    else:
                        logger.warning(
                            f"The Column {column} is not present in airtable! Please create it and try again")
                        pass

            if rename_key_column:
                if client.missing_field_single(rename_key_column[1]):
                    data['fields'][rename_key_column[1]] = data['fields'][rename_key_column[0]]
                    del data['fields'][rename_key_column[0]]
                else:
                    logger.warning(
                            f"The Key Column {column} is not present in airtable! Please create it and try again")
                    pass

            try:
                for key, value in data['fields'].items():
                    if attachment_columns:
                        if dbx:
                            if key in attachment_columns:
                                try:
                                    if dirname:
                                        data['fields'][key] = [{"url": dbx.upload_to_dropbox(f"{dirname}/{value}")}]
                                    else:
                                        data['fields'][key] = [{"url": dbx.upload_to_dropbox(f"{value}")}]
                                except Exception as e:
                                    data['fields'][key] = ""

                    if attachment_columns_map:
                        if dbx:
                            if key == attachment_columns_map[0]:
                                try:
                                    if dirname:
                                        data['fields'][attachment_columns_map[1]] = [
                                            {"url": dbx.upload_to_dropbox(f"{dirname}/{value}")}]
                                    else: 
                                        data['fields'][attachment_columns_map[1]] = [
                                            {"url": dbx.upload_to_dropbox(f"{value}")}]
                                except Exception as e:
                                    data['fields'][attachment_columns_map[1]] = ""

                        else:
                            logger.error("Dropbox token not provided! Aborting the upload!")

                client.single_upload(data)
                progress_bar.update(1)
            except Exception as e:
                logger.error(str(e))
        except Empty:
            break
