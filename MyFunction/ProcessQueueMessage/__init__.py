import azure.functions as func
import json
import logging

def main(msg: func.ServiceBusMessage):
    queue_name = msg.trigger_metadata.get("EntityName", "unknown")
    logging.info(f"Processing message from: {queue_name}")
    logging.info(f"Message ID: {msg.message_id}")

    try:
        # Decode and parse the message
        message_body = msg.get_body().decode('utf-8')
        message_data = json.loads(message_body)
        logging.info(f"Message Body: {message_data}")

        if queue_name.endswith("$DeadLetterQueue"):
            # Logic for Dead-Letter Queue
            logging.warning(f"Processing Dead-Letter Queue message: {msg.message_id}")
            handle_dead_letter_message(message_data)
        else:
            # Logic for Primary Queue
            logging.info(f"Processing primary queue message: {msg.message_id}")
            handle_primary_queue_message(message_data)

        logging.info(f"Successfully processed message ID: {msg.message_id}")

    except Exception as e:
        logging.error(f"Error processing message ID {msg.message_id}: {e}")
        # If an exception occurs, let Service Bus retry or move to DLQ
        raise


def handle_primary_queue_message(message_data):
    """Logic for processing messages from the primary queue."""
    logging.info("Processing primary queue message...")
    if "failover" in message_data:
        # Simulate failure to trigger DLQ behavior
        raise Exception("Simulated failure for testing DLQ handling.")
    logging.info("Primary message processed successfully.")


def handle_dead_letter_message(message_data):
    """Logic for processing messages from the Dead-Letter Queue."""
    logging.warning("Processing DLQ message...")
    # Example: Log to external system, alert, or attempt reprocessing
    logging.info(f"Reprocessing failed message: {message_data}")
    # Add custom failover handling logic here
