
import duckdb
import pandas as pd

# Mock table for now: In real system, data comes from BigQuery, HANA, or Excel
MOCK_SALES_DATA = pd.DataFrame({
    "customer_id": [1, 2, 3],
    "sale_date": ["2023-01-01", "2023-02-01", "2023-03-01"],
    "amount": [100.0, 200.0, 150.0]
})

def connect():
    # Create in-memory DuckDB connection
    con = duckdb.connect()
    return con

def execute_sql(sql, con):
    try:
        result = con.execute(sql).fetchdf()
        cols = list(result.columns)
        rows = result.values.tolist()


        print({"raw_table": {"cols": cols, "rows": rows}})
        return {"raw_table": {"cols": cols, "rows": rows}}
    except Exception as e:
        print(f"Error executing DuckDB query: {e}")
        return {"raw_table": {"cols": [], "rows": []}}