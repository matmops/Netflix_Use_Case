from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient

# Remplacez par l'URL de votre compte de stockage
account_url = "https://netflixsa194.blob.core.windows.net/"
container_name = "raw"

# Authentification avec l'identité assignée
credential = DefaultAzureCredential()
blob_service_client = BlobServiceClient(account_url=account_url, credential=credential)

# Récupérer le client du conteneur
container_client = blob_service_client.get_container_client(container_name)

# Lister les blobs dans le conteneur
print("Liste des fichiers dans le conteneur :")
for blob in container_client.list_blobs():
    print(blob.name)
