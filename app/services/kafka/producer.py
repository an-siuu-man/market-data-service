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
