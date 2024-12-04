import os
from azure.servicebus import ServiceBusClient, ServiceBusMessage

# Utiliser les informations d'identification managées
connection_str = os.environ["SERVICE_BUS_CONNECTION_STR"]
queue_name = os.environ["SERVICE_BUS_QUEUE_NAME"]

def main():
    servicebus_client = ServiceBusClient.from_connection_string(conn_str=connection_str, logging_enable=True)
    with servicebus_client:
        receiver = servicebus_client.get_queue_receiver(queue_name=queue_name, max_wait_time=5)
        with receiver:
            for msg in receiver:
                print("Received: " + str(msg))
                receiver.complete_message(msg)

if __name__ == "__main__":
    main()