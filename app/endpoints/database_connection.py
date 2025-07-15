import os
import asyncio
from contextlib import asynccontextmanager
from psycopg_pool import AsyncConnectionPool
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://hopjetair:SecurePass123!@localhost:5432/hopjetair"
)

# Connection pool configuration
MIN_CONNECTIONS = int(os.getenv("DB_MIN_CONNECTIONS", "5"))
MAX_CONNECTIONS = int(os.getenv("DB_MAX_CONNECTIONS", "20"))

class DatabaseManager:
    def __init__(self):
        self.pool = None
        self.engine = None
        self.async_session_factory = None
        
    async def initialize(self):
        """Initialize database connections and pool"""
        try:
            # Create async engine
            self.engine = create_async_engine(
                DATABASE_URL,
                echo=False,
                pool_size=10,
                max_overflow=20,
                pool_timeout=30,
                pool_recycle=3600
            )
            
            # Create session factory
            self.async_session_factory = async_sessionmaker(
                self.engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            
            # Initialize connection pool for raw queries
            self.pool = AsyncConnectionPool(
                conninfo=DATABASE_URL,
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