import pandas as pd
import sqlite3
import pathlib
import sys
import os

# Add the project root to the Python path
PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from utils.logger import logger

# Constants
DW_DIR = pathlib.Path("data").joinpath("dw")
DB_PATH = DW_DIR.joinpath("store_returns.db")
PREPARED_DATA_DIR = pathlib.Path("data").joinpath("prepared")

def delete_existing_records(cursor: sqlite3.Cursor) -> None:
    """Delete all existing records from the p7_returns, p7_salesreps, p7_products, and p7_sales tables."""
    try:
        cursor.execute("DELETE FROM p7_returns")
        cursor.execute("DELETE FROM p7_products")
        cursor.execute("DELETE FROM p7_salesreps")
        cursor.execute("DELETE FROM p7_sales")
        logger.info("Existing records deleted from all tables.")
    except sqlite3.Error as e:
        logger.error(f"Error deleting existing records: {e}")

def validate_csv_columns(df: pd.DataFrame, required_columns: list) -> bool:
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        logger.error(f"Missing columns: {missing_columns}")
        return False
    return True

def load_p7_products(cursor: sqlite3.Cursor, file_path: str) -> None:
    """Load data from p7_products.csv into the p7_products table."""
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return
    try:
        df = pd.read_csv(file_path)
        df.to_sql('p7_products', cursor.connection, if_exists='append', index=False)
        logger.info(f"Data from {file_path} loaded into p7_products table.")
    except Exception as e:
        logger.error(f"Error loading data into p7_products table: {e}")

def load_p7_sales(cursor: sqlite3.Cursor, file_path: str) -> None:
    """Load data from p7_sales.csv into the p7_sales table."""
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return
    try:
        df = pd.read_csv(file_path)
        # Convert date columns to proper format
        df['sale_date'] = pd.to_datetime(df['sale_date'], errors='coerce')
        df['ship_date'] = pd.to_datetime(df['ship_date'], errors='coerce')
        # Remove dollar signs and commas from sales and profit columns
        df['sales'] = df['sales'].replace(r'[\$,]', '', regex=True).astype(float)
        df['profit'] = df['profit'].replace(r'[\$,]', '', regex=True).astype(float)
        df.to_sql('p7_sales', cursor.connection, if_exists='append', index=False)
        logger.info(f"Data from {file_path} loaded into p7_sales table.")
    except Exception as e:
        logger.error(f"Error loading data into p7_sales table: {e}")

def load_p7_returns(cursor: sqlite3.Cursor, file_path: str) -> None:
    """Load data from p7_returns.csv into the p7_returns table."""
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return
    try:
        df = pd.read_csv(file_path)
        df.to_sql('p7_returns', cursor.connection, if_exists='append', index=False)
        logger.info(f"Data from {file_path} loaded into p7_returns table.")
    except Exception as e:
        logger.error(f"Error loading data into p7_returns table: {e}")

def load_p7_salesreps(cursor: sqlite3.Cursor, file_path: str) -> None:
    """Load data from p7_salesreps.csv into the p7_salesreps table."""
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return
    try:
        df = pd.read_csv(file_path)
        df.to_sql('p7_salesreps', cursor.connection, if_exists='append', index=False)
        logger.info(f"Data from {file_path} loaded into p7_salesreps table.")
    except Exception as e:
        logger.error(f"Error loading data into p7_salesreps table: {e}")

def insert_returns(df: pd.DataFrame, cursor: sqlite3.Cursor) -> None:
    """Insert data into the p7_returns table."""
    try:
        df.to_sql('p7_returns', cursor.connection, if_exists='append', index=False)
        logger.info("Data inserted into p7_returns table.")
    except Exception as e:
        logger.error(f"Error inserting data into p7_returns table: {e}")

def insert_products(df: pd.DataFrame, cursor: sqlite3.Cursor) -> None:
    """Insert data into the p7_products table."""
    try:
        df.to_sql('p7_products', cursor.connection, if_exists='append', index=False)
        logger.info("Data inserted into p7_products table.")
    except Exception as e:
        logger.error(f"Error inserting data into p7_products table: {e}")

