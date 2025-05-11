import sys
from PyQt5.QtWidgets import QApplication
from sortingviz import MainWindow
import logging
from connect import DatabaseConnection

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('sorting_viz.log'),
            logging.StreamHandler()
        ]
    )

def initialize_database():
    try:
        db = DatabaseConnection()
        # Test the connection
        db.execute_query("SELECT version();")
        logging.info("Database connection successful")
        return True
    except Exception as e:
        logging.error(f"Database initialization failed: {e}")
        return False

def main():
    # Setup logging
    setup_logging()
    
    try:
        # Initialize database
        if not initialize_database():
            print("Error: Could not connect to database. Please check your database configuration.")
            return
        
        # Create the application
        app = QApplication(sys.argv)
        
        # Create and show the main window
        window = MainWindow()
        window.show()
        
        # Start the event loop
        sys.exit(app.exec_())
        
    except Exception as e:
        logging.error(f"Application error: {e}")
        print(f"Error running application: {e}")

if __name__ == '__main__':
    main() 