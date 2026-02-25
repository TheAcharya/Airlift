import logging
import concurrent.futures
import threading
from airlift.airtable_client import new_client
from typing import Dict, List
from queue import Queue
from airlift.dropbox_client import dropbox_client
import os
from tqdm import tqdm
from airlift.utils_exceptions import CriticalError

logger = logging.getLogger(__name__)
ATDATA = List[Dict[str, Dict[str, str]]]


class Upload:
    def __init__(self,client: new_client, new_data:ATDATA,dbx:dropbox_client,args:dict):
        self.dbx = dbx
        self.new_data = new_data
        self.client = client
        self.dirname = os.path.dirname(args.csv_file)
        self.basename = os.path.basename(args.csv_file)
        self.attachment_columns=args.attachment_columns
        self.attachment_columns_map=args.attachment_columns_map
        self.columns_copy=args.columns_copy
        self.rename_key_column=args.rename_key_column
        self.workers = args.workers if args.workers else 5
        self.log = args.log
        self.stop_event = threading.Event()

    def write_log(self,file_path, line):
        with open(file_path, 'a') as file:
            file.write(line + '\n')

    def upload_data(self) -> None:
        logger.info("Uploding data now!")
        progress_bar = tqdm(total=len(self.new_data),leave=False)
        
        try:
            data_queue = Queue()
            for data in self.new_data:
                data_queue.put(data)

            with concurrent.futures.ThreadPoolExecutor(max_workers=self.workers) as executor:
                futures = [executor.submit(self._worker,data_queue, progress_bar) for _ in
                            range(self.workers)]    
                
                for future in concurrent.futures.as_completed(futures):
                    try:
                        future.result()  # This will re-raise any exception caught in the worker
                    except CriticalError as e:
                        logger.error('A critical error occurred in one of the worker threads: %s', str(e))
                        self.stop_event.set()  # Signal other workers to stop
                        break
                #concurrent.futures.wait(futures, timeout=None)

        except Exception as e:
            #logger.error('Something went wrong while uploading the data: %s', str(e))
            raise CriticalError('Something went wrong while uploading the data')
        


    def _worker(self,data_queue: Queue, progress_bar) -> None:
        while True:
            if self.stop_event.is_set():
                break
            try:
                data = data_queue.get_nowait()
                for key, value in data['fields'].items():
                    if self.attachment_columns:
                        if self.dbx:
                            if key in self.attachment_columns:
                                try:
                                    if self.dirname:
                                        file_path = f"{self.dirname}/{value}"
                                        data['fields'][key] = [{"url": self.dbx.upload_to_dropbox(file_path)}]
                                    else:
                                        file_path = f"{value}"
                                        data['fields'][key] = [{"url": self.dbx.upload_to_dropbox(file_path)}]
                                    
                                except Exception as e:
                                    logger.error(f"Error uploading {value}: {type(e).__name__}: {str(e)}")
                                    self.write_log(self.log,f"{value} Could not be found!")
                                    tqdm.write(f"{value} Could not be found!")
                                    data['fields'][key] = ""

                    if self.attachment_columns_map:
                        if self.dbx:
                            for attachments in self.attachment_columns_map:
                                if key == attachments[0]:
                                    try:
                                        if self.dirname:
                                            file_path = f"{self.dirname}/{value}"
                                            data['fields'][attachments[1]] = [
                                                {"url": self.dbx.upload_to_dropbox(file_path)}]
                                        else: 
                                            file_path = f"{value}"
                                            data['fields'][attachments[1]] = [
                                                {"url": self.dbx.upload_to_dropbox(file_path)}]
                                    except Exception as e:
                                        logger.error(f"Error uploading {value}: {type(e).__name__}: {str(e)}")
                                        self.write_log(self.log,f"{value} Could not be found!")
                                        tqdm.write(f"{value} Could not be found!")
                                        data['fields'][attachments[1]] = ""
                                #ic(data['fields'])

                        else:
                            logger.error("Dropbox token not provided! Aborting the upload!")

                self.client.single_upload(data)
                progress_bar.update(1)
            except Exception as e:
                if data_queue.empty():
                    break
                else:
                    logger.error(e)
                    raise CriticalError

                

