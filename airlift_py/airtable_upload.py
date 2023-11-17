from airlift_py.airtable_client import new_client
from typing import Any, Dict, Iterable, Iterator, List, Optional
from airlift_py.utils_exceptions import CriticalError
from tqdm import tqdm
import logging
from requests.exceptions import HTTPError
from airlift_py.airtable_error_handling import ClientError
from queue import Queue, Empty
import concurrent.futures
from airlift_py.dropbox_client import dropbox_client

logger = logging.getLogger(__name__)
ATDATA = List[Dict[str,Dict[str,str]]]


def upload_data(client: new_client, new_data:ATDATA, workers:int, dbx:str, dirname:str, attachment_columns:List[str],attachment_columns_map:List[str]) -> None:
    
    logger.info("Uploding data now!")
    with tqdm(total = len(new_data)) as progress_bar:
        try:
            data_queue = Queue()
            for data in new_data:
                data_queue.put(data)

            with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
                futures = [executor.submit(_worker,client,data_queue,progress_bar,dbx,attachment_columns,dirname,attachment_columns_map) for _ in range(workers)]
                concurrent.futures.wait(futures,timeout=None)

        except:
            raise CriticalError('Something went wrong while uploading the data')
    logger.info("Upload completed!")
    
def _worker(client:new_client,data_queue:Queue,progress_bar,dbx:dropbox_client,attachment_columns:List[str],dirname:str,attachment_columns_map:List[str]) -> None:            
    while True:
        try:
            data = data_queue.get_nowait()
            if attachment_columns_map:
                data['fields'][attachment_columns_map[1]] = ""
            try:
                for key,value in data['fields'].items():
                    if attachment_columns:
                        if dbx:
                            if key in attachment_columns:
                                if dirname:
                                    data['fields'][key] = [{"url":dbx.upload_to_dropbox(f"{dirname}/{value}")}]
                                else:
                                    data['fields'][key] = [{"url":dbx.upload_to_dropbox(f"{value}")}]

                    if attachment_columns_map:
                        if dbx:
                            if key == attachment_columns_map[0]:
                                if dirname:
                                    data['fields'][attachment_columns_map[1]] = [{"url":dbx.upload_to_dropbox(f"{dirname}/{value}")}]
                                else:
                                    data['fields'][attachment_columns_map[1]] = [{"url":dbx.upload_to_dropbox(f"{value}")}]

                        else:
                            raise CriticalError("Dropbox token not provided! Aborting the upload!")
                
                # print(data)
                client.single_upload(data)
                progress_bar.update(1)
            except HTTPError as e:
                ClientError(e)
            except Exception as e:
                print(e)
                raise CriticalError("An unexpected error occured! Please contact the developers.")
        except Empty:
            break
