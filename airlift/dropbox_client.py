"""
Dropbox integration layer for Airlift.

This module manages Dropbox authentication, file uploads for attachments,
refresh-token updates, and folder cleanup operations.
"""

import os
import time
import threading
import dropbox
import logging
import json
import certifi
from datetime import datetime
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

from airlift.utils_exceptions import CriticalError
from dropbox import DropboxOAuth2FlowNoRedirect
from dropbox.sharing import RequestedVisibility, SharedLinkSettings


logger = logging.getLogger(__name__)

# OAuth scopes for Dropbox. files.content.read is required for temporary
# direct links; sharing.write is required for shared links used by Airtable.
DROPBOX_OAUTH_SCOPES = [
    "files.content.read",
    "files.content.write",
    "sharing.write",
]

def _configure_ssl_environment():
    """Configure SSL environment for proper certificate handling in PyInstaller"""
    try:
        # Try to use certifi's certificate bundle
        cert_path = certifi.where()
        if os.path.exists(cert_path):
            # Set environment variable for requests to use certifi certificates
            os.environ['REQUESTS_CA_BUNDLE'] = cert_path
            os.environ['SSL_CERT_FILE'] = cert_path
        else:
            # Fallback to system certificates
            logger.warning("certifi certificate file not found, using system certificates")
        
    except Exception as e:
        logger.warning(f"SSL environment configuration failed: {e}, using default")

