from pydrive.drive import GoogleDrive 
from pydrive.auth import GoogleAuth 
import os 
import dropbox
import logging
from datetime import datetime
from airlift.utils_exceptions import CriticalError
logger = logging.getLogger(__name__)
class dropbox_client:
    def __init__(self,access_token,md):
    
        try:
            try:
                self.dbx = dropbox.Dropbox(access_token)
                logger.info("Created a Dropbox Client")
            except:
                raise CriticalError('Failed to create the Dropbox client')

            if md:
                self.main_folder = "/Marker Data"
                try:
                    self.dbx.files_create_folder("/Marker Data")
                except Exception as e:
                    print(f"The folder Marker Data already exists.")
            else:
                self.main_folder = "/Airlift"
                try:
                    self.dbx.files_create_folder("/Airlift")
                except Exception as e:
                    print(f"The folder Airlift already exists.")

            c = datetime.now()
            self.sub_folder = f"{self.main_folder}{self.main_folder} {c.strftime('%H:%M:%S')}"

            try:
                self.dbx.files_create_folder(self.sub_folder)
            except dropbox.exceptions.ApiError as e:
                print(f"The folder {self.sub_folder} already exists.")
        except Exception as e:
            raise CriticalError("Error during Dropbox client creation",e)


    def upload_to_dropbox(self,filename):
        with open(filename, 'rb') as f:
            image_data = f.read()
    
            dropbox_path = f"{self.sub_folder}/{filename}"
     
            # Upload the image
            self.dbx.files_upload(image_data, dropbox_path)

            shared_link_metadata = self.dbx.sharing_create_shared_link(path=dropbox_path)
            shared_url = shared_link_metadata.url

        
            direct_download_url = shared_url.replace('www.dropbox.com', 'dl.dropboxusercontent.com').replace('?dl=0', '?dl=1')

            return direct_download_url
