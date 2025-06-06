"""
Module 6: OLAP Goal Script (uses cubed results)
File: scripts/olap_goals_top_product_by_month.py

This script uses our precomputed cubed data set to get the information 
we need to answer a specific business goal. 

GOAL: Analyze sales data to determine the product with the highest revenue 
for each Month. 

ACTION: This can help inform inventory decisions, optimize promotions, 
and understand purchasing patterns on different days.

PROCESS: 
Group transactions by the Month and product.
Sum SaleAmount for each product each Month.
Identify the top product for each Month based on total revenue.

month,product_id,customer_id,sale_amount_usd_sum,sale_amount_usd_mean,sale_id_count,sale_ids
April,101,1001,6344.96,6344.96,1,[582]
"""

import pandas as pd
import matplotlib.pyplot as plt
import pathlib
import sys

# For local imports, temporarily add project root to Python sys.path
PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from utils.logger import logger  # noqa: E402

# Constants
OLAP_OUTPUT_DIR: pathlib.Path = pathlib.Path("data").joinpath("olap_cubing_outputs")
CUBED_FILE: pathlib.Path = OLAP_OUTPUT_DIR.joinpath("multidimensional_olap_month_cube.csv")
RESULTS_OUTPUT_DIR: pathlib.Path = pathlib.Path("data").joinpath("results")

# Create output directory for results if it doesn't exist
RESULTS_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def load_olap_cube(file_path: pathlib.Path) -> pd.DataFrame:
    """Load the precomputed OLAP cube data."""
    try:
        cube_df = pd.read_csv(file_path)
        logger.info(f"OLAP cube data successfully loaded from {file_path}.")
        return cube_df
    except Exception as e:
        logger.error(f"Error loading OLAP cube data: {e}")
        raise


def analyze_top_product_by_month(cube_df: pd.DataFrame) -> pd.DataFrame:
    """Identify the product with the highest revenue for each month."""
    try:
        # Group by month and product_id, sum the sales
        grouped = cube_df.groupby(["Month", "product_id"])["sale_amount_usd_sum"].sum().reset_index()
        grouped.rename(columns={"sale_amount_usd_sum": "TotalSales"}, inplace=True)

        # Sort within each day to find the top product
        top_products = grouped.sort_values(["Month", "TotalSales"], ascending=[True, False]).groupby("Month").head(1)
        logger.info("Top products identified for each month.")
        return top_products
    except Exception as e:
        logger.error(f"Error analyzing top product by month: {e}")
        raise


def visualize_sales_by_month_and_product(cube_df: pd.DataFrame) -> None:
    """Visualize total sales by month, broken down by product."""
    try:
        # Pivot the data to organize sales by Month and ProductID
        sales_pivot = cube_df.pivot_table(
            index="Month",
            columns="product_id",
            values="sale_amount_usd_sum",
            aggfunc="sum",
            fill_value=0
        )

        # Plot the stacked bar chart
        sales_pivot.plot(
            kind="bar",
            stacked=True,
            figsize=(12, 8),
            colormap="tab10"
        )

        plt.title("Total Sales by Month and Product", fontsize=16)
        plt.xlabel("Month", fontsize=12)
        plt.ylabel("Total Sales (USD)", fontsize=12)
        plt.xticks(rotation=45)
        plt.legend(title="Product ID", bbox_to_anchor=(1.05, 1), loc="upper left")
        plt.tight_layout()

        # Save the visualization
        output_path = RESULTS_OUTPUT_DIR.joinpath("sales_by_month_and_product.png")
        plt.savefig(output_path)
        logger.info(f"Stacked bar chart saved to {output_path}.")
        plt.show()
    except Exception as e:
        logger.error(f"Error visualizing sales by month and product: {e}")
        raise


def main():
    """Main function for analyzing and visualizing top product sales by month."""
    logger.info("Starting SALES_TOP_PRODUCT_BY_MONTH analysis...")

    # Step 1: Load the precomputed OLAP cube
    cube_df = load_olap_cube(CUBED_FILE)

    # Step 2: Analyze top products by Month
    top_products = analyze_top_product_by_month(cube_df)
    logger.info("Top products by month analysis completed.")
    logger.debug("Top products by month:\n%s", top_products)
    print(top_products)

    # Step 3: Visualize the results
    visualize_sales_by_month_and_product(cube_df)
    logger.info("Analysis and visualization completed successfully.")


if __name__ == "__main__":
    main()