class dropbox_client:
    def __init__(self, access_token, md: bool):
        # Configure SSL environment for proper certificate handling
        _configure_ssl_environment()
        
        try:
            try:
                creds = self._get_tokens(access_token)
                self.dbx = dropbox.Dropbox(
                    oauth2_refresh_token=creds[1],
                    app_key=creds[0]
                )
                logger.info("Created a Dropbox Client")
            except Exception:
                raise CriticalError('Failed to create the Dropbox client')
            
            # Set up folder structure
            if md:
                self.main_folder = "/Marker Data"
                try:
                    self.dbx.files_create_folder_v2("/Marker Data")
                except Exception as e:
                    logger.warning(f"The folder Marker Data already exists.")
            else:
                self.main_folder = "/Airlift"
                try:
                    self.dbx.files_create_folder_v2("/Airlift")
                except Exception as e:
                    logger.warning(f"The folder Airlift already exists.")

            c = datetime.now()
            self.sub_folder = f"{self.main_folder}{self.main_folder} {c.strftime('%Y-%m-%d')} {c.strftime('%H-%M-%S')}"

            try:
                self.dbx.files_create_folder_v2(self.sub_folder)
            except dropbox.exceptions.ApiError as e:
                logger.warning(f"The folder {self.sub_folder} already exists.")
                
        except Exception as e:
            raise CriticalError("Error during Dropbox client creation",e)

        self._api_lock = threading.Lock()
        self._use_temporary_links = True
        self._temporary_link_scope_logged = False

    @staticmethod
    def _auth_error_missing_read_scope(exc: BaseException) -> bool:
        text = str(exc).lower()
        return "files.content.read" in text or (
            "missing_scope" in text and "content.read" in text
        )

    def _get_tokens(self,access_token):
        try:
            with open(access_token,'r') as file:
                creds = json.load(file)
        except FileNotFoundError:
            logger.error(f"Access token file not found: {access_token}")
            raise CriticalError(f"Access token file not found: {access_token}")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in access token file: {e}")
            raise CriticalError(f"Invalid JSON in access token file: {e}")
        except Exception as e:
            logger.error(f"Error reading access token file: {type(e).__name__}: {str(e)}")
            raise CriticalError(f"Error reading access token file: {str(e)}")
        
        try:
            app_key = creds['app_key']
        except KeyError:
            logger.warning("app_key not present in json file")
            raise CriticalError("app_key not present in the json file, please check!")
        
        try:
            refresh_token = creds['refresh_token']
        except KeyError:
            try:
                auth_flow = DropboxOAuth2FlowNoRedirect(
                    app_key, 
                    use_pkce=True, 
                    token_access_type='offline',
                    scope=DROPBOX_OAUTH_SCOPES,
                )
                authorize_url = auth_flow.start()
                print("1. Go to: " + authorize_url)
                print("2. Click \"Allow\" (you might have to log in first).")
                print("3. Copy the authorization code.")
                auth_code = input("Enter the authorization code here: ").strip()
                try:
                    oauth_result = auth_flow.finish(auth_code)
                    refresh_token = oauth_result.refresh_token
                except Exception as e:
                    logger.warning("error during retreival of refresh token")
                    raise CriticalError("error during retreival of refresh token")
                # Save the refresh token to file
                with open(access_token,'r') as file:
                    creds_data = json.load(file)
                creds_data['refresh_token'] = refresh_token
                with open(access_token,'w') as file:
                    json.dump(creds_data,file,indent=2)
            except Exception as e:
                logger.warning("error during retreival of refresh token")
                raise CriticalError("error during retreival of refresh token")
        
        return (app_key,refresh_token)
        


    @staticmethod
    def _dropbox_relative_path(local_path: str) -> str:
        """Build a Dropbox path segment from a local filesystem path."""
        file_path = os.path.split(local_path)
        basename = file_path[1]
        if not file_path[0]:
            return basename
        last_dir = os.path.split(file_path[0])
        if not last_dir[0]:
            return basename
        return f"{last_dir[1]}/{basename}"

    @staticmethod
    def _to_direct_download_url(shared_url: str) -> str:
        """Convert a Dropbox share URL to a direct file URL for Airtable."""
        parsed = urlparse(shared_url)
        host = parsed.netloc.lower()
        if host.endswith("dropbox.com") and not host.startswith("dl."):
            host = "dl.dropboxusercontent.com"
        query = parse_qs(parsed.query, keep_blank_values=True)
        flat = {key: (values[0] if values else "") for key, values in query.items()}
        flat["dl"] = "1"
        if "/scl/" in parsed.path:
            flat["raw"] = "1"
        new_query = urlencode(flat)
        return urlunparse(
            (parsed.scheme or "https", host, parsed.path, "", new_query, "")
        )

    @staticmethod
    def _is_retryable_dropbox_error(exc: BaseException) -> bool:
        if isinstance(exc, (OSError, TimeoutError, ConnectionError)):
            return True
        if not isinstance(exc, dropbox.exceptions.ApiError):
            return False
        err = exc.error
        if hasattr(err, "is_too_many_requests") and err.is_too_many_requests():
            return True
        if hasattr(err, "is_too_many_write_operations") and err.is_too_many_write_operations():
            return True
        error_tag = getattr(err, "_tag", None) or getattr(err, "tag", None)
        return error_tag in {
            "too_many_requests",
            "too_many_write_operations",
            "internal_error",
            "transient_error",
        }

    def _call_with_retry(self, operation, description: str):
        delay_seconds = 2.0
        last_error: BaseException | None = None
        for attempt in range(1, 6):
            try:
                return operation()
            except Exception as exc:
                last_error = exc
                if (
                    not self._is_retryable_dropbox_error(exc)
                    or attempt == 5
                ):
                    raise
                logger.warning(
                    "Retrying Dropbox %s after %s (attempt %s/5): %s",
                    description,
                    type(exc).__name__,
                    attempt,
                    exc,
                )
                time.sleep(delay_seconds)
                delay_seconds = min(delay_seconds * 2, 60.0)
        if last_error:
            raise last_error
        raise RuntimeError(f"Dropbox operation failed: {description}")

    def _shared_link_url(self, dropbox_path: str) -> str:
        link_settings = SharedLinkSettings(
            requested_visibility=RequestedVisibility.public
        )
        try:
            shared_link_metadata = (
                self.dbx.sharing_create_shared_link_with_settings(
                    path=dropbox_path,
                    settings=link_settings,
                )
            )
            return self._to_direct_download_url(shared_link_metadata.url)
        except dropbox.exceptions.ApiError as exc:
            err = exc.error
            if hasattr(err, "is_shared_link_already_exists") and (
                err.is_shared_link_already_exists()
            ):
                existing = err.get_shared_link_already_exists()
                return self._to_direct_download_url(existing.url)
            links = self.dbx.sharing_list_shared_links(
                path=dropbox_path, direct_only=True
            )
            if links.links:
                return self._to_direct_download_url(links.links[0].url)
            raise

    def _airtable_download_url(self, dropbox_path: str) -> str:
        """Return a direct download URL Airtable can fetch when creating attachments."""
        if self._use_temporary_links:
            try:
                temporary = self.dbx.files_get_temporary_link(dropbox_path)
                return temporary.link
            except dropbox.exceptions.AuthError as exc:
                if self._auth_error_missing_read_scope(exc):
                    self._use_temporary_links = False
                    if not self._temporary_link_scope_logged:
                        logger.warning(
                            "Dropbox token is missing files.content.read; "
                            "using shared links (less reliable for large "
                            "files). Disconnect this app at "
                            "https://www.dropbox.com/account/connected_apps "
                            "then run: airlift --dropbox-token <file> "
                            "--dropbox-refresh-token"
                        )
                        self._temporary_link_scope_logged = True
                else:
                    raise
            except Exception as exc:
                logger.debug(
                    "Temporary Dropbox link failed for %s, using shared link: %s",
                    dropbox_path,
                    exc,
                )
        return self._shared_link_url(dropbox_path)

    def upload_to_dropbox(self, filename: str) -> str:
        local_path = os.path.normpath(filename)
        with open(local_path, "rb") as file_handle:
            image_data = file_handle.read()

        final_path = self._dropbox_relative_path(local_path)
        dropbox_path = f"{self.sub_folder}/{final_path}"

        # Dropbox client is not thread-safe; serialize API calls across workers.
        with self._api_lock:
            def _upload_and_link() -> str:
                self.dbx.files_upload(
                    image_data,
                    dropbox_path,
                    mode=dropbox.files.WriteMode.overwrite,
                )
                return self._airtable_download_url(dropbox_path)

            return self._call_with_retry(
                _upload_and_link,
                f"upload for {os.path.basename(local_path)}",
            )

    def empty_folder_contents(self) -> int:
        """Empty all contents from the main Dropbox folder without deleting the folder itself.
        
        Returns:
            int: Number of items deleted
        """
        from tqdm import tqdm
        
        deleted_count = 0
        
        try:
            logger.info(f"Fetching contents of folder: {self.main_folder}")
            
            # List all contents in the main folder
            result = self.dbx.files_list_folder(self.main_folder)
            entries = result.entries
            
            # Handle pagination if there are more entries
            while result.has_more:
                result = self.dbx.files_list_folder_continue(result.cursor)
                entries.extend(result.entries)
            
            if not entries:
                logger.info(f"No contents found in {self.main_folder}")
                return 0
            
            total_items = len(entries)
            logger.info(f"Found {total_items} items to delete in {self.main_folder}")
            
            # Create progress bar
            progress_bar = tqdm(total=total_items, desc="Emptying folder", leave=False)
            
            # Delete each entry (files and folders)
            for entry in entries:
                try:
                    self.dbx.files_delete_v2(entry.path_display)
                    deleted_count += 1
                    progress_bar.update(1)
                except dropbox.exceptions.ApiError as e:
                    logger.warning(f"Failed to delete {entry.path_display}: {e}")
            
            progress_bar.close()
            logger.info(f"Successfully deleted {deleted_count} items from {self.main_folder}")
            return deleted_count
            
        except dropbox.exceptions.ApiError as e:
            if "not_found" in str(e):
                logger.info(f"Folder {self.main_folder} does not exist or is empty")
                return 0
            logger.error(f"Error emptying folder: {e}")
            raise CriticalError(f"Failed to empty Dropbox folder: {e}")


