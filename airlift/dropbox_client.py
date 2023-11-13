from pydrive.drive import GoogleDrive 
from pydrive.auth import GoogleAuth 
import os 
import dropbox
import logging
logger = logging.getLogger(__name__)
class dropbox_client:
    def __init__(self,access_token):
        
        self.dbx = dropbox.Dropbox(access_token)
        logger.info("Created a dropbox client")

        try:
            self.dbx.files_create_folder("/airlift")
        except dropbox.exceptions.ApiError as e:
            print(f"The folder airlift already exists.")

    def upload_to_dropbox(self,filename):
        with open(filename, 'rb') as f:
            image_data = f.read()
            image_name = os.path.basename(filename)
    
            dropbox_path = f"/airlift/{image_name}"
           
            # Upload the image
            self.dbx.files_upload(image_data, dropbox_path)

            shared_link_metadata = self.dbx.sharing_create_shared_link(path=dropbox_path)
            shared_url = shared_link_metadata.url

        
            direct_download_url = shared_url.replace('www.dropbox.com', 'dl.dropboxusercontent.com').replace('?dl=0', '?dl=1')

            return direct_download_url