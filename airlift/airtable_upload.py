"""
Concurrent upload worker pipeline for Airlift.

This module coordinates threaded row uploads and attachment handling between
Dropbox and Airtable clients.
"""

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

    def write_log(self, file_path, line: str) -> None:
        if not file_path:
            return
        with open(file_path, "a", encoding="utf-8") as file:
            file.write(line + "\n")

    def _attachment_local_path(self, value: str) -> str:
        if isinstance(value, str):
            value = value.strip()
        if self.dirname:
            return os.path.normpath(os.path.join(self.dirname, value))
        return os.path.normpath(value)

    def _attachment_payload(
        self, file_path: str, download_url: str
    ) -> List[Dict[str, str]]:
        return [
            {
                "url": download_url,
                "filename": os.path.basename(file_path),
            }
        ]

    def _upload_attachment_for_field(
        self, data: Dict, field_name: str, value: str
    ) -> None:
        if value is None or (isinstance(value, str) and not value.strip()):
            raise FileNotFoundError("Attachment filename is empty")
        file_path = self._attachment_local_path(value)
        if not os.path.isfile(file_path):
            raise FileNotFoundError(
                f"Attachment file not found: {file_path}"
            )
        download_url = self.dbx.upload_to_dropbox(file_path)
        data["fields"][field_name] = self._attachment_payload(
            file_path, download_url
        )

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
                                    self._upload_attachment_for_field(
                                        data, key, value
                                    )
                                except Exception as e:
                                    logger.error(
                                        "Attachment upload failed [%s] %s: "
                                        "%s: %s",
                                        key,
                                        value,
                                        type(e).__name__,
                                        e,
                                    )
                                    self.write_log(
                                        self.log,
                                        f"{value} attachment failed: {e}",
                                    )
                                    tqdm.write(
                                        f"{value} attachment failed: {e}"
                                    )
                                    data["fields"][key] = []

                    if self.attachment_columns_map:
                        if self.dbx:
                            for attachments in self.attachment_columns_map:
                                if key == attachments[0]:
                                    try:
                                        self._upload_attachment_for_field(
                                            data, attachments[1], value
                                        )
                                    except Exception as e:
                                        logger.error(
                                            "Attachment upload failed "
                                            "[%s -> %s] %s: %s: %s",
                                            attachments[0],
                                            attachments[1],
                                            value,
                                            type(e).__name__,
                                            e,
                                        )
                                        self.write_log(
                                            self.log,
                                            f"{value} attachment failed: {e}",
                                        )
                                        tqdm.write(
                                            f"{value} attachment failed: {e}"
                                        )
                                        data["fields"][attachments[1]] = []
                                #ic(data['fields'])

                        else:
                            logger.error("Dropbox token not provided! Aborting the upload!")

                if self.attachment_columns_map:
                    for _source, target in self.attachment_columns_map:
                        attachment_value = data["fields"].get(target)
                        if attachment_value == []:
                            logger.warning(
                                "%s has no attachment (upload failed or "
                                "file missing)",
                                target,
                            )
                self.client.single_upload(data)
                progress_bar.update(1)
            except Exception as e:
                if data_queue.empty():
                    break
                else:
                    logger.error(e)
                    raise CriticalError

                

