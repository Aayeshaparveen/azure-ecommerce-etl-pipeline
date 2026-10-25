import pandas as pd
from src.transform_sales import transform_sales


def test_transform_sales_removes_duplicates_and_invalid_rows(tmp_path):
    input_file = tmp_path / "sales.csv"
    silver_file = tmp_path / "silver" / "cleaned_sales.csv"
    gold_file = tmp_path / "gold" / "daily_sales_summary.csv"

    pd.DataFrame([
        {"order_id": 1, "order_date": "2026-10-01", "product": "Book",
         "quantity": 2, "unit_price": 10},
        {"order_id": 1, "order_date": "2026-10-01", "product": "Book",
         "quantity": 2, "unit_price": 10},
        {"order_id": 2, "order_date": "bad-date", "product": "Pen",
         "quantity": 1, "unit_price": 2},
        {"order_id": 3, "order_date": "2026-10-02", "product": "Bag",
         "quantity": 0, "unit_price": 20},
    ]).to_csv(input_file, index=False)

    silver, gold = transform_sales(input_file, silver_file, gold_file)

    assert len(silver) == 1
    assert silver.iloc[0]["total_sales"] == 20
    assert len(gold) == 1
    assert gold.iloc[0]["daily_revenue"] == 20
