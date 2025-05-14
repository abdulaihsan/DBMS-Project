import psycopg2
from psycopg2 import pool
from config import DB_CONFIG, CREATE_TABLES
import logging

class DatabaseConnection:
    _instance = None
    _connection_pool = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
            cls._instance._initialize_pool()
        return cls._instance

    def _initialize_pool(self):
        try:
            self._connection_pool = pool.SimpleConnectionPool(
                1,  # minconn
                10,  # maxconn
                host=DB_CONFIG['host'],
                database=DB_CONFIG['database'],
                user=DB_CONFIG['user'],
                password=DB_CONFIG['password'],
                port=DB_CONFIG['port']
            )
            self._create_tables()
        except Exception as e:
            logging.error(f"Error initializing connection pool: {e}")
            raise

    def _create_tables(self):
        """Create all necessary tables if they don't exist"""
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                for table_name, create_query in CREATE_TABLES.items():
                    cur.execute(create_query)
            conn.commit()
        except Exception as e:
            logging.error(f"Error creating tables: {e}")
            raise
        finally:
            self.return_connection(conn)

    def get_connection(self):
        """Get a connection from the pool"""
        return self._connection_pool.getconn()

    def return_connection(self, conn):
        """Return a connection to the pool"""
        self._connection_pool.putconn(conn)

    def execute_query(self, query, params=None):
        """Execute a query and return results"""
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(query, params or ())
                if cur.description:  # If the query returns data
                    return cur.fetchall()
                conn.commit()
                return None
        except Exception as e:
            conn.rollback()
            logging.error(f"Error executing query: {e}")
            raise
        finally:
            self.return_connection(conn)

    def execute_many(self, query, params_list):
        """Execute a query multiple times with different parameters"""
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                cur.executemany(query, params_list)
            conn.commit()
        except Exception as e:
            conn.rollback()
            logging.error(f"Error executing multiple queries: {e}")
            raise
        finally:
            self.return_connection(conn)

    def close_all(self):
        """Close all connections in the pool"""
        if self._connection_pool:
            self._connection_pool.closeall()
            self._connection_pool = None

def connect(config):
    """ Connect to the PostgreSQL database server """
    try:
        # connecting to the PostgreSQL server
        with psycopg2.connect(**config) as conn:
            print('Connected to the PostgreSQL server.')
            return conn
    except (psycopg2.DatabaseError, Exception) as error:
        print(error)

if __name__ == '__main__':
    config = load_config()
    connect(config)