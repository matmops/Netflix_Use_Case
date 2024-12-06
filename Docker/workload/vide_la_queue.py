from azure.identity import DefaultAzureCredential
from azure.servicebus import ServiceBusClient

# Remplacez par votre connexion à la chaîne de connexion Service Bus et le nom de la file d'attente
fully_qualified_namespace = 'NetflixServiceBusNamespace.servicebus.windows.net'
queue_name = 'netflixbusqueue'

# Authentification avec l'identité assignée
credential = DefaultAzureCredential()
servicebus_client = ServiceBusClient(fully_qualified_namespace=fully_qualified_namespace, credential=credential, logging_enable=True)

def vider_la_queue():
    with servicebus_client:
        receiver = servicebus_client.get_queue_receiver(queue_name=queue_name, max_wait_time=5)
        with receiver:
            while True:
                messages = receiver.receive_messages(max_message_count=10, max_wait_time=5)
                if not messages:
                    print("La file d'attente est vide.")
                    break
                for message in messages:
                    receiver.complete_message(message)
                    print(f"Message {message.message_id} complété et supprimé de la file d'attente.")

            # Récupérer et compléter les messages différés
            deferred_messages = receiver.peek_messages(max_message_count=100)
            for deferred_message in deferred_messages:
                if deferred_message.sequence_number:
                    deferred_message = receiver.receive_deferred_messages(sequence_numbers=[deferred_message.sequence_number])
                    for message in deferred_message:
                        receiver.complete_message(message)
                        print(f"Message différé {message.message_id} complété et supprimé de la file d'attente.")

# Exemple d'utilisation
vider_la_queue()