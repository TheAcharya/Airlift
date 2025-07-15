import os 
import dropbox
import logging
import json
import sys
import certifi
import ssl
from datetime import datetime
from airlift.utils_exceptions import CriticalError
from dropbox import DropboxOAuth2FlowNoRedirect
from typing import Dict


logger = logging.getLogger(__name__)

def _configure_ssl_context():
    """Configure SSL context with proper certificate handling for PyInstaller"""
    try:
        # Try to use certifi's certificate bundle
        cert_path = certifi.where()
        if os.path.exists(cert_path):
            ssl_context = ssl.create_default_context(cafile=cert_path)
            logger.debug(f"Using SSL certificates from: {cert_path}")
        else:
            # Fallback to system certificates
            ssl_context = ssl.create_default_context()
            logger.warning("certifi certificate file not found, using system certificates")
        
        return ssl_context
    except Exception as e:
        logger.warning(f"SSL context configuration failed: {e}, using default")
        return ssl.create_default_context()

class dropbox_client:
    def __init__(self,access_token,md:bool):
    
        try:
            # Configure SSL context before creating Dropbox client
            ssl_context = _configure_ssl_context()
            
            try:
                creds = self._get_tokens(access_token)
                # Create Dropbox client with custom SSL context
                self.dbx = dropbox.Dropbox(
                    oauth2_refresh_token=creds[1],
                    app_key=creds[0],
                    ssl_context=ssl_context
                )
                logger.info("Created a Dropbox Client")
            except Exception as e:
                logger.error(f"Dropbox client creation failed: {e}")
                raise CriticalError('Failed to create the Dropbox client')

            if md:
                self.main_folder = "/Marker Data"
                try:
                    self.dbx.files_create_folder("/Marker Data")
                except Exception as e:
                    logger.warning(f"The folder Marker Data already exists.")
            else:
                self.main_folder = "/Airlift"
                try:
                    self.dbx.files_create_folder("/Airlift")
                except Exception as e:
                    logger.warning(f"The folder Airlift already exists.")

            c = datetime.now()
            self.sub_folder = f"{self.main_folder}{self.main_folder} {c.strftime('%Y-%m-%d')} {c.strftime('%H-%M-%S')}"

            try:
                self.dbx.files_create_folder(self.sub_folder)
            except dropbox.exceptions.ApiError as e:
                logger.warning(f"The folder {self.sub_folder} already exists.")
        except Exception as e:
            raise CriticalError("Error during Dropbox client creation",e)


    def _get_tokens(self,access_token):
        with open(access_token,'r') as file:
            creds = json.load(file)
        
        try:
            app_key = creds['app_key']
        except:
            logger.warning("app_key not present in json file")
            raise CriticalError("app_key not present in the json file, please check!")
        
        try:
            refresh_token = creds['refresh_token']
        except:
            auth_flow = DropboxOAuth2FlowNoRedirect(app_key, use_pkce=True, token_access_type='offline')

            authorize_url = auth_flow.start()
            logger.warning("1. Go to: " + authorize_url)
            logger.warning("2. Click \"Allow\" (you might have to log in first).")
            logger.warning("3. Copy the authorization code.")
            auth_code = input("Enter the authorization code here: ").strip()

            try:
                oauth_result = auth_flow.finish(auth_code)
                refresh_token = oauth_result.refresh_token
                with open(access_token,'r') as file:
                    creds_data = json.load(file)
                
                creds_data['refresh_token'] = refresh_token

                with open(access_token,'w') as file:
                    json.dump(creds_data,file,indent=2)

            except Exception as e:
                logger.warning("error during retreival of refresh token")
                raise CriticalError("error during retreival of refresh token")
        
        return (app_key,refresh_token)
        


    def upload_to_dropbox(self,filename):
        with open(filename, 'rb') as f:
            image_data = f.read()

        
            file_path = os.path.split(filename)
            filename = file_path[1]

            if file_path[0]:
                last_dir = os.path.split(file_path[0])

            if last_dir:
                if last_dir[0] is None:
                    final_path = f'{filename}'
                else:
                    final_path = f'{last_dir[1]}/{filename}'
            else:
                final_path = f'{filename}'
            
            dropbox_path = f"{self.sub_folder}/{final_path}"
            self.dbx.files_upload(image_data, dropbox_path)

            shared_link_metadata = self.dbx.sharing_create_shared_link(path=dropbox_path)
            shared_url = shared_link_metadata.url

        
            direct_download_url = shared_url.replace('www.dropbox.com', 'dl.dropboxusercontent.com').replace('?dl=0', '?dl=1')

            return direct_download_url

def change_refresh_access_token(access_token):
    with open(access_token,'r') as file:
            creds = json.load(file)
        
    try:
        app_key = creds['app_key']
    except:
        logger.warning("app_key not present in json file")
        raise CriticalError("app_key not present in the json file, please check!")
    
    
    auth_flow = DropboxOAuth2FlowNoRedirect(app_key, use_pkce=True, token_access_type='offline')

    authorize_url = auth_flow.start()
    print("STEP 1. Go to: " + authorize_url)
    print("STEP 2. Click \"Allow\" (you might have to log in first).")
    print("STEP 3. Copy the authorization code.")
    auth_code = input("Enter the authorization code here: ").strip()

    try:
        oauth_result = auth_flow.finish(auth_code)
        refresh_token = oauth_result.refresh_token
        with open(access_token,'r') as file:
            creds_data = json.load(file)
        
        creds_data['refresh_token'] = refresh_token

        with open(access_token,'w') as file:
            json.dump(creds_data,file,indent=2)
        
        logger.info("Refresh Token updated in the json file!")

    except Exception as e:
        logger.warning("error during retreival of refresh token")
        raise CriticalError("error during retreival of refresh token")
