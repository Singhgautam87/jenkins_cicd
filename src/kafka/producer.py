"""
Kafka producer to send JSON events to Kafka topic.
Used for testing and simulating real-time data ingestion.
"""
import json
import time
from kafka import KafkaProducer
from kafka.errors import KafkaError

from ..config.kafka_config import KAFKA_BOOTSTRAP_SERVERS, KAFKA_TOPIC_RAW_EVENTS
from ..config.settings import KAFKA_PRODUCER_CONFIG


def create_producer() -> KafkaProducer:
    """
    Create Kafka producer instance.
    Uses configuration from settings module.
    """
    config = KAFKA_PRODUCER_CONFIG.copy()
    
    # Handle serializers - convert string configs to actual functions
    if config.get("value_serializer") == "json":
        config["value_serializer"] = lambda v: json.dumps(v).encode("utf-8")
    if config.get("key_serializer") == "string":
        config["key_serializer"] = lambda k: k.encode("utf-8") if k else None
    
    # Extract bootstrap_servers (it's already a list from settings)
    bootstrap_servers = config.pop("bootstrap_servers")
    
    return KafkaProducer(
        bootstrap_servers=bootstrap_servers,
        **config
    )


def send_event(producer: KafkaProducer, event: dict, key: str = None) -> None:
    """Send a single event to Kafka topic."""
    try:
        future = producer.send(KAFKA_TOPIC_RAW_EVENTS, value=event, key=key)
        future.get(timeout=10)
        print(f"✅ Sent event: {event.get('booking_id', event.get('customer_id', 'unknown'))}")
    except KafkaError as e:
        print(f"❌ Failed to send event: {e}")


def send_batch_from_file(file_path: str) -> None:
    """
    Read JSON file and send all events to Kafka.
    Handles both single JSON object and array of objects.
    """
    producer = create_producer()
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Handle both single object and array
            if isinstance(data, list):
                events = data
            else:
                events = [data]
            
            print(f"Sending {len(events)} events to Kafka...")
            for i, event in enumerate(events, 1):
                # Use booking_id or customer_id as key for partitioning
                key = event.get("booking_id") or event.get("customer_id")
                send_event(producer, event, key)
                
                # Small delay to avoid overwhelming Kafka (can remove for production)
                time.sleep(0.1)
                
                # Progress indicator for large files
                if i % 100 == 0:
                    print(f"Sent {i}/{len(events)} events...")
        
        # Make sure all messages are sent before closing
        producer.flush()
        print(f"✅ Successfully sent {len(events)} events to topic: {KAFKA_TOPIC_RAW_EVENTS}")
    except FileNotFoundError:
        print(f"❌ File not found: {file_path}")
        raise
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in file: {e}")
        raise
    finally:
        producer.close()


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        send_batch_from_file(sys.argv[1])
    else:
        print("Usage: python -m src.kafka.producer <json_file_path>")
