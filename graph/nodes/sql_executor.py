# graph/nodes/sql_executor.py

import duckdb
import pandas as pd
from database_clients import SQL_CLIENTS



def sql_executor(state):
    print('🧠 sql_executor', state)
    source = state["data_source"]
    sql_query = state["generated_sql"]
    conn = state["app_config"].get("conn_hana")

    if not sql_query or not source:
        return {
            **state,
            "error": "Missing SQL or source in state",
            "query_result": None
        }
    
    try:
        execute_fn = SQL_CLIENTS[source]
        print("running")
        result = execute_fn(sql_query, conn)
        print("running 1")
        state = {
            **state,
            "query_result": result
        }
        return state
    except Exception as e:
        state = {
            **state,
            "error": str(e),
            "query_result": None
        }
        return state
