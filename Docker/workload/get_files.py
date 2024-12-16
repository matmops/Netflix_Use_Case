import json
import os
import configparser
from azure.identity import DefaultAzureCredential
from azure.servicebus import ServiceBusClient


fully_qualified_namespace = os.getenv('AZURE_SERVICEBUS_NAME_SPACE') + '.servicebus.windows.net'
queue_name = os.getenv('AZURE_SERVICEBUS_QUEUE_NAME')

client_id = os.getenv('AZURE_AZURE_CLIENT_ID')

# Authentification avec l'identité assignée
credential = DefaultAzureCredential(managed_identity_client_id=client_id)
servicebus_client = ServiceBusClient(fully_qualified_namespace=fully_qualified_namespace, credential=credential, logging_enable=True)

def process_message_with_lock_renewal():
    with servicebus_client:
        receiver = servicebus_client.get_queue_receiver(queue_name=queue_name, max_wait_time=5)
        with receiver:
            messages = receiver.receive_messages(max_message_count=1, max_wait_time=5)
            for message in messages:
                try:
                    # Extraire le contenu du message
                    message_body = str(message)
                    message_json = json.loads(message_body)
                    # Accéder à la balise "url" dans le dictionnaire imbriqué
                    url = message_json.get("data", {}).get("url")
                    message_id = message.message_id

                    # Stocker les informations dans un fichier INI
                    config = configparser.ConfigParser()
                    config['INFO'] = {
                        'URL': url,
                        'Message ID': message_id
                    }
                    with open('info.ini', 'w') as configfile:
                        config.write(configfile)

                    # Masquer le message pour que les autres ne le voient pas
                    receiver.defer_message(message)
                    print(f"Message {message_id} différé et informations stockées dans info.ini.")
                except Exception as e:
                    print(f"Erreur lors du traitement du message : {e}")

# Exemple d'utilisation
process_message_with_lock_renewal()