import pandas as pd
import sqlite3
import pathlib
import sys

# For local imports, temporarily add project root to sys.path
PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

# Constants
DW_DIR = pathlib.Path("data").joinpath("dw")
DB_PATH = DW_DIR.joinpath("smart_sales.db")
PREPARED_DATA_DIR = pathlib.Path("data").joinpath("prepared")

def create_schema(cursor: sqlite3.Cursor) -> None:
    """Create tables in the data warehouse if they don't exist."""
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customer (
            customer_id INTEGER PRIMARY KEY,
            name TEXT,
            region TEXT,
            join_date TEXT,
            loyalty_points INTEGER,
            prefered_contact_method TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS product (
            product_id INTEGER PRIMARY KEY,
            name TEXT,
            category TEXT,
            unit_price REAL,
            year_added INTEGER,
            subcategory TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sale (
            sale_id INTEGER PRIMARY KEY,
            customer_id INTEGER,
            product_id INTEGER,
            store_id INTEGER,
            campaign_id INTEGER,
            sale_date DATE,
            quantity INTEGER,
            sale_amount_usd REAL,
            discount_amount_usd INTEGAR,
            payment_method TEXT,            
            FOREIGN KEY (customer_id) REFERENCES customer (customer_id),
            FOREIGN KEY (product_id) REFERENCES product (product_id)
        )
    """)

def delete_existing_records(cursor: sqlite3.Cursor) -> None:
    """Delete all existing records from the customer, product, and sale tables."""
    cursor.execute("DELETE FROM customer")
    cursor.execute("DELETE FROM product")
    cursor.execute("DELETE FROM sale")

def insert_customers(customers_df: pd.DataFrame, cursor: sqlite3.Cursor) -> None:
    """Insert customer data into the customer table."""
    # Keep only the columns that match the database schema
    customers_df = customers_df[[
        "customer_id",
        "name",
        "region",
        "join_date",
        "loyalty_points",
        "preferred_contact_method"
    ]]
    
    # Insert data into the database
    customers_df.to_sql("customer", cursor.connection, if_exists="append", index=False)

def insert_products(products_df: pd.DataFrame, cursor: sqlite3.Cursor) -> None:
    """Insert product data into the product table."""
    products_df.to_sql("product", cursor.connection, if_exists="append", index=False)

def insert_sales(sales_df: pd.DataFrame, cursor: sqlite3.Cursor) -> None:
    """Insert sales data into the sales table."""
    # Normalize and validate payment_method values
    valid_methods = ['Credit_Card', 'Cash']
    sales_df['payment_method'] = sales_df['payment_method'].str.strip().str.title()
    sales_df['payment_method'] = sales_df['payment_method'].where(
        sales_df['payment_method'].isin(valid_methods), 'Cash'
    )
    sales_df['payment_method'] = sales_df['payment_method'].fillna('Cash')

    # Insert data into the database
    sales_df.to_sql("sale", cursor.connection, if_exists="append", index=False)

def load_data_to_db() -> None:
    try:
        # Connect to SQLite – will create the file if it doesn't exist
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Create schema and clear existing records
        create_schema(cursor)
        delete_existing_records(cursor)

        # Load prepared data using pandas
        customers_df = pd.read_csv(PREPARED_DATA_DIR.joinpath("customers_data_prepared.csv"))
        products_df = pd.read_csv(PREPARED_DATA_DIR.joinpath("products_data_prepared.csv"))
        sales_df = pd.read_csv(PREPARED_DATA_DIR.joinpath("sales_data_prepared.csv"))

        # Print unique payment methods
        print(sales_df['payment_method'].unique())

        # Clean and validate payment methods
        valid_methods = ['Credit_Card', 'Cash']
        sales_df['payment_method'] = sales_df['payment_method'].fillna('Cash')
        sales_df['payment_method'] = sales_df['payment_method'].str.strip().str.title()
        sales_df['payment_method'] = sales_df['payment_method'].where(
            sales_df['payment_method'].isin(valid_methods), 'Cash'
        )

        # Insert data into the database
        insert_customers(customers_df, cursor)
        insert_products(products_df, cursor)
        insert_sales(sales_df, cursor)

        conn.commit()
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    load_data_to_db()