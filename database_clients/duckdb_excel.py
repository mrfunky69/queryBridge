
import duckdb
import pandas as pd

# Mock table for now: In real system, data comes from BigQuery, HANA, or Excel
MOCK_SALES_DATA = pd.DataFrame({
    "customer_id": [1, 2, 3],
    "sale_date": ["2023-01-01", "2023-02-01", "2023-03-01"],
    "amount": [100.0, 200.0, 150.0]
})

def execute_sql(sql_query):
    con = duckdb.connect(database=':memory:')
    con.register("sales_data", MOCK_SALES_DATA)
    try:
        result_df = con.execute(sql_query).df()
        return result_df.to_dict(orient="records")
    except Exception as e:
        return {
            "Error": True,
            "Message" : f"❌ SQL Execution Error: {str(e)}"
            }