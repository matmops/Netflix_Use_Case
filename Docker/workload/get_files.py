import json
import os
import configparser
import sys
import logging
from azure.identity import DefaultAzureCredential
from azure.servicebus import ServiceBusClient
from log_message import send_log_to_queue, log_message

# Logging configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

fully_qualified_namespace = os.getenv('AZURE_SERVICEBUS_NAME_SPACE') + '.servicebus.windows.net'
queue_name = os.getenv('AZURE_SERVICEBUS_QUEUE_NAME')

client_id = os.getenv('AZURE_CLIENT_ID')

# Authentication with managed identity
credential = DefaultAzureCredential(managed_identity_client_id=client_id)
servicebus_client = ServiceBusClient(fully_qualified_namespace=fully_qualified_namespace, credential=credential)

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
                    url = message_json.get("data", {}).get("url")
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
                except Exception as e:
                    logging.error(f"Error processing message: {e}")
                    sys.exit(1)

# Run function
process_message_with_lock_renewal()
