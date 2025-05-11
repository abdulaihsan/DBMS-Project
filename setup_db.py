from connect import DatabaseConnection
import logging

def setup_database():
    try:
        # Initialize database connection and create tables
        db = DatabaseConnection()
        print("Database connection successful!")
        print("Tables created successfully!")
        
        # Test the connection with a simple query
        result = db.execute_query("SELECT version();")
        print(f"PostgreSQL version: {result[0][0]}")
        
        # Close all connections
        db.close_all()
        print("Database setup completed!")
        
    except Exception as e:
        print(f"Error setting up database: {e}")
        logging.error(f"Database setup error: {e}")

if __name__ == "__main__":
    setup_database() 