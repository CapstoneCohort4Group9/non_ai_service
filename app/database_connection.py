import os
import asyncio
from contextlib import asynccontextmanager
from psycopg_pool import AsyncConnectionPool
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
import logging
import boto3
import json
from botocore.exceptions import ClientError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Connection pool configuration
MIN_CONNECTIONS = int(os.getenv("DB_MIN_CONNECTIONS", "5"))
MAX_CONNECTIONS = int(os.getenv("DB_MAX_CONNECTIONS", "20"))

# --- AWS Secrets Manager and Connection String Functions ---

def get_db_credentials():
    """Fetch database credentials (user and password) from AWS Secrets Manager"""
    secret_name = os.getenv("DB_SECRET_NAME")
    region_name = os.getenv("AWS_REGION")

    if not secret_name or not region_name:
        logger.warning("DB_SECRET_NAME or AWS_REGION not set. Cannot fetch credentials from Secrets Manager.")
        return None

    try:
        client = boto3.session.Session().client(
            service_name='secretsmanager',
            region_name=region_name
        )
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
        secret = json.loads(get_secret_value_response['SecretString'])
        logger.info(f"Successfully fetched credentials from AWS Secrets Manager for secret: {secret_name}")
        return secret
    except ClientError as e:
        logger.error(f"Error fetching secret '{secret_name}' from Secrets Manager: {e}")
    except Exception as e:
        logger.error(f"Unexpected error occurred while fetching secret: {e}")
    
    return None

def get_connection_string():
    """
    Build database connection string dynamically.
    user and pass from AWS Secrets Manager (or fallback to env).
    Host, port, database name always from environment variables.
    Returns SQLAlchemy compatible URL (e.g., postgresql+asyncpg://).
    """
    db_user = None
    db_pass = None
    
    # Attempt to get user and pass from AWS Secrets Manager
    try:
        credentials = get_db_credentials()
        if credentials:
            db_pass = credentials.get('db_pass') # Common key in Secrets Manager
            db_user = credentials.get('db_user') # Common key in Secrets Manager
            
            if not all([db_user, db_pass]):
                logger.warning("Incomplete user/pass from Secrets Manager. Falling back to environment variables.")
                db_user, db_pass = None, None # Reset to trigger fallback
        else:
            logger.warning("No credentials returned from AWS Secrets Manager. Falling back to environment variables for user/pass.")
            
    except Exception as e:
        logger.error(f"Error during Secrets Manager credential retrieval for user/pass: {e}. Falling back to environment variables.")
        db_user, db_pass = None, None

    # Fallback to environment variables for user/pass if Secrets Manager failed or was incomplete
    if not all([db_user, db_pass]):
        db_user = os.getenv("DB_USER")
        db_pass = os.getenv("DB_PASS")
        logger.info("Using environment variables for database user and pass.")
    else:
        logger.info("Using AWS Secrets Manager credentials for database user and pass.")

    # Always get host, port, and database name from environment variables
    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT", "5432")
    database = os.getenv("DB_NAME")
    
    # Validate required variables
    if not all([host, database, db_user, db_pass]):
        error_msg = "Missing required database configuration (host, database, user, or pass). Please set environment variables or AWS Secrets Manager."
        logger.critical(error_msg)
        raise ValueError(error_msg)
    
    # Build connection string for SQLAlchemy (with +asyncpg)
    connection_string = f"postgresql+asyncpg://{db_user}:{db_pass}@{host}:{port}/{database}"
    return connection_string

# Initialize DATABASE_URL using the function
DATABASE_URL = get_connection_string()

# --- End AWS Secrets Manager and Connection String Functions ---


class DatabaseManager:
    def __init__(self):
        self.pool = None
        self.engine = None
        self.async_session_factory = None
        
    async def initialize(self):
        """Initialize database connections and pool"""
        try:
            # Create async engine for SQLAlchemy
            self.engine = create_async_engine(
                DATABASE_URL,
                echo=False,
                pool_size=MIN_CONNECTIONS,
                max_overflow=MAX_CONNECTIONS - MIN_CONNECTIONS,
                pool_timeout=30,
                pool_recycle=3600
            )
            
            # Create session factory
            self.async_session_factory = async_sessionmaker(
                self.engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            
            # Initialize connection pool for raw queries (psycopg_pool)
            # Remove '+asyncpg' from the URL for psycopg_pool
            raw_conn_info = DATABASE_URL.replace("+asyncpg", "")
            self.pool = AsyncConnectionPool(
                conninfo=raw_conn_info,
                min_size=MIN_CONNECTIONS,
                max_size=MAX_CONNECTIONS,
                timeout=30
            )
            
            await self.pool.open()
            logger.info("Database connections initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    async def close(self):
        """Close all database connections"""
        try:
            if self.pool:
                await self.pool.close()
            if self.engine:
                await self.engine.dispose()
            logger.info("Database connections closed")
        except Exception as e:
            logger.error(f"Error closing database connections: {e}")
    
    @asynccontextmanager
    async def get_session(self):
        """Get async SQLAlchemy session"""
        if not self.async_session_factory:
            raise RuntimeError("Database not initialized")
        
        async with self.async_session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception as e:
                await session.rollback()
                logger.error(f"Database session error: {e}")
                raise
            finally:
                await session.close()
    
    @asynccontextmanager
    async def get_connection(self):
        """Get raw database connection from pool"""
        if not self.pool:
            raise RuntimeError("Database pool not initialized")
        
        async with self.pool.connection() as conn:
            try:
                yield conn
            except Exception as e:
                logger.error(f"Database connection error: {e}")
                raise

# Global database manager instance
db_manager = DatabaseManager()

# Dependency for FastAPI
async def get_db_session():
    async with db_manager.get_session() as session:
        yield session

async def get_db_connection():
    async with db_manager.get_connection() as conn:
        yield conn

# Database initialization for app startup
async def init_database():
    await db_manager.initialize()

async def close_database():
    await db_manager.close()

# Health check function
async def check_database_health():
    """Check if database is healthy"""
    try:
        async with db_manager.get_connection() as conn:
            result = await conn.execute("SELECT 1")
            return await result.fetchone() is not None
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False

# Utility functions for database operations
async def execute_query(query: str, params: dict = None):
    """Execute a raw SQL query"""
    async with db_manager.get_connection() as conn:
        if params:
            result = await conn.execute(query, params)
        else:
            result = await conn.execute(query)
        return await result.fetchall()

async def execute_single_query(query: str, params: dict = None):
    """Execute a query and return single result"""
    async with db_manager.get_connection() as conn:
        if params:
            result = await conn.execute(query, params)
        else:
            result = await conn.execute(query)
        return await result.fetchone()

class DatabaseError(Exception):
    """Custom database exception"""
    pass

class BookingNotFoundError(DatabaseError):
    """Booking not found exception"""
    pass

class FlightNotFoundError(DatabaseError):
    """Flight not found exception"""
    pass

class PassengerNotFoundError(DatabaseError):
    """Passenger not found exception"""
    pass

# Connection retry decorator
def retry_db_operation(max_retries: int = 3, delay: float = 1.0):
    """Decorator to retry database operations"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        logger.error(f"Database operation failed after {max_retries} attempts: {e}")
                        raise
                    logger.warning(f"Database operation attempt {attempt + 1} failed: {e}, retrying...")
                    await asyncio.sleep(delay)
            return None
        return wrapper
    return decorator