import configparser
from azure.identity import DefaultAzureCredential
from azure.servicebus import ServiceBusClient

# Lire le fichier info.ini pour obtenir le statut du check, l'URL et l'ID du message
config = configparser.ConfigParser()
config.read('info.ini')

message_id = config.get('INFO', 'Message ID')

print(message_id)
    # Authentification avec l'identité assignée
credential = DefaultAzureCredential()

    # Compléter le message dans la file d'attente
fully_qualified_namespace = 'NetflixServiceBusNamespace.servicebus.windows.net'
queue_name = 'netflixbusqueue'
servicebus_client = ServiceBusClient(fully_qualified_namespace=fully_qualified_namespace, credential=credential, logging_enable=True)

with servicebus_client:
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
                break
        else:
            print(f"Aucun message différé avec l'ID {message_id} trouvé.")