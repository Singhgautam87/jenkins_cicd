# Configuration Guide

## 📋 Overview

All dynamic and configurable values are centralized in `src/config/` directory. This makes the codebase maintainable and allows easy changes without modifying business logic.

## 🗂️ Config Files Structure

```
src/config/
├── settings.py          # Environment variables & app settings
├── business_rules.py    # Business logic constants
├── validation_rules.py  # Data validation rules
├── spark_config.py      # Spark-specific settings
├── dq_config.py         # Data quality check configurations
├── kafka_config.py     # Kafka settings (imports from settings)
├── database.py         # Database schema & connection
└── paths.py            # File/directory paths
```

## 🔧 Configuration Files

### 1. `settings.py`
**Purpose**: Environment variables and application-level settings

**Key Settings**:
- Environment (dev/prod)
- Logging configuration
- Connection pool sizes
- Retry policies
- Kafka producer/consumer configs
- PostgreSQL connection pool settings

**Usage**:
```python
from src.config.settings import SPARK_VERSION, KAFKA_BOOTSTRAP_SERVERS
```

### 2. `business_rules.py`
**Purpose**: Business logic constants that might change based on requirements

**Contains**:
- Valid booking statuses
- Customer status mappings
- Data quality thresholds
- Date formats
- Phone normalization rules
- Data retention policies
- Batch sizes
- Deduplication rules

**Usage**:
```python
from src.config.business_rules import VALID_BOOKING_STATUSES, BATCH_SIZES
```

### 3. `validation_rules.py`
**Purpose**: Data validation rules and schemas

**Contains**:
- Email regex patterns
- Required fields per entity
- Not-null field constraints
- Field length limits
- Validation patterns
- Business validation rules

**Usage**:
```python
from src.config.validation_rules import EMAIL_REGEX, REQUIRED_FIELDS
```

### 4. `spark_config.py`
**Purpose**: Spark-specific configuration

**Contains**:
- Spark version
- Master URL
- Memory settings
- Serialization config
- Adaptive execution settings
- Deequ package configuration

**Usage**:
```python
from src.config.spark_config import get_spark_config
```

### 5. `dq_config.py`
**Purpose**: Data quality check configurations

**Contains**:
- DQ check levels (error/warning)
- Bookings DQ checks
- Customers DQ checks
- DQ reporting configuration

**Usage**:
```python
from src.config.dq_config import BOOKINGS_DQ_CHECKS, DQ_REPORTING
```

### 6. `paths.py`
**Purpose**: File and directory paths

**Contains**:
- Raw data directory
- Staging directory
- Final data directory
- File naming patterns

**Usage**:
```python
from src.config import paths as config
raw_path = config.get_raw_file_path(run_date)
```

## 🎯 Best Practices

1. **Never hardcode values** - Always use config
2. **Group related configs** - Business rules together, validation together
3. **Use environment variables** - For sensitive or environment-specific values
4. **Document configs** - Add comments explaining why values are set
5. **Version control configs** - Keep configs in git (except secrets)

## 🔐 Environment Variables

Create `.env` file for environment-specific values:

```bash
# Environment
ENVIRONMENT=development
DEBUG=false
LOG_LEVEL=INFO

# Spark
SPARK_VERSION=3.3
SPARK_MASTER=local[*]

# Kafka
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_TOPIC_RAW_EVENTS=zoomcar-raw-events

# PostgreSQL
POSTGRES_HOST=postgres
POSTGRES_DB=zoomcar_db
POSTGRES_USER=zoomcar_user
POSTGRES_PASSWORD=zoomcar_pass
```

## 📝 Adding New Configuration

1. **Determine category**: Business rule, validation, or setting?
2. **Choose file**: Add to appropriate config file
3. **Add to settings.py**: If it needs environment variable
4. **Update imports**: If needed in other modules
5. **Document**: Add comment explaining the config

## 🔄 Changing Configuration

To change any configuration:

1. **Business rules**: Edit `business_rules.py`
2. **Validation**: Edit `validation_rules.py`
3. **Environment**: Edit `.env` file or `settings.py`
4. **Spark**: Edit `spark_config.py`
5. **DQ checks**: Edit `dq_config.py`

No need to modify business logic code!

---

**This configuration structure makes the codebase maintainable and allows easy tuning without code changes.**
