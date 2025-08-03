import os
from dotenv import load_dotenv
from google.cloud import bigquery

load_dotenv() 

os.environ["GOOGLE_APPLICATION_CREDENTIALS"]=os.environ["BIGQUERY_SERVICE_ACCOUNT_JSON_PATH"]

def connect():
    try:
        client = bigquery.Client()
        return client
    except Exception as e:
        print("Error ,", e)
        #raise Exception("bigQ connection failed")

    

def execute_sql(query, client):
    query_job = client.query(query)
    results = query_job.result()
    return results