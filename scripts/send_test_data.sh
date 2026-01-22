#!/bin/bash
# Send test JSON data to Kafka topic

if [ -z "$1" ]; then
    echo "Usage: $0 <json_file_path>"
    exit 1
fi

echo "📤 Sending test data to Kafka..."
python -m src.kafka.producer "$1"

echo "✅ Data sent to Kafka topic: zoomcar-raw-events"
