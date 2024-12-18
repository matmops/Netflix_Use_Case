# log_message.py
import os
import logging
import json
from azure.identity import DefaultAzureCredential
from azure.servicebus import ServiceBusClient, ServiceBusMessage
from datetime import datetime

# Logging configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

log_file_path = "log_message.json"  # Chemin du fichier de log

# Charger le log depuis le fichier JSON
def load_log_message():
    if os.path.exists(log_file_path):
        with open(log_file_path, "r") as f:
            return json.load(f)
    else:
        return None  # Si le fichier n'existe pas encore, retourner None

# Sauvegarder le log dans le fichier JSON
def save_log_message(log_message):
    with open(log_file_path, "w") as f:
        json.dump(log_message, f, indent=4)

# Send log message to Service Bus queue
def send_log_to_queue(log_message, retries=3):
    for attempt in range(retries):
        try:
            fully_qualified_namespace = os.getenv('AZURE_SERVICEBUS_NAME_SPACE') + '.servicebus.windows.net'
            queue_name = os.getenv('AZURE_SERVICEBUS_QUEUE_NAME_LOG')
            client_id = os.getenv('AZURE_CLIENT_ID')

            credential = DefaultAzureCredential(managed_identity_client_id=client_id)
            servicebus_client = ServiceBusClient(fully_qualified_namespace=fully_qualified_namespace, credential=credential)
            
            with servicebus_client:
                sender = servicebus_client.get_queue_sender(queue_name=queue_name)
                with sender:
                    message = ServiceBusMessage(json.dumps(log_message))
                    sender.send_messages(message)
                    logging.info("Log message successfully sent to the queue.")
            break
        except Exception as e:
            logging.error(f"Attempt {attempt + 1} failed: {e}")
            if attempt == retries - 1:
                raise e

# Base log message structure
def create_base_log(job_id, message_id):
    return {
        "job_id": job_id,
        "message_id": message_id,
        "status": "EN COURS",
        "error_message": None,
        "start_time": datetime.utcnow().isoformat() + "Z",
        "end_time": None,
        "file_format": None,
        "container_id": None,
        "file_url": None
    }
