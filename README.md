# Zoom Car Real-time Data Pipeline

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![Spark](https://img.shields.io/badge/Spark-3.3-orange.svg)](https://spark.apache.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue.svg)](https://www.postgresql.org/)
[![Kafka](https://img.shields.io/badge/Kafka-7.5.0-black.svg)](https://kafka.apache.org/)

Industry-standard real-time data processing pipeline with Kafka, Spark, and PostgreSQL.

## 🏗️ Architecture

```
JSON Events → Kafka → Spark (PySpark) → PostgreSQL → Dashboard
```

### Component Details

- **Kafka**: Real-time event streaming (topic: `zoomcar-raw-events`)
- **Spark**: Distributed data processing and transformation
- **PostgreSQL**: ACID-compliant database for final storage
- **Jenkins**: Full CI/CD automation
- **Docker Compose**: Infrastructure orchestration

## ✨ Features

- ✅ **Real-time Streaming**: Kafka-based event ingestion
- ✅ **Distributed Processing**: Apache Spark for scalable ETL
- ✅ **ACID Database**: PostgreSQL for reliable data storage
- ✅ **Data Quality**: Deequ-based validation and checks
- ✅ **CI/CD**: Fully automated Jenkins pipeline
- ✅ **Configuration-Driven**: All dynamic values in config files
- ✅ **Industry Standards**: Logging, error handling, testing

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.11+
- Jenkins (for CI/CD)

### 1. Clone Repository

```bash
git clone <repo-url>
cd my_jenkins_pipeline
```

### 2. Setup Environment

```bash
cp .env.example .env
# Edit .env with your configuration
```

### 3. Start Infrastructure

```bash
make docker-up
# Or manually:
docker-compose up -d
```

This starts:
- **Zookeeper** (port 2181)
- **Kafka** (port 9092)
- **PostgreSQL** (port 5432) - Database `zoomcar_db` is created automatically
- **PgAdmin** (port 5050) - Database UI

### 4. Initialize Database Schema

The database `zoomcar_db` is created automatically by PostgreSQL container. You just need to create tables:

```bash
python -m src.config.database
```

This creates:
- `bookings` table
- `customers` table
- Indexes for performance

### 5. Send Test Data to Kafka

```bash
python -m src.kafka.producer data/raw/zoom_car_events_20260101.json
```

### 6. Run Real-time ETL

```bash
python -m src.realtime_pipeline --run-date 2026-01-01
```

## 📋 Jenkins Pipeline

### Real-time Mode (Kafka + PostgreSQL)

1. **Jenkins Job** → **Build with Parameters**:
   - `PIPELINE_MODE`: `realtime`
   - `RUN_DATE`: `2026-01-01` (optional)

2. **Pipeline Stages**:
   - ✅ Checkout code
   - ✅ Build Docker image
   - ✅ Start Kafka + PostgreSQL
   - ✅ **Initialize database schema** (creates tables automatically)
   - ✅ Send test data to Kafka
   - ✅ Run real-time ETL (Kafka → Spark → PostgreSQL)
   - ✅ Generate dashboard
   - ✅ Archive results
   - ✅ Clean workspace

### Batch Mode (File-based)

1. **Jenkins Job** → **Build with Parameters**:
   - `PIPELINE_MODE`: `batch`
   - `RUN_DATE`: `2026-01-01`

2. Uses file-based processing (Parquet workflow)

## 🗄️ Database Setup

### Automatic Database Creation

PostgreSQL container automatically creates the database `zoomcar_db` when it starts (via `POSTGRES_DB` environment variable in docker-compose.yml).

### Schema Initialization

Run this to create tables and indexes:

```bash
python -m src.config.database
```

Or it's done automatically in:
- Jenkins pipeline (real-time mode)
- Real-time ETL pipeline (before processing)

### Database Schema

**Bookings Table:**
- Primary Key: `booking_id`
- Foreign Key: `customer_id`
- Indexes: `customer_id`, `booking_status`

**Customers Table:**
- Primary Key: `customer_id`
- Unique: `email`
- Indexes: `email`

### Access Database

**Via PgAdmin (Web UI):**
- URL: http://localhost:5050
- Email: admin@zoomcar.com
- Password: admin

**Via psql:**
```bash
docker-compose exec postgres psql -U zoomcar_user -d zoomcar_db
```

## 📁 Project Structure

```
.
├── src/
│   ├── config/          # All configuration (dynamic values)
│   ├── core/            # Core utilities (logging, exceptions)
│   ├── models/          # Data models (bookings, customers)
│   ├── kafka/           # Kafka integration
│   ├── ingestion/       # Real-time ETL
│   └── utils/           # Utility functions
├── tests/               # Unit tests
├── scripts/             # Helper scripts
├── docker-compose.yml   # Infrastructure
└── Jenkinsfile          # CI/CD pipeline
```

See [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) for detailed structure.

## 🧪 Testing

```bash
# Install dev dependencies
make install

# Run tests
make test

# Check code quality
make lint
```

## 🔧 Configuration

All configuration is centralized in `src/config/`:

- **`settings.py`**: Environment variables & app settings
- **`business_rules.py`**: Business logic constants
- **`validation_rules.py`**: Data validation rules
- **`spark_config.py`**: Spark-specific settings
- **`dq_config.py`**: Data quality configurations

See [CONFIG_GUIDE.md](CONFIG_GUIDE.md) for detailed configuration guide.

### Environment Variables

Create `.env` file:

```bash
# Kafka
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_TOPIC_RAW_EVENTS=zoomcar-raw-events

# PostgreSQL
POSTGRES_HOST=postgres
POSTGRES_DB=zoomcar_db
POSTGRES_USER=zoomcar_user
POSTGRES_PASSWORD=zoomcar_pass

# Spark
SPARK_VERSION=3.3
SPARK_MASTER=local[*]
```

## 📊 Data Flow

1. **Producer** sends JSON events to Kafka topic `zoomcar-raw-events`
2. **Consumer** (Spark) reads from Kafka in batches
3. **Processing**:
   - Validation & cleaning
   - Transformations (duration, phone normalization, tenure)
   - Deduplication
4. **Storage**: Upsert to PostgreSQL (ON CONFLICT DO UPDATE)
5. **Dashboard**: Generated from PostgreSQL data

## 🛠️ Development

```bash
# Format code
make format

# Run linter
make lint

# Run tests
make test

# Clean temporary files
make clean
```

## 📚 Documentation

- [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) - Detailed project structure
- [CONFIG_GUIDE.md](CONFIG_GUIDE.md) - Configuration guide
- [CONTRIBUTING.md](CONTRIBUTING.md) - Contribution guidelines
- [CHANGELOG.md](CHANGELOG.md) - Version history

## 🎯 Industry Standards

This project follows industry best practices:

- ✅ **Modular Architecture**: Clear separation of concerns
- ✅ **Configuration-Driven**: All dynamic values in config
- ✅ **Centralized Logging**: Structured logging system
- ✅ **Error Handling**: Custom exceptions & retry mechanisms
- ✅ **Type Hints**: Full type annotations
- ✅ **Unit Tests**: Comprehensive test coverage
- ✅ **Documentation**: Complete API docs
- ✅ **CI/CD**: Automated pipeline
- ✅ **Docker**: Containerized deployment

## 📝 License

MIT License - see [LICENSE](LICENSE) file

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

**Built with industry best practices** 🚀
