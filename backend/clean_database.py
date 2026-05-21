import os
import certifi
import pymysql
from dotenv import load_dotenv

def clean_and_recreate_db():
    print("--- STARTING DATABASE CLEANING AND RESET ---")
    
    # Load environment variables
    load_dotenv()
    load_dotenv(dotenv_path="backend/.env")
    load_dotenv(dotenv_path="../backend/.env")
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    if not DATABASE_URL:
        print("Error: DATABASE_URL not found in environment.")
        return

    # Automatically convert standard mysql:// to mysql+pymysql:// for PyMySQL support
    if DATABASE_URL.startswith("mysql://"):
        DATABASE_URL = DATABASE_URL.replace("mysql://", "mysql+pymysql://", 1)
        
    print(f"Connecting to database to clear tables...")
    
    # Parse DB connection info
    import re
    match = re.match(r"mysql\+pymysql://([^:]+):([^@]+)@([^:]+):(\d+)/(\w+)", DATABASE_URL)
    if not match:
        print("Error: Could not parse DATABASE_URL. Make sure it matches mysql+pymysql format.")
        return
        
    user, password, host, port, dbname = match.groups()
    is_local = "localhost" in host or "127.0.0.1" in host
    ssl_args = {"ssl": {"ca": certifi.where()}} if not is_local else {}
    
    try:
        # Connect to TiDB Cloud
        conn = pymysql.connect(
            host=host, 
            port=int(port), 
            user=user, 
            password=password, 
            database=dbname,
            **ssl_args
        )
        cursor = conn.cursor()
        
        # Disable foreign key checks to safely drop tables
        print("Disabling foreign key checks...")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
        
        # Get list of tables
        cursor.execute("SHOW TABLES;")
        tables = [row[0] for row in cursor.fetchall()]
        
        # Drop all tables
        for table in tables:
            print(f"Dropping table: {table}")
            cursor.execute(f"DROP TABLE IF EXISTS `{table}`;")
            
        # Re-enable foreign key checks
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
        conn.commit()
        
        print("\nAll tables successfully dropped! Recreating clean tables...")
        
        # Read and run setup_database.sql
        sql_file_path = "setup_database.sql"
        if not os.path.exists(sql_file_path):
            # Try parent directory
            sql_file_path = "../setup_database.sql"
            
        if os.path.exists(sql_file_path):
            with open(sql_file_path, "r") as f:
                sql_content = f.read()
                
            # Split by semicolon and run commands
            commands = sql_content.split(";")
            for command in commands:
                cleaned_command = command.strip()
                if cleaned_command and not cleaned_command.startswith("--"):
                    print(f"Executing command: {cleaned_command[:60]}...")
                    cursor.execute(cleaned_command)
            conn.commit()
            print("\nDatabase schemas recreated perfectly from setup_database.sql!")
        else:
            print("Warning: setup_database.sql file not found. Please recreate manually.")
            
        conn.close()
        print("--- DATABASE RESET COMPLETE ---")
        
    except Exception as e:
        print(f"Error resetting database: {e}")

if __name__ == "__main__":
    clean_and_recreate_db()
