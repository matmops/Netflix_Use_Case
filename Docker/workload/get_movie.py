import os
import configparser
import logging
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
from azure.servicebus import ServiceBusClient

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logging.getLogger("azure").setLevel(logging.ERROR)  # Affiche uniquement les erreurs pour Azure SDK
logging.getLogger("azure-identity").setLevel(logging.ERROR)  # Filtrer les logs de `azure-identity`
logging.getLogger("azure.servicebus").setLevel(logging.ERROR)

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
fully_qualified_namespace = os.getenv('AZURE_SERVICEBUS_NAME_SPACE') + '.servicebus.windows.net'
queue_name = os.getenv('AZURE_SERVICEBUS_QUEUE_NAME')

credential = DefaultAzureCredential(managed_identity_client_id=client_id)
blob_service_client = BlobServiceClient(account_url=f"https://{account_name}.blob.core.windows.net", credential=credential)
servicebus_client = ServiceBusClient(fully_qualified_namespace=fully_qualified_namespace, credential=credential)

# Check file format
if not blob_name.lower().endswith('.avi'):
    logging.error("Invalid file format. Only AVI files are accepted.")

    # Connect to the Service Bus and close the message
    try:
        with servicebus_client:
            receiver = servicebus_client.get_queue_receiver(queue_name=queue_name, max_wait_time=5)
            with receiver:
                # Peek deferred messages to find the one with the correct ID
                deferred_messages = receiver.peek_messages(max_message_count=100)
                for deferred_message in deferred_messages:
                    if deferred_message.message_id == message_id:
                        # Receive the deferred message and complete it
                        deferred_message = receiver.receive_deferred_messages(sequence_numbers=[deferred_message.sequence_number])
                        for message in deferred_message:
                            if message.message_id == message_id:
                                receiver.complete_message(message)
                                logging.info(f"Message with ID {message_id} closed successfully.")
                                break
                else:
                    logging.warning(f"Message with ID {message_id} not found in the deferred queue.")
    except Exception as e:
        logging.error(f"Error closing the message in Service Bus: {e}")
    
    # Exit the script after closing the message
    exit(1)

# Download the file
download_file_path = os.path.expanduser(f"~/file_to_process/{os.path.basename(blob_name)}")
os.makedirs(os.path.dirname(download_file_path), exist_ok=True)

try:
    with open(download_file_path, "wb") as download_file:
        blob_client = blob_service_client.get_blob_client(container_name, blob_name)
        download_stream = blob_client.download_blob()
        download_file.write(download_stream.readall())
    logging.info(f"File downloaded to {download_file_path}")
except Exception as e:
    logging.error(f"Error downloading file {blob_name}: {e}")
    exit(1)
