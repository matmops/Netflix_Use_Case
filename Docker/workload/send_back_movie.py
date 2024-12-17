import os
import shutil
import configparser
import logging
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
from azure.servicebus import ServiceBusClient

# Logging configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Read the info.ini file to get the check status, URL, and message ID
config = configparser.ConfigParser()
config.read('info.ini')
check_status = config.get('INFO', 'CHECK_STATUS')
url = config.get('INFO', 'URL')
message_id = config.get('INFO', 'Message ID')

if check_status == "DONE":
    try:
        # Extract necessary information from the URL
        blob_url_parts = url.split('/')
        account_name = blob_url_parts[2].split('.')[0]
        container_name = blob_url_parts[3]
        blob_name = '/'.join(blob_url_parts[4:])
        file_name = os.path.basename(blob_name)

        client_id = os.getenv('AZURE_CLIENT_ID')

        # Authentication with managed identity
        credential = DefaultAzureCredential(managed_identity_client_id=client_id)
        blob_service_client_raw = BlobServiceClient(
            account_url=f"https://{os.getenv('AZURE_STORAGE_ACCOUNT_NAME_RAW')}.blob.core.windows.net",
            credential=credential
        )
        blob_service_client_final = BlobServiceClient(
            account_url=f"https://{os.getenv('AZURE_STORAGE_ACCOUNT_NAME_FINAL')}.blob.core.windows.net",
            credential=credential
        )

        # Retrieve the container and blob clients for read and write
        container_client_read = blob_service_client_raw.get_container_client(os.getenv('AZURE_BLOB_READ'))
        container_client_write = blob_service_client_final.get_container_client(os.getenv('AZURE_BLOB_WRITE'))

        original_blob_client = container_client_read.get_blob_client(blob_name)
        converted_blob_client = container_client_write.get_blob_client(f"{os.path.splitext(blob_name)[0]}.mp4")

        # Path to the converted file
        converted_file_path = os.path.expanduser(f"~/final/{os.path.splitext(file_name)[0]}.mp4")

        # Upload the converted file to the target blob container
        try:
            with open(converted_file_path, "rb") as data:
                converted_blob_client.upload_blob(data, overwrite=True)
                logging.info(f"File {converted_file_path} uploaded to the target blob container.")
        except Exception as e:
            logging.error(f"Failed to upload the file to the target container: {e}")
            raise e

        # Delete the original .avi file from the source blob
        try:
            original_blob_client.delete_blob()
            logging.info(f"File {blob_name} successfully deleted from the source blob container.")
        except Exception as e:
            logging.error(f"Failed to delete the original file from the source container: {e}")
            raise e

        # Service Bus Queue management
        fully_qualified_namespace = os.getenv('AZURE_SERVICEBUS_NAME_SPACE') + '.servicebus.windows.net'
        queue_name = os.getenv('AZURE_SERVICEBUS_QUEUE_NAME')

        try:
            servicebus_client = ServiceBusClient(fully_qualified_namespace=fully_qualified_namespace, credential=credential)
            with servicebus_client:
                receiver = servicebus_client.get_queue_receiver(queue_name=queue_name, max_wait_time=5)
                with receiver:
                    deferred_messages = receiver.peek_messages(max_message_count=100)
                    for deferred_message in deferred_messages:
                        if deferred_message.message_id == message_id:
                            deferred_message = receiver.receive_deferred_messages(
                                sequence_numbers=[deferred_message.sequence_number]
                            )
                            for message in deferred_message:
                                if message.message_id == message_id:
                                    receiver.complete_message(message)
                                    logging.info(f"Deferred message {message.message_id} completed in the queue.")
                                    break
        except Exception as e:
            logging.error(f"Error managing the Service Bus queue: {e}")
            raise e

        # Clean up local folders
        file_to_process_folder = os.path.expanduser("~/file_to_process")
        final_folder = os.path.expanduser("~/final")

        try:
            if os.path.exists(file_to_process_folder):
                shutil.rmtree(file_to_process_folder)
                logging.info(f"Directory {file_to_process_folder} successfully deleted.")
            if os.path.exists(final_folder):
                shutil.rmtree(final_folder)
                logging.info(f"Directory {final_folder} successfully deleted.")
        except Exception as e:
            logging.error(f"Error while cleaning up local directories: {e}")
            raise e

    except Exception as main_error:
        logging.error(f"An error occurred during the send_back_movie process: {main_error}")
        exit(1)

else:
    logging.warning("The check status is not 'DONE'. No action will be performed.")
    exit(0)
