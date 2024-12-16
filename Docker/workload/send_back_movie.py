import os
import shutil
import configparser
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
from azure.servicebus import ServiceBusClient

# Lire le fichier info.ini pour obtenir le statut du check, l'URL et l'ID du message
config = configparser.ConfigParser()
config.read('info.ini')
check_status = config.get('INFO', 'CHECK_STATUS')
url = config.get('INFO', 'URL')
message_id = config.get('INFO', 'Message ID')

if check_status == "DONE":
    # Extraire les informations nécessaires de l'URL
    blob_url_parts = url.split('/')
    account_name = blob_url_parts[2].split('.')[0]
    container_name = blob_url_parts[3]
    blob_name = '/'.join(blob_url_parts[4:])
    file_name = os.path.basename(blob_name)

    client_id = os.getenv('AZURE_CLIENT_ID')

# Authentification avec l'identité assignée
    credential = DefaultAzureCredential(managed_identity_client_id=client_id)
    blob_service_client_read = BlobServiceClient(account_url=f"https://{os.getenv('AZURE_BLOB_READ')}.blob.core.windows.net", credential=credential)
    blob_service_client_write = BlobServiceClient(account_url=f"https://{os.getenv('AZURE_BLOB_WRITE')}.blob.core.windows.net", credential=credential)

    # Récupérer le client du conteneur et du blob pour lecture et écriture
    container_client_read = blob_service_client_read.get_container_client(container_name)
    container_client_write = blob_service_client_write.get_container_client(container_name)

    original_blob_client = container_client_read.get_blob_client(blob_name)
    converted_blob_client = container_client_write.get_blob_client(f"{os.path.splitext(blob_name)[0]}.mp4")

    # Chemin du fichier converti
    converted_file_path = os.path.expanduser(f"~/final/{os.path.splitext(file_name)[0]}.mp4")

    # Télécharger le fichier converti dans le blob d'écriture
    with open(converted_file_path, "rb") as data:
        converted_blob_client.upload_blob(data, overwrite=True)
        print(f"Fichier {converted_file_path} téléchargé dans le blob d'écriture.")

    # Supprimer le fichier initial .avi du blob de lecture
    original_blob_client.delete_blob()
    print(f"Fichier {blob_name} supprimé du blob de lecture.")

    # Gestion de la file d'attente Service Bus
    fully_qualified_namespace = os.getenv('AZURE_SERVICEBUS_NAME_SPACE') + '.servicebus.windows.net'
    queue_name = os.getenv('AZURE_SERVICEBUS_QUEUE_NAME')
    servicebus_client = ServiceBusClient(fully_qualified_namespace=fully_qualified_namespace, credential=credential, logging_enable=True)

    receiver = servicebus_client.get_queue_receiver(queue_name=queue_name, max_wait_time=5)
    with receiver:
        # Recevoir les messages différés
        deferred_messages = receiver.peek_messages(max_message_count=100)
        for deferred_message in deferred_messages:
            if deferred_message.message_id == message_id:
                # Récupérer le message différé en utilisant son sequence_number
                deferred_message = receiver.receive_deferred_messages(sequence_numbers=[deferred_message.sequence_number])
                for message in deferred_message:
                    if message.message_id == message_id:
                        receiver.complete_message(message)
                        print(f"Message différé {message.message_id} complété dans la file d'attente.")
                        break

    # Supprimer les dossiers locaux et leur contenu
    file_to_process_folder = os.path.expanduser("~/file_to_process")
    final_folder = os.path.expanduser("~/final")
    if os.path.exists(file_to_process_folder):
        shutil.rmtree(file_to_process_folder)
    if os.path.exists(final_folder):
        shutil.rmtree(final_folder)
    print(f"Dossiers {file_to_process_folder} et {final_folder} supprimés.")
else:
    print("Le statut du check n'est pas 'DONE'. Aucune action effectuée.")
