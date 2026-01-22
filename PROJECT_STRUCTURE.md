# Project Structure & Architecture

## 📁 Enterprise-Grade Data Engineering Project Structure

This project follows industry best practices for data engineering pipelines, structured by an experienced data engineer.

## 🏗️ System Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐     ┌──────────────┐
│   JSON      │────▶│    Kafka     │────▶│   Spark     │────▶│  PostgreSQL  │
│   Events    │     │   (Stream)   │     │  (Process)  │     │  (Store)     │
└─────────────┘     └──────────────┘     └─────────────┘     └──────────────┘
                                                                    │
                                                                    ▼
                                                           ┌──────────────┐
                                                           │  Dashboard   │
                                                           │  (Report)    │
                                                           └──────────────┘
```

### Component Details

1. **Data Ingestion Layer**
   - Kafka Producer: Sends JSON events to Kafka topic
   - Kafka Topic: `zoomcar-raw-events` (3 partitions)
   - Consumer Group: `zoomcar-etl-group`

2. **Processing Layer**
   - Spark: Distributed data processing
   - Validation: Data quality checks
   - Transformation: Business logic
   - Deduplication: Upsert logic

3. **Storage Layer**
   - PostgreSQL: ACID-compliant database
   - Tables: `bookings`, `customers`
   - Indexes: Optimized for queries

4. **Orchestration Layer**
   - Jenkins: CI/CD automation
   - Docker Compose: Infrastructure management
   - Health Checks: Service monitoring

```
.
├── src/
│   ├── config/              # ⚙️ ALL CONFIGURATION (Dynamic values here)
│   │   ├── settings.py      # Environment variables & app settings
│   │   ├── business_rules.py    # Business logic constants
│   │   ├── validation_rules.py   # Data validation rules
│   │   ├── spark_config.py       # Spark-specific config
│   │   ├── dq_config.py          # Data quality check configs
│   │   ├── kafka_config.py       # Kafka settings
│   │   ├── database.py           # DB schema & connection
│   │   └── paths.py              # File/directory paths
│   │
│   ├── core/                # 🔧 Core utilities
│   │   ├── logger.py        # Centralized logging
│   │   ├── exceptions.py     # Custom exceptions
│   │   └── health_check.py  # Service health checks
│   │
│   ├── models/              # 📊 Data models (Domain layer)
│   │   ├── bookings.py      # Booking validation & transform
│   │   └── customers.py     # Customer validation & transform
│   │
│   ├── kafka/               # 📨 Kafka integration
│   │   ├── producer.py      # Send events to Kafka
│   │   └── consumer.py      # Read from Kafka
│   │
│   ├── ingestion/           # 🔄 Real-time ETL
│   │   └── kafka_ingestion.py  # Kafka → Spark → PostgreSQL
│   │
│   ├── utils/               # 🛠️ Utility functions
│   │   ├── spark_utils.py    # Spark session management
│   │   ├── validators.py     # Data validation
│   │   ├── date_utils.py     # Date parsing
│   │   └── retry.py         # Retry mechanism
│   │
│   ├── process_data.py      # 📥 Batch processing (file-based)
│   ├── transform_merge.py   # 🔀 Transformations & merge logic
│   ├── data_quality_dashboard.py  # 📊 DQ checks & dashboard
│   ├── main_pipeline.py     # 🚀 Batch pipeline entry point
│   ├── realtime_pipeline.py # ⚡ Real-time pipeline entry point
│   └── utils.py            # Legacy utils (backward compat)
│
├── tests/                   # 🧪 Unit tests
│   └── test_validators.py
│
├── scripts/                 # 📜 Helper scripts
│   ├── init_services.sh
│   └── send_test_data.sh
│
├── data/                    # 📁 Data directories
│   └── raw/                 # Input JSON files
│
├── docker-compose.yml       # 🐳 Infrastructure orchestration
├── Dockerfile               # 🐳 Application container
├── Jenkinsfile              # 🔄 CI/CD pipeline
├── requirements.txt         # 📦 Python dependencies
├── Makefile                 # 🔨 Common tasks
│
└── docs/                    # 📚 Documentation
    ├── README.md
    ├── README_REALTIME.md
    ├── CONFIG_GUIDE.md
    └── ARCHITECTURE.md
```

## 🎯 Key Design Principles

### 1. **Configuration-Driven**
- ✅ All dynamic values in `src/config/`
- ✅ Business rules separate from code
- ✅ Easy to change without modifying logic

### 2. **Separation of Concerns**
- ✅ **Config**: All configuration
- ✅ **Models**: Domain logic
- ✅ **Utils**: Reusable utilities
- ✅ **Core**: Cross-cutting concerns

### 3. **Modular Architecture**
- ✅ Each module has single responsibility
- ✅ Clear dependencies
- ✅ Easy to test and maintain

### 4. **Industry Standards**
- ✅ Type hints throughout
- ✅ Proper error handling
- ✅ Logging and monitoring
- ✅ Unit tests

## 📦 Module Responsibilities

### `config/` - Configuration Layer
**Purpose**: Centralize all configurable values

- `settings.py`: Environment variables, app settings
- `business_rules.py`: Business logic constants
- `validation_rules.py`: Data validation rules
- `spark_config.py`: Spark-specific settings
- `dq_config.py`: Data quality configurations

### `models/` - Domain Layer
**Purpose**: Business logic for data entities

- `bookings.py`: Booking validation, transformation
- `customers.py`: Customer validation, transformation

### `core/` - Infrastructure Layer
**Purpose**: Cross-cutting concerns

- `logger.py`: Logging setup
- `exceptions.py`: Custom exceptions
- `health_check.py`: Service health monitoring

### `utils/` - Utility Layer
**Purpose**: Reusable helper functions

- `spark_utils.py`: Spark session management
- `validators.py`: Data validation utilities
- `date_utils.py`: Date parsing utilities
- `retry.py`: Retry mechanism

### `kafka/` - Integration Layer
**Purpose**: Kafka integration

- `producer.py`: Send events to Kafka
- `consumer.py`: Read from Kafka

### `ingestion/` - Processing Layer
**Purpose**: ETL logic

- `kafka_ingestion.py`: Real-time ETL pipeline

## 🔄 Data Flow

```
Raw Data → Kafka → Spark → Validation → Transformation → PostgreSQL → Dashboard
```

## 📝 Configuration Philosophy

**All dynamic values go in config files:**

- ✅ Business rules → `business_rules.py`
- ✅ Validation rules → `validation_rules.py`
- ✅ Spark settings → `spark_config.py`
- ✅ Environment vars → `settings.py`
- ✅ DQ checks → `dq_config.py`

**Never hardcode:**
- ❌ Magic numbers
- ❌ Status values
- ❌ Thresholds
- ❌ Batch sizes
- ❌ Connection strings

## 🚀 Benefits of This Structure

1. **Maintainable**: Easy to find and change configs
2. **Testable**: Can mock configs for testing
3. **Scalable**: Easy to add new features
4. **Professional**: Follows industry best practices
5. **Flexible**: Change behavior without code changes

---

**This structure reflects the work of an experienced data engineer who understands maintainability and best practices.**
