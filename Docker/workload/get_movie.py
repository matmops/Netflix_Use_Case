import os
import configparser
import logging
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient

# Logging configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Read info.ini
config = configparser.ConfigParser()
config.read('info.ini')
url = config.get('INFO', 'URL')
message_id = config.get('INFO', 'Message ID')

# Extract necessary details from the URL
blob_url_parts = url.split('/')
account_name = blob_url_parts[2].split('.')[0]
container_name = blob_url_parts[3]
blob_name = '/'.join(blob_url_parts[4:])

# Authentication
client_id = os.getenv('AZURE_CLIENT_ID')
credential = DefaultAzureCredential(managed_identity_client_id=client_id)
blob_service_client = BlobServiceClient(account_url=f"https://{account_name}.blob.core.windows.net", credential=credential)

# Check file format
if not blob_name.lower().endswith('.avi'):
    logging.error("Invalid file format. Only AVI files are accepted.")
    logging.info(f"Closing message with ID {message_id}.")
    sys.exit(1)

# Download the file
download_file_path = os.path.expanduser(f"~/file_to_process/{os.path.basename(blob_name)}")
os.makedirs(os.path.dirname(download_file_path), exist_ok=True)

with open(download_file_path, "wb") as download_file:
    blob_client = blob_service_client.get_blob_client(container_name, blob_name)
    download_stream = blob_client.download_blob()
    download_file.write(download_stream.readall())

logging.info(f"File downloaded to {download_file_path}")
