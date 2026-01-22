#!/bin/bash
# Initialize PostgreSQL database and schema

echo "💾 Initializing PostgreSQL database..."

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL to be ready..."
until docker-compose exec -T postgres pg_isready -U zoomcar_user > /dev/null 2>&1; do
    echo "Waiting for PostgreSQL..."
    sleep 2
done

echo "✅ PostgreSQL is ready"

# Initialize schema
echo "📊 Creating database schema..."
python -m src.config.database

echo "✅ Database initialization complete!"
