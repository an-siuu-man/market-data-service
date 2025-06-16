from confluent_kafka import Producer
import json
import os

# Load Kafka server from environment or default to local Docker setup
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")

conf = {
    'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS
}

producer = Producer(conf)

def delivery_report(err, msg):
    if err is not None:
        print(f"Delivery failed: {err}")
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition()}]")

def publish_price_event(data: dict, topic: str = "price-events") -> None:
    """
    Publish a JSON-encoded price event to Kafka.
    """
    producer.produce(topic, json.dumps(data).encode("utf-8"), callback=delivery_report)
    producer.flush()

# --- Ensure topic exists by sending a dummy message at import time ---
def _send_dummy_message():
    dummy = {"symbol": "DUMMY", "price": 0, "timestamp": "1970-01-01T00:00:00Z", "provider": "dummy"}
    try:
        producer.produce("price-events", json.dumps(dummy).encode("utf-8"), callback=delivery_report)
        producer.flush()
        print("Dummy message sent to 'price-events' to ensure topic exists.")
    except Exception as e:
        print(f"Failed to send dummy message: {e}")

_send_dummy_message()
