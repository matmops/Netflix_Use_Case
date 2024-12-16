import os
import configparser
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient

# Lire l'URL depuis le fichier info.ini
config = configparser.ConfigParser()
config.read('info.ini')
url = config.get('INFO', 'URL')

# Extraire les informations nécessaires de l'URL
blob_url_parts = url.split('/')
account_name = blob_url_parts[2].split('.')[0]
container_name = blob_url_parts[3]
blob_name = '/'.join(blob_url_parts[4:])

client_id = os.getenv('AZURE_AZURE_CLIENT_ID')

# Authentification avec l'identité assignée
credential = DefaultAzureCredential(managed_identity_client_id=client_id)
blob_service_client = BlobServiceClient(account_url=f"https://{account_name}.blob.core.windows.net", credential=credential)

# Récupérer le client du conteneur et du blob
container_client = blob_service_client.get_container_client(container_name)
blob_client = container_client.get_blob_client(blob_name)

# Télécharger le fichier
download_file_path = os.path.expanduser(f"~/file_to_process/{os.path.basename(blob_name)}")
os.makedirs(os.path.dirname(download_file_path), exist_ok=True)

with open(download_file_path, "wb") as download_file:
    download_stream = blob_client.download_blob()
    download_file.write(download_stream.readall())

print(f"Fichier téléchargé et stocké dans {download_file_path}")