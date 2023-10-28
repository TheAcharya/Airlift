import pyairtable.api.table as ATtable
from airlift.csv_data import CSVRowType
from typing import Any, Dict, Iterable, Iterator, List, Optional
from airlift.utils_exceptions import CriticalError
from tqdm import tqdm
import logging
from requests.exceptions import HTTPError
from airlift.airtable_error_handling import ClientError
from queue import Queue, Empty
import concurrent.futures

logger = logging.getLogger(__name__)
ATDATA = List[Dict[str,Dict[str,str]]]


def upload_data(client: ATtable, new_data:ATDATA, workers:int) -> None:
    logger.info("uploding data now!")
    with tqdm(total = len(new_data)) as progress_bar:
        data_queue = Queue()
        for data in new_data:
            data_queue.put(data)

        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
            futures = [executor.submit(_worker,client,data_queue,progress_bar) for _ in range(workers)]
            concurrent.futures.wait(futures,timeout=None)

    logger.info("Upload done!!!")

def _worker(client,data_queue,progress_bar) -> None:            
    while True:
        try:
            data = data_queue.get_nowait()
            try:
                client.single_upload(data)
                progress_bar.update(1)
            except HTTPError as e:
                ClientError(e)
            except Exception as e:
                print(e)
                raise CriticalError("An unexpected error occured! please contact the developers")
        except Empty:
            break