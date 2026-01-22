#!/bin/bash
# Initialize Kafka, PostgreSQL and create topics

echo "🚀 Starting infrastructure services..."

# Start Docker services
docker-compose up -d

echo "⏳ Waiting for services to be ready..."
sleep 15

# Create Kafka topic
docker-compose exec -T kafka kafka-topics --create \
  --bootstrap-server localhost:9092 \
  --topic zoomcar-raw-events \
  --partitions 3 \
  --replication-factor 1 \
  --if-not-exists || echo "Topic already exists"

# Initialize PostgreSQL schema
echo "📊 Initializing database schema..."
python -m src.config.database

echo "✅ Infrastructure ready!"
