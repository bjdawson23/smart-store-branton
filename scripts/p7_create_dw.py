"""
Module 4: Data Warehouse Creation Script
File: scripts/dw_create.py

This script handles the creation of the SQLite data warehouse. It creates tables
for returns, salesrep, product, and sale in the 'data/store_returns.db' database.
Each table creation is handled in a separate function for easier testing and error handling.
"""

import sqlite3
import sys
import pathlib
import pandas as pd

# For local imports, temporarily add project root to Python sys.path
PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

# Now we can import local modules
from utils.logger import logger  # noqa: E402

# Constants
DW_DIR: pathlib.Path = pathlib.Path("data").joinpath("dw")
DB_PATH: pathlib.Path = DW_DIR.joinpath("store_returns.db")

# Ensure the 'data/dw' directory exists
DW_DIR.mkdir(parents=True, exist_ok=True)

# Delete data warehouse file if it exists
if DB_PATH.exists():
    try:
        DB_PATH.unlink()  # Deletes the file
        logger.info(f"Existing database {DB_PATH} deleted.")
    except Exception as e:
        logger.error(f"Error deleting existing database {DB_PATH}: {e}")

def create_p7_product_table(cursor: sqlite3.Cursor) -> None:
    """Create p7_product table in the data warehouse."""
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS p7_products (
                product_id VARCHAR(20) PRIMARY KEY,
                category VARCHAR(50),
                sub_category VARCHAR(50),
                name VARCHAR(255),
                cost DECIMAL(10, 2),
                FOREIGN KEY (product_id) REFERENCES p7_sales(product_id)       
            )
        """)
        logger.info("p7_product table created.")
    except sqlite3.Error as e:
        logger.error(f"Error creating p7_product table: {e}")
    
def create_p7_sales_table(cursor: sqlite3.Cursor) -> None:
    """Create p7_sales table in the data warehouse."""
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS p7_sales (
                row_id INTEGER PRIMARY KEY,
                sale_id VARCHAR(20) NOT NULL,
                product_id VARCHAR(20) NOT NULL,
                sale_date DATE NOT NULL,
                ship_mode VARCHAR(50),
                ship_date DATE,
                customer_id VARCHAR(20) NOT NULL,
                customer_name VARCHAR(100),
                segment VARCHAR(50),
                country VARCHAR(50),
                city VARCHAR(50),
                state VARCHAR(50),
                postal_code VARCHAR(20),
                region VARCHAR(50),
                quantity INTEGER NOT NULL,
                discount DECIMAL(5, 2),
                sales DECIMAL(10, 2),
                profit DECIMAL(10, 2),
                FOREIGN KEY (product_id) REFERENCES p7_products(product_id),       
                FOREIGN KEY (sale_id) REFERENCES p7_returns(order_id),
                FOREIGN KEY (region) REFERENCES p7_salereps(region)       
            )
        """)
        logger.info("p7_sales table created.")
    except sqlite3.Error as e:
        logger.error(f"Error creating p7_sales table: {e}")

def create_p7_returns_table(cursor: sqlite3.Cursor) -> None:
    """Create p7_returns table in the data warehouse."""
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS p7_returns (
                order_id VARCHAR(20) PRIMARY KEY NOT NULL,
                returned VARCHAR(20) NOT NULL,
                FOREIGN KEY (order_id) REFERENCES p7_sales(sale_id)
            )
        """)
        logger.info("p7_returns table created.")
    except sqlite3.Error as e:
        logger.error(f"Error creating p7_returns table: {e}")

def create_p7_salesreps_table(cursor: sqlite3.Cursor) -> None:
    """Create p7_salesreps table in the data warehouse."""
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS p7_salesreps (
                region VARCHAR(50) PRIMARY KEY,
                sales_rep_name VARCHAR(100) NOT NULL,
                FOREIGN KEY (region) REFERENCES p7_sales(region)
            )
        """)
        logger.info("p7_salesreps table created.")
    except sqlite3.Error as e:
        logger.error(f"Error creating p7_salesreps table: {e}")

def create_dw() -> None:
    """Create the data warehouse by creating returns, salesreps, product, and sale tables."""
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Create tables
        create_p7_product_table(cursor)
        create_p7_sales_table(cursor)
        create_p7_returns_table(cursor)
        create_p7_salesreps_table(cursor)

        # Commit the changes and close the connection
        conn.commit()
        logger.info("All tables created successfully.")
        conn.close()

    except sqlite3.Error as e:
        logger.error(f"Error connecting to the database: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
    finally:
        if conn:
            conn.close()

def main() -> None:
    """Main function to create the data warehouse."""
    logger.info("Starting data warehouse creation...")
    create_dw()
    logger.info("Data warehouse creation complete.")

if __name__ == "__main__":
    main()