def empty_dropbox_folder(access_token, md: bool) -> int:
    """Empty the contents of the Dropbox folder without creating subfolders.
    
    Args:
        access_token: Path to the JSON file with Dropbox credentials
        md: If True, use 'Marker Data' folder, otherwise use 'Airlift' folder
        
    Returns:
        int: Number of items deleted
    """
    from tqdm import tqdm
    
    # Configure SSL environment
    _configure_ssl_environment()
    
    try:
        # Load credentials
        with open(access_token, 'r') as file:
            creds = json.load(file)
        
        app_key = creds.get('app_key')
        refresh_token = creds.get('refresh_token')
        
        if not app_key:
            raise CriticalError("app_key not present in the json file")
        if not refresh_token:
            raise CriticalError("refresh_token not present in the json file")
        
        # Create Dropbox client
        dbx = dropbox.Dropbox(
            oauth2_refresh_token=refresh_token,
            app_key=app_key
        )
        
        # Determine folder path
        main_folder = "/Marker Data" if md else "/Airlift"
        
        logger.info(f"Fetching contents of folder: {main_folder}")
        
        # List all contents in the main folder
        try:
            result = dbx.files_list_folder(main_folder)
        except dropbox.exceptions.ApiError as e:
            if "not_found" in str(e):
                logger.info(f"Folder {main_folder} does not exist or is empty")
                return 0
            raise
        
        entries = result.entries
        
        # Handle pagination if there are more entries
        while result.has_more:
            result = dbx.files_list_folder_continue(result.cursor)
            entries.extend(result.entries)
        
        if not entries:
            logger.info(f"No contents found in {main_folder}")
            return 0
        
        total_items = len(entries)
        logger.info(f"Found {total_items} items to delete in {main_folder}")
        
        # Create progress bar
        progress_bar = tqdm(total=total_items, desc="Emptying folder", leave=False)
        
        deleted_count = 0
        
        # Delete each entry (files and folders)
        for entry in entries:
            try:
                dbx.files_delete_v2(entry.path_display)
                deleted_count += 1
                progress_bar.update(1)
            except dropbox.exceptions.ApiError as e:
                logger.warning(f"Failed to delete {entry.path_display}: {e}")
        
        progress_bar.close()
        logger.info(f"Successfully deleted {deleted_count} items from {main_folder}")
        return deleted_count
        
    except FileNotFoundError:
        raise CriticalError(f"Access token file not found: {access_token}")
    except json.JSONDecodeError as e:
        raise CriticalError(f"Invalid JSON in access token file: {e}")
    except Exception as e:
        logger.error(f"Error emptying Dropbox folder: {e}")
        raise CriticalError(f"Failed to empty Dropbox folder: {e}")


