import os
from dotenv import load_dotenv
from google.cloud import bigquery
from graph.state_schema import State
from typing import Any, Dict, List

load_dotenv() 

os.environ["GOOGLE_APPLICATION_CREDENTIALS"]=os.environ["BIGQUERY_SERVICE_ACCOUNT_JSON_PATH"]

def connect():
    try:
        client = bigquery.Client()
        return client
    except Exception as e:
        print("Error ,", e)
        #raise Exception("bigQ connection failed")

def bigquery_query(state: State, client) -> Dict[str, Any]:
    
    sql = state["sql"].strip()
    print(f"Executing BigQuery SQL: {sql}")

    try:
        if not sql:
            raise ValueError("No SQL statement found in state['sql']")
        # Kick off the query
        job = client.query(sql)
        result = job.result()  # blocks until the job completes
        cols: List[str] = [field.name.upper() for field in result.schema]
        rows: List[List[Any]] = [list(row) for row in result]
        # Extract schema + data
        return {"raw_table": {"cols": cols, "rows": rows}} 
    except Exception as e:
        print("error in bigquery_query ", e)
    

      

def execute_sql(query, client):
    query_job = client.query(query)
    results = query_job.result()
    return results