def insert_sales(df: pd.DataFrame, cursor: sqlite3.Cursor) -> None:
    """Insert data into the p7_sales table."""
    try:
        df.to_sql('p7_sales', cursor.connection, if_exists='append', index=False)
        logger.info("Data inserted into p7_sales table.")
    except Exception as e:
        logger.error(f"Error inserting data into p7_sales table: {e}")

def insert_salesreps(df: pd.DataFrame, cursor: sqlite3.Cursor) -> None:
    """Insert data into the p7_salesreps table."""
    try:
        # Rename the column to match the table schema
        df.rename(columns={"sales_rep": "sales_rep_name"}, inplace=True)
        df.to_sql('p7_salesreps', cursor.connection, if_exists='append', index=False)
        logger.info("Data inserted into p7_salesreps table.")
    except Exception as e:
        logger.error(f"Error inserting data into p7_salesreps table: {e}")

def create_p7_product_table(cursor: sqlite3.Cursor) -> None:
    """Create p7_products table in the data warehouse."""
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS p7_products (
                product_id VARCHAR(20) PRIMARY KEY,
                category VARCHAR(50),
                sub_category VARCHAR(50),
                name VARCHAR(255),
                cost DECIMAL(10, 2)
            )
        """)
        logger.info("p7_products table created.")
    except sqlite3.Error as e:
        logger.error(f"Error creating p7_products table: {e}")

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
                FOREIGN KEY (product_id) REFERENCES p7_products(product_id)
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
                sales_rep VARCHAR(100) NOT NULL
            )
        """)
        logger.info("p7_salesreps table created.")
    except sqlite3.Error as e:
        logger.error(f"Error creating p7_salesreps table: {e}")

def create_dw() -> None:
    """Create the data warehouse by creating tables and loading data from CSV files."""
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Create tables
        create_p7_product_table(cursor)
        create_p7_sales_table(cursor)
        create_p7_returns_table(cursor)
        create_p7_salesreps_table(cursor)

        # Check for missing files
        if not os.path.exists("data/raw/p7_products.csv"):
            logger.error("p7_products.csv is missing.")
        if not os.path.exists("data/raw/p7_sales.csv"):
            logger.error("p7_sales.csv is missing.")
        if not os.path.exists("data/raw/p7_returns.csv"):
            logger.error("p7_returns.csv is missing.")
        if not os.path.exists("data/raw/p7_salesreps.csv"):
            logger.error("p7_salesreps.csv is missing.")

        # Commit the changes and close the connection
        conn.commit()
        conn.close()
        logger.info("Data warehouse created and data loaded successfully.")

    except sqlite3.Error as e:
        logger.error(f"Error connecting to the database: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
    finally:
        if conn:
            conn.close()

def load_data_to_db() -> None:
    try:
        # Connect to SQLite – will create the file if it doesn't exist
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Create schema (create tables)
        create_p7_product_table(cursor)
        create_p7_sales_table(cursor)
        create_p7_returns_table(cursor)
        create_p7_salesreps_table(cursor)

        # Clear existing records
        delete_existing_records(cursor)

        # Load prepared data using pandas
        returns_df = pd.read_csv(PREPARED_DATA_DIR.joinpath("p7_returns_data_prepared.csv"))
        products_df = pd.read_csv(PREPARED_DATA_DIR.joinpath("p7_products_data_prepared.csv"))
        sales_df = pd.read_csv(PREPARED_DATA_DIR.joinpath("p7_sales_data_prepared.csv"))
        salesreps_df = pd.read_csv(PREPARED_DATA_DIR.joinpath("p7_salesreps_data_prepared.csv"))

        # Insert data into the database
        insert_returns(returns_df, cursor)
        insert_products(products_df, cursor)
        insert_sales(sales_df, cursor)
        insert_salesreps(salesreps_df, cursor)

        conn.commit()
        logger.info("Data loaded into the database successfully.")
    except Exception as e:
        logger.error(f"Error loading data into the database: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    load_data_to_db()