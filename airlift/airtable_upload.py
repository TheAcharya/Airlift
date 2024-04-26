import logging
import concurrent.futures
from airlift.airtable_client import new_client
from typing import Any, Dict, Iterable, Iterator, List, Optional
from queue import Queue, Empty
from airlift.dropbox_client import dropbox_client
import os
from tqdm import tqdm
from icecream import ic
from airlift.dropbox_client import dropbox_client

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

        ic(self.attachment_columns_map)

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
                concurrent.futures.wait(futures, timeout=None)

        except Exception as e:
            logger.error('Something went wrong while uploading the data: %s', str(e))
        


    def _worker(self,data_queue: Queue, progress_bar) -> None:
        while True:
            try:
                data = data_queue.get_nowait()
                
                if self.attachment_columns_map:
                    for attachment in self.attachment_columns_map:
                        data['fields'][attachment[1]] = ""

                if self.columns_copy:
                    for column in self.columns_copy[1::]:
                        if self.client.missing_field_single(column):
                            data['fields'][column] = data['fields'][self.columns_copy[0]]
                        else:
                            logger.warning(
                                f"The Column {column} is not present in airtable! Please create it and try again")
                            pass

                if self.rename_key_column:
                    if self.client.missing_field_single(self.rename_key_column[1]):
                        data['fields'][self.rename_key_column[1]] = data['fields'][self.rename_key_column[0]]
                        del data['fields'][self.rename_key_column[0]]
                    else:
                        logger.warning(
                                f"The Key Column {column} is not present in airtable! Please create it and try again")
                        pass

                try:
                    for key, value in data['fields'].items():
                        if self.attachment_columns:
                            if self.dbx:
                                if key in self.attachment_columns:
                                    try:
                                        if self.dirname:
                                            data['fields'][key] = [{"url": self.dbx.upload_to_dropbox(f"{self.dirname}/{value}")}]
                                        else:
                                            data['fields'][key] = [{"url": self.dbx.upload_to_dropbox(f"{value}")}]
                                        
                                    except Exception as e:
                                        tqdm.write(f"{value} Could not be found!")
                                        data['fields'][key] = ""

                        if self.attachment_columns_map:
                            if self.dbx:
                                for attachments in self.attachment_columns_map:
                                    if key == attachments[0]:
                                        try:
                                            if self.dirname:
                                                data['fields'][attachments[1]] = [
                                                    {"url": self.dbx.upload_to_dropbox(f"{self.dirname}/{value}")}]
                                            else: 
                                                data['fields'][attachments[1]] = [
                                                    {"url": self.dbx.upload_to_dropbox(f"{value}")}]
                                        except Exception as e:
                                            tqdm.write(f"{value} Could not be found!")
                                            data['fields'][attachments[1]] = ""
                                    #ic(data['fields'])

                            else:
                                logger.error("Dropbox token not provided! Aborting the upload!")

                    self.client.single_upload(data)
                    progress_bar.update(1)
                except Exception as e:
                    logger.error(e)
                    logger.error('Error at %s', 'division', exc_info=e)
            except Empty:
                break

