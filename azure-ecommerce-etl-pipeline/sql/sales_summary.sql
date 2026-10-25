-- Example SQL for a database table named cleaned_sales.
-- Load data/silver/cleaned_sales.csv into that table before running this query.

SELECT
    order_date,
    SUM(total_sales) AS daily_revenue,
    COUNT(DISTINCT order_id) AS total_orders,
    SUM(quantity) AS units_sold
FROM cleaned_sales
GROUP BY order_date
ORDER BY order_date;
