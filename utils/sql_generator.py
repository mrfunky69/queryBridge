import json
from metadata.table_registry import MOCK_TABLE_METADATA

def _build_sql_generator_system_prompt(dialect: str) -> str:
    common_rules = (
        "GENERAL RULES:\n"
        "- Return ONLY a single SQL SELECT statement. No explanations, no backticks.\n"
        "- Always include an explicit LIMIT 200000 at the end unless a smaller limit already present.\n"
        "- Only use columns and tables that exist in the provided metadata.\n"
        "- If user asks for columns that do not exist, choose the closest valid columns without warning (do NOT invent new ones).\n"
        "- Prefer explicit column lists over SELECT * if user mentions any specific columns or metrics.\n"
        "- Use uppercase for SQL keywords.\n"
    )
    if dialect == "DUCKDB":
        return (
            "ROLE: You generate DuckDB SQL over local CSV files that originate from an EXCEL source.\n"
            "SOURCE MAPPING:\n"
            "- Excel table vendor_payments -> file 'vendor_payments.csv'\n"
            "- Excel table fixed_assets    -> file 'fixed_assets.csv'\n"
            "ACCESS RULES FOR DUCKDB:\n"
            "- Always reference the CSV directly using FROM 'vendor_payments.csv' (single quotes) or 'fixed_assets.csv'.\n"
            "- Do NOT prepend schemas; no database qualifiers.\n"
            "- If a column contains special characters like % wrap it in double quotes, e.g. \"Profit_Margin%\".\n"
            "- Date filtering: assume ISO format 'YYYY-MM-DD'.\n"
            "- If user asks about 'net book value', map to Net_Book_Value column.\n"
            "- If user asks about unpaid / pending invoices, filter Payment_Status IN ('Pending','Unpaid','OPEN') if mentioned.\n"
            + common_rules +
            "AVAILABLE COLUMNS:\n"
            f"{json.dumps(MOCK_TABLE_METADATA['EXCEL'], indent=2)}\n"
            "TASK: Given the conversation, output only the DuckDB SQL.\n"
        )
    elif dialect == "SAP_HANA":
        return (
            "ROLE: You generate SAP HANA SQL.\n"
            + common_rules +
            "If you are not able to clarify the query based on the user request generate a query closest to the user request.\n"
            "AVAILABLE TABLES:\n"
            f"{json.dumps(MOCK_TABLE_METADATA['SAP_HANA'], indent=2)}\n"
            "TASK: Produce a single SAP HANA compatible SELECT.\n"
        )
    elif dialect == "BIGQUERY":
        return (
            "ROLE: You generate BigQuery Standard SQL.\n"
            + common_rules +
            "SCHEMA HINT: Assume dataset finance unless specified. Do NOT add project unless user specifies.\n"
            "AVAILABLE TABLES:\n"
            f"{json.dumps(MOCK_TABLE_METADATA['BIGQUERY'], indent=2)}\n"
            "TASK: Produce a single BigQuery SELECT.\n"
        )
    else:
        return (
            "ROLE: Fallback SQL generator.\n"
            + common_rules +
            "Use safest generic ANSI SQL.\n"
        )
