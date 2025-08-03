
MOCK_TABLE_METADATA = {
    "SAP_HANA": {
    "PR2_SLT_QDX.ANLA": {
      "columns": ["ANLN1", "ANLN2", "BUKRS", "AKTIV", "DEAKT"],
      "primary_key": ["ANLN1", "BUKRS"],
    },
    "PR2_SLT_QDX.ANLA": {
      "columns": ["ANLN1", "BUKRS", "KOSTL"],
      "foreign_keys": [
        {
          "columns": ["ANLN1", "BUKRS"],
          "ref_table": "ANLA",
          "ref_columns": ["ANLN1", "BUKRS"]
        }
      ]
    }
  },
    "BIGQUERY": {
        "user_logs": {
            "columns": ["user_id", "login_time", "device"],
            "types": ["string", "timestamp", "string"]
        }
    }
}

def get_metadata() -> dict:
    return MOCK_TABLE_METADATA

def get_metadata_source_tables(source: str) -> dict:
    return MOCK_TABLE_METADATA.get(source,{})
