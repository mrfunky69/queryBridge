from database_clients import sap_hana, bigquery, duckdb_excel

SQL_CLIENTS = {
    "SAP_HANA": sap_hana.execute_sql,
    "BIGQUERY": bigquery.execute_sql,
    "EXCEL": duckdb_excel.execute_sql
}
