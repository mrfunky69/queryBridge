
import os
import json
from dotenv import load_dotenv
from database_clients import sap_hana
from database_clients import bigquery

load_dotenv()  # Load from .env file if present

def config():
    
    conn_hana = sap_hana.connect()
    conn_bigq = bigquery.connect()

    bigquery_config = {}
    sa_path = os.environ.get("BIGQUERY_SERVICE_ACCOUNT_JSON_PATH")
    if sa_path and os.path.exists(sa_path):
        with open(sa_path) as f:
            bigquery_config["service_account"] = json.load(f)

    return {
        "llm_url": "http://localhost:11434/api/generate",
        "llm_model": "mistral",
        "conn_hana": conn_hana,
        "conn_bigq": conn_bigq
    }