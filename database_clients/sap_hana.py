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

def hana_query(sql, conn) -> dict:

    conn = connect()
    try: 
        cur = conn.cursor()
        cur.execute(sql)
        cols = [d[0] for d in cur.description]
        rows = cur.fetchall()
        conn.close()
        return {"raw_table": {"cols": cols, "rows": rows}}
    except Exception as e:
        print("error in hana_query : ", e)