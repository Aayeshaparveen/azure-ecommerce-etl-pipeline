from pathlib import Path
import logging
import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)

REQUIRED_COLUMNS = {
    "order_id", "order_date", "product", "quantity", "unit_price"
}


def transform_sales(input_file, silver_file, gold_file):
    """Read raw sales CSV, validate and clean it, then create silver and gold outputs."""
    input_path = Path(input_file)
    silver_path = Path(silver_file)
    gold_path = Path(gold_file)

    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    df = pd.read_csv(input_path)
    missing_columns = REQUIRED_COLUMNS - set(df.columns)
    if missing_columns:
        raise ValueError(f"Missing required columns: {sorted(missing_columns)}")

    starting_rows = len(df)
    df = df.drop_duplicates(subset=["order_id"], keep="first").copy()
    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
    df["unit_price"] = pd.to_numeric(df["unit_price"], errors="coerce")

    df = df.dropna(
        subset=["order_id", "order_date", "product", "quantity", "unit_price"]
    )
    df = df[(df["quantity"] > 0) & (df["unit_price"] >= 0)].copy()
    df["total_sales"] = df["quantity"] * df["unit_price"]
    df["order_date"] = df["order_date"].dt.strftime("%Y-%m-%d")

    silver_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(silver_path, index=False)

    gold = (
        df.groupby("order_date", as_index=False)
        .agg(
            daily_revenue=("total_sales", "sum"),
            total_orders=("order_id", "nunique"),
            units_sold=("quantity", "sum"),
        )
        .sort_values("order_date")
    )
    gold_path.parent.mkdir(parents=True, exist_ok=True)
    gold.to_csv(gold_path, index=False)

    logger.info(
        "ETL completed. Input rows=%s, valid sales rows=%s, removed rows=%s, daily summary rows=%s",
        starting_rows, len(df), starting_rows - len(df), len(gold)
    )
    logger.info("Silver output: %s", silver_path)
    logger.info("Gold output: %s", gold_path)
    return df, gold


if __name__ == "__main__":
    transform_sales(
        "data/raw/sales.csv",
        "data/silver/cleaned_sales.csv",
        "data/gold/daily_sales_summary.csv",
    )
