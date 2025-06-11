"""
Database connection and initialization for Travel Planner.
Handles PostgreSQL connection setup and schema management.
"""

import os
import psycopg2
from psycopg2 import pool, sql
from typing import Optional, Dict, Any
import logging
from config import get_config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global connection pool
connection_pool: Optional[psycopg2.pool.SimpleConnectionPool] = None


def create_connection_pool(database_url: str, min_conn: int = 1, max_conn: int = 20) -> psycopg2.pool.SimpleConnectionPool:
    """
    Create a PostgreSQL connection pool.
    
    Args:
        database_url: PostgreSQL connection string
        min_conn: Minimum number of connections in pool
        max_conn: Maximum number of connections in pool
        
    Returns:
        Connection pool instance
        
    Raises:
        psycopg2.Error: If connection fails
    """
    try:
        pool_instance = psycopg2.pool.SimpleConnectionPool(
            min_conn, max_conn, database_url
        )
        logger.info(f"Connection pool created with {min_conn}-{max_conn} connections")
        return pool_instance
    except psycopg2.Error as e:
        logger.error(f"Failed to create connection pool: {e}")
        raise


def get_connection():
    """
    Get a connection from the pool.
    
    Returns:
        Database connection
        
    Raises:
        RuntimeError: If connection pool not initialized
        psycopg2.Error: If no connections available
    """
    global connection_pool
    if connection_pool is None:
        raise RuntimeError("Connection pool not initialized. Call init_db() first.")
    
    try:
        conn = connection_pool.getconn()
        logger.debug("Connection retrieved from pool")
        return conn
    except psycopg2.Error as e:
        logger.error(f"Failed to get connection from pool: {e}")
        raise


def return_connection(conn):
    """
    Return a connection to the pool.
    
    Args:
        conn: Database connection to return
    """
    global connection_pool
    if connection_pool is not None and conn is not None:
        connection_pool.putconn(conn)
        logger.debug("Connection returned to pool")


def close_connection_pool():
    """Close all connections in the pool."""
    global connection_pool
    if connection_pool is not None:
        connection_pool.closeall()
        connection_pool = None
        logger.info("Connection pool closed")


def execute_query(query: str, params: tuple = None, fetch_one: bool = False, fetch_all: bool = False) -> Any:
    """
    Execute a database query with connection pooling.
    
    Args:
        query: SQL query string
        params: Query parameters (for parameterized queries)
        fetch_one: Return single row result
        fetch_all: Return all rows result
        
    Returns:
        Query result or None
        
    Raises:
        psycopg2.Error: If query execution fails
    """
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute(query, params)
            
            if fetch_one:
                result = cur.fetchone()
                conn.commit()  # Commit after INSERT/UPDATE...RETURNING
                return result
            elif fetch_all:
                return cur.fetchall()
            else:
                conn.commit()
                return cur.rowcount
                
    except psycopg2.Error as e:
        if conn:
            conn.rollback()
        logger.error(f"Query execution failed: {e}")
        raise
    finally:
        if conn:
            return_connection(conn)


# SQL Schema Definition
SCHEMA_SQL = """
-- Drop tables if they exist (for development)
DROP TABLE IF EXISTS activities CASCADE;
DROP TABLE IF EXISTS days CASCADE;
DROP TABLE IF EXISTS trips CASCADE;

-- Trips table
CREATE TABLE trips (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    start_date DATE,
    end_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Days table (represents individual days within a trip)
CREATE TABLE days (
    id SERIAL PRIMARY KEY,
    trip_id INTEGER REFERENCES trips(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    day_number INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Activities table
CREATE TABLE activities (
    id SERIAL PRIMARY KEY,
    day_id INTEGER REFERENCES days(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    start_time TIME,
    end_time TIME,
    order_index INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance optimization
CREATE INDEX idx_days_trip_id ON days(trip_id);
CREATE INDEX idx_days_date ON days(date);
CREATE INDEX idx_activities_day_id ON activities(day_id);
CREATE INDEX idx_activities_start_time ON activities(start_time);
CREATE INDEX idx_activities_order_index ON activities(order_index);

-- Unique constraints
CREATE UNIQUE INDEX idx_days_trip_day_number ON days(trip_id, day_number);
"""


def create_schema():
    """
    Create the database schema with all tables and indexes.
    
    Raises:
        psycopg2.Error: If schema creation fails
    """
    try:
        execute_query(SCHEMA_SQL)
        logger.info("Database schema created successfully")
    except psycopg2.Error as e:
        logger.error(f"Failed to create schema: {e}")
        raise


def drop_schema():
    """
    Drop all tables from the database.
    
    Raises:
        psycopg2.Error: If schema dropping fails
    """
    drop_sql = """
    DROP TABLE IF EXISTS activities CASCADE;
    DROP TABLE IF EXISTS days CASCADE;
    DROP TABLE IF EXISTS trips CASCADE;
    """
    try:
        execute_query(drop_sql)
        logger.info("Database schema dropped successfully")
    except psycopg2.Error as e:
        logger.error(f"Failed to drop schema: {e}")
        raise


def test_connection() -> bool:
    """
    Test database connection.
    
    Returns:
        True if connection successful, False otherwise
    """
    try:
        result = execute_query("SELECT 1 as test", fetch_one=True)
        if result and result[0] == 1:
            logger.info("Database connection test successful")
            return True
        else:
            logger.error("Database connection test failed")
            return False
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        return False


def init_db(env_name: str = None):
    """
    Initialize database connection pool and create schema.
    
    Args:
        env_name: Environment name (development, production, testing)
        
    Raises:
        psycopg2.Error: If initialization fails
    """
    global connection_pool
    
    # Get configuration
    config = get_config(env_name)
    database_url = config.DATABASE_URL
    
    # Create connection pool
    connection_pool = create_connection_pool(database_url)
    
    # Test connection
    if not test_connection():
        raise RuntimeError("Database connection test failed")
    
    # Create schema
    create_schema()
    
    logger.info("Database initialized successfully")


def reset_db(env_name: str = None):
    """
    Reset database by dropping and recreating schema.
    
    Args:
        env_name: Environment name (development, production, testing)
    """
    global connection_pool
    
    if connection_pool is None:
        init_db(env_name)
    
    drop_schema()
    create_schema()
    
    logger.info("Database reset successfully")


def get_db_stats() -> Dict[str, int]:
    """
    Get database statistics (table row counts).
    
    Returns:
        Dictionary with table names and row counts
    """
    try:
        trips_count = execute_query("SELECT COUNT(*) FROM trips", fetch_one=True)[0]
        days_count = execute_query("SELECT COUNT(*) FROM days", fetch_one=True)[0]
        activities_count = execute_query("SELECT COUNT(*) FROM activities", fetch_one=True)[0]
        
        return {
            'trips': trips_count,
            'days': days_count,
            'activities': activities_count
        }
    except psycopg2.Error as e:
        logger.error(f"Failed to get database stats: {e}")
        return {'trips': 0, 'days': 0, 'activities': 0}