def change_refresh_access_token(access_token):
    try:
        with open(access_token,'r') as file:
            creds = json.loads(file.read())
    except FileNotFoundError:
        logger.error(f"Access token file not found: {access_token}")
        raise CriticalError(f"Access token file not found: {access_token}")
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in access token file: {e}")
        raise CriticalError(f"Invalid JSON in access token file: {e}")
    except Exception as e:
        logger.error(f"Error reading access token file: {type(e).__name__}: {str(e)}")
        raise CriticalError(f"Error reading access token file: {str(e)}")
        
    try:
        app_key = creds['app_key']
    except KeyError:
        logger.warning("app_key not present in json file")
        raise CriticalError("app_key not present in the json file, please check!")
    
    try:
        # Configure SSL environment before creating OAuth flow
        _configure_ssl_environment()
        # Create OAuth flow (SSL is handled at environment level)
        # Use explicit scopes for better security and clarity
        auth_flow = DropboxOAuth2FlowNoRedirect(
            app_key, 
            use_pkce=True, 
            token_access_type='offline',
            scope=DROPBOX_OAUTH_SCOPES,
        )
        authorize_url = auth_flow.start()
        print("STEP 1. Go to: " + authorize_url)
        print("STEP 2. Click \"Allow\" (you might have to log in first).")
        print("STEP 3. Copy the authorization code.")
        auth_code = input("Enter the authorization code here: ").strip()
        try:
            oauth_result = auth_flow.finish(auth_code)
            refresh_token = oauth_result.refresh_token
            granted_scope = getattr(oauth_result, "scope", None)
            with open(access_token,'r') as file:
                creds_data = json.load(file)
            creds_data['refresh_token'] = refresh_token
            with open(access_token,'w') as file:
                json.dump(creds_data,file,indent=2)
            logger.info("Refresh Token updated in the json file!")
            if granted_scope:
                print(f"STEP 4. Granted scopes: {granted_scope}")
                if "files.content.read" not in str(granted_scope):
                    print(
                        "WARNING: files.content.read was not granted. "
                        "Disconnect the app in Dropbox connected apps and "
                        "run --dropbox-refresh-token again."
                    )
            else:
                print(
                    "STEP 4. Re-open the authorize URL and confirm the app "
                    "requests read, write, and sharing access."
                )
        except Exception as e:
            logger.warning("error during retreival of refresh token")
            raise CriticalError("error during retreival of refresh token")
    except Exception as e:
        logger.warning("error during retreival of refresh token")
        raise CriticalError("error during retreival of refresh token")
