import os
from dotenv import load_dotenv
from hdbcli import dbapi

load_dotenv()  # Load from .env file if present

def connect():
    try:
        conn = dbapi.connect(
            address=os.environ["SAP_HANA_HOST"],
            port=int(os.environ["SAP_HANA_PORT"]),
            user=os.environ["SAP_HANA_USER"],
            password=os.environ["SAP_HANA_PASSWORD"]
        )
        return conn
    except Exception as e:
        print("Error ,", e)
        #raise Exception("HANA connection failed")


def execute_sql(query, conn):
    print("********** RUNNING SQL ************", query, conn)
    try:
        cursor = conn.cursor()
        cursor.execute(query)
        result = cursor.fetchall()
        columns = [col[0] for col in cursor.description]
        return {"columns": columns, "rows": result}
    except Exception as e:
        print("Error execute_sql hana \n", e)
        return {"Error": True}