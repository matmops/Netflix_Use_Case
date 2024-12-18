import json
import os
import configparser
import sys
import logging
import time
from azure.identity import DefaultAzureCredential
from azure.servicebus import ServiceBusClient, ServiceBusMessage
from log_message import load_log_message, save_log_message, create_base_log

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logging.getLogger("azure").setLevel(logging.ERROR)  # Affiche uniquement les erreurs pour Azure SDK
logging.getLogger("azure-identity").setLevel(logging.ERROR)  # Filtrer les logs de `azure-identity`
logging.getLogger("azure.servicebus").setLevel(logging.ERROR)
instance_id = os.getenv("CONTAINER_APP_REPLICA_NAME")
# Environment Variables
fully_qualified_namespace = os.getenv('AZURE_SERVICEBUS_NAME_SPACE') + '.servicebus.windows.net'
queue_name = os.getenv('AZURE_SERVICEBUS_QUEUE_NAME')
dlq_name = f"{queue_name}/$DeadLetterQueue"
client_id = os.getenv('AZURE_CLIENT_ID')

# Authentication with managed identity
# Constants
MAX_RETRIES = 5  # Max retries before sending to DLQ

# Authentication
credential = DefaultAzureCredential(managed_identity_client_id=client_id)
servicebus_client = ServiceBusClient(fully_qualified_namespace=fully_qualified_namespace, credential=credential)

# Charger log_message depuis le fichier JSON
log_message = load_log_message()

# Vérifier que log_message est un dictionnaire
if log_message is None:
    logging.error("Log message is None. Exiting.")
    log_message = create_base_log(job_id=instance_id, message_id="run_all_12345")

def process_message_with_lock_renewal():
    with servicebus_client:
        receiver = servicebus_client.get_queue_receiver(queue_name=queue_name, max_wait_time=5)
        with receiver:
            messages = receiver.receive_messages(max_message_count=1, max_wait_time=5)

            if not messages:
                logging.warning("No file in queue. Exiting container.")
                sys.exit(0)

            for message in messages:
                try:
                    # Extract message content
                    message_body = str(message)
                    message_json = json.loads(message_body)
                    data = message_json.get("data")
                    if data is None:
                        logging.error(f"Missing 'data' in message: {message_body}")
                        continue

                    url = data.get("url")
                    message_id = message.message_id
                    log_message["file_url"] = url
                    log_message["message_id"] = message_id
                    # Store message details in info.ini
                    config = configparser.ConfigParser()
                    config['INFO'] = {'URL': url, 'Message ID': message_id}
                    with open('info.ini', 'w') as configfile:
                        config.write(configfile)

                    # Defer the message for processing
                    receiver.defer_message(message)
                    logging.info(f"Message {message_id} deferred and saved in info.ini.")

                    # Sauvegarder les logs après traitement
                    save_log_message(log_message)
                except Exception as e:
                    logging.error(f"Error processing message: {e}")
                    sys.exit(1)

# Run function
process_message_with_lock_renewal()
