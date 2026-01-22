"""
PostgreSQL database configuration and connection management.
Handles schema initialization and database connections.
"""
from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool

from .settings import (
    POSTGRES_HOST,
    POSTGRES_PORT,
    POSTGRES_DB,
    POSTGRES_USER,
    POSTGRES_PASSWORD,
)


def get_postgres_url() -> str:
    """Build PostgreSQL connection URL from settings."""
    return f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"


def get_engine():
    """
    Create SQLAlchemy engine for PostgreSQL.
    Using NullPool to avoid connection pool issues in Spark context.
    """
    url = get_postgres_url()
    return create_engine(url, poolclass=NullPool, echo=False)


def create_database_if_not_exists():
    """
    Create database if it doesn't exist.
    PostgreSQL container usually creates it automatically via POSTGRES_DB env var,
    but this function ensures it exists and handles edge cases.
    """
    from sqlalchemy import create_engine, text
    
    # Try to connect to our database first
    try:
        test_engine = get_engine()
        with test_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        test_engine.dispose()
        print(f"✅ Database {POSTGRES_DB} exists and is accessible")
        return
    except Exception:
        # Database doesn't exist or not accessible, try to create it
        pass
    
    # Connect to postgres database (default) to create our database
    admin_url = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/postgres"
    admin_engine = create_engine(admin_url, isolation_level="AUTOCOMMIT", poolclass=NullPool)
    
    try:
        with admin_engine.connect() as conn:
            # Check if database exists
            result = conn.execute(text(
                f"SELECT 1 FROM pg_database WHERE datname = '{POSTGRES_DB}'"
            ))
            exists = result.fetchone() is not None
            
            if not exists:
                print(f"📦 Creating database: {POSTGRES_DB}")
                conn.execute(text(f'CREATE DATABASE {POSTGRES_DB}'))
                print(f"✅ Database {POSTGRES_DB} created successfully")
            else:
                print(f"✅ Database {POSTGRES_DB} already exists")
    except Exception as e:
        # Database might already exist or we don't have permission
        # This is usually fine - PostgreSQL container creates it automatically
        print(f"⚠️ Note: {e}")
        print(f"   (Database is likely created automatically by PostgreSQL container)")
    finally:
        admin_engine.dispose()


def init_schema():
    """
    Initialize database schema (tables for bookings and customers).
    Creates tables if they don't exist, adds indexes for performance.
    
    This function:
    1. Ensures database exists
    2. Creates bookings and customers tables
    3. Creates indexes for performance
    """
    print("🔧 Initializing database schema...")
    
    # First ensure database exists
    create_database_if_not_exists()
    
    engine = get_engine()
    
    try:
        with engine.connect() as conn:
            print("📊 Creating tables...")
            # Bookings table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS bookings (
                    booking_id VARCHAR(50) PRIMARY KEY,
                    customer_id VARCHAR(50) NOT NULL,
                    booking_date DATE NOT NULL,
                    booking_status VARCHAR(20) NOT NULL,
                    start_time TIMESTAMP,
                    end_time TIMESTAMP,
                    booking_duration_minutes DECIMAL(10, 2),
                    car_type VARCHAR(50),
                    pickup_city VARCHAR(100),
                    booking_date_parsed DATE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            # Customers table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS customers (
                    customer_id VARCHAR(50) PRIMARY KEY,
                    customer_name VARCHAR(200) NOT NULL,
                    email VARCHAR(200) NOT NULL,
                    phone VARCHAR(20),
                    phone_norm VARCHAR(20),
                    customer_status VARCHAR(50),
                    customer_status_std VARCHAR(50),
                    signup_date DATE,
                    signup_date_parsed DATE,
                    customer_tenure_days INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            # Indexes for better query performance
            # These help with joins and filtering
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_bookings_customer_id ON bookings(customer_id)
            """))
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_bookings_status ON bookings(booking_status)
            """))
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_customers_email ON customers(email)
            """))
            
            conn.commit()
        
        print("✅ Database schema initialized successfully")
        print(f"   - Tables: bookings, customers")
        print(f"   - Indexes: 3 indexes created")
    except Exception as e:
        print(f"❌ Error initializing schema: {e}")
        raise
    finally:
        engine.dispose()


if __name__ == "__main__":
    # Can run this directly to initialize schema
    init_schema()
