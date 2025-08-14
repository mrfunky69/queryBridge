
from graph.state_schema import State
from agents.openai_chat_client import create_openai_chat_client
from utils.get_content import get_content
import json
from metadata.table_registry import MOCK_TABLE_METADATA
from utils.sql_generator import _build_sql_generator_system_prompt
from database_clients import bigquery, sap_hana, duckdb_excel


def _is_probably_sql(text: str) -> bool:
    if not text or not isinstance(text, str):
        return False
    # must include select and from, and must not look like plain English question
    return ("SELECT" in text or " FROM " in text) or not text.endswith("?")

def _fallback_sql(dialect: str, user_text: str) -> str:
    ut = (user_text or "").lower()

    if dialect == "SAP_HANA":
        if "expense" in ut or "department" in ut or "trend" in ut:
            return (
                "SELECT Department,\n"
                "       EXTRACT(YEAR FROM Expense_Date) AS year,\n"
                "       EXTRACT(MONTH FROM Expense_Date) AS month,\n"
                "       SUM(Amount) AS total_expense\n"
                "FROM expenses\n"
                "GROUP BY Department, EXTRACT(YEAR FROM Expense_Date), EXTRACT(MONTH FROM Expense_Date)\n"
                "ORDER BY year DESC, month DESC, total_expense DESC\n"
                "LIMIT 200"
            )
        if "budget" in ut:
            return (
                "SELECT Department, Month, Budget, Actual, Variance\n"
                "FROM budgets\n"
                "ORDER BY Month\n"
                "LIMIT 200"
            )
        if "withholding" in ut or "tax" in ut:
            return (
                "SELECT EXTRACT(YEAR FROM Posting_Date) AS year,\n"
                "       EXTRACT(MONTH FROM Posting_Date) AS month,\n"
                "       SUM(Tax_Amount) AS total_tax\n"
                "FROM withholding_tax\n"
                "GROUP BY EXTRACT(YEAR FROM Posting_Date), EXTRACT(MONTH FROM Posting_Date)\n"
                "ORDER BY year DESC, month DESC\n"
                "LIMIT 200"
            )
        if "profit margin" in ut or "profit_data" in ut or "profit" in ut:
            return (
                "SELECT Product,\n"
                "       SUM(Total_Amount) AS revenue,\n"
                "       SUM(Cost_Price) AS cost,\n"
                "       SUM(Profit) AS profit,\n"
                "       AVG(\"Profit_Margin%\") AS avg_profit_margin\n"
                "FROM profit_data\n"
                "GROUP BY Product\n"
                "ORDER BY revenue DESC\n"
                "LIMIT 200"
            )
        # default SAP HANA starter: monthly P&L
        return (
            "SELECT Month, Revenue, Expenses, Profit_or_Loss, P_L_Status\n"
            "FROM monthly_pnl\n"
            "ORDER BY Month DESC\n"
            "LIMIT 200"
        )

    if dialect == "BIGQUERY":
        if "customer" in ut or "loyalty" in ut:
            return (
                "SELECT CAST(EXTRACT(YEAR FROM signup_date) AS INT64) AS year,\n"
                "       COUNT(*) AS customers,\n"
                "       APPROX_QUANTILES(loyalty_points, 5) AS loyalty_point_quintiles\n"
                "FROM customers\n"
                "GROUP BY year\n"
                "ORDER BY year DESC\n"
                "LIMIT 50"
            )
        # default BigQuery starter: sales by product
        return (
            "SELECT Product,\n"
            "       SUM(Quantity) AS total_qty,\n"
            "       SUM(Total_Amount) AS revenue\n"
            "FROM sales\n"
            "GROUP BY Product\n"
            "ORDER BY revenue DESC\n"
            "LIMIT 200"
        )

    if dialect == "DUCKDB":  # EXCEL-backed
        if "asset" in ut:
            return (
                "SELECT Asset_ID, Asset_Name, Acquisition_Date, Acquisition_Value,\n"
                "       Depreciation_Value, Net_Book_Value\n"
                "FROM fixed_assets\n"
                "ORDER BY Net_Book_Value DESC\n"
                "LIMIT 200"
            )
        # default Excel starter: vendor payments by month
        return (
            "SELECT strftime(Payment_Date, '%Y') AS year,\n"
            "       strftime(Payment_Date, '%m') AS month,\n"
            "       SUM(Invoice_Amount) AS total_paid,\n"
            "       COUNT(*) AS payments\n"
            "FROM vendor_payments\n"
            "GROUP BY year, month\n"
            "ORDER BY year DESC, month DESC\n"
            "LIMIT 200"
        )

    # unknown dialect fallback: no-op
    return "SELECT 1"


def route_db(state: State) -> str:
    """
    Ask the LLM to decide whether which DB to hit depending on the metadata
    """
    # 1) Grab only the *last* user message
    config = state.get("app_config")
    last = state["messages"][-1]
    # if it’s a BaseMessage you can pull .content; if a dict, use ["content"]
    text = last.content if hasattr(last, "content") else last["content"]

    # 2) Build a tiny classification prompt
    system = {
        "role": "system",
        "content": (
            "ROLE: You are a deterministic classifier that selects exactly one data source.\n"
            "ALLOWED OUTPUT (MUST BE EXACT, NO EXTRA TEXT): SAP_HANA | BIGQUERY | EXCEL | CLARIFY\n\n"
            "DATA SOURCES & TABLE DOMAINS:\n"
            "- SAP_HANA: monthly_pnl (Month, Revenue, Expenses, Profit_or_Loss, P_L_Status), expenses (Expense_ID, Employee_Name, Department, Expense_Type, Expense_Date, Amount, Approval_Status), profit_data (Sale_ID, Sale_Date, Customer_Name, Product, Quantity, Unit_Price, Total_Amount, Cost_Price, Profit, Profit_Margin%), budgets (Department, Month, Budget, Actual, Variance), withholding_tax (Document_ID, Vendor_ID, Tax_Code, Tax_Percentage, Tax_Amount, Posting_Date)\n"
            "- BIGQUERY: sales (Sale_ID, Sale_Date, Customer_Name, Product, Quantity, Unit_Price, Total_Amount), customers (customer_id, name, loyalty_points, signup_date)\n"
            "- EXCEL: vendor_payments (Vendor_ID, Vendor_Name, Invoice_Number, Invoice_Date, Payment_Date, Invoice_Amount, Payment_Status, Category, Related_Revenue, Profit_or_Loss, P_L_Status), fixed_assets (Asset_ID, Asset_Name, Acquisition_Date, Acquisition_Value, Depreciation_Value, Net_Book_Value)\n\n"
            "DECISION RULES:\n"
            "1. If the user references a table name or unmistakable column set belonging to one source, choose that source.\n"
            "2. If request mentions: invoices, vendors, payments, assets -> EXCEL.\n"
            "3. If request mentions: sales transactions (Sale_ID, Product, Quantity, Unit_Price, customers, loyalty) -> BIGQUERY.\n"
            "4. If request mentions: budgets, monthly pnl, expenses, withholding tax, profit margin% -> SAP_HANA.\n"
            "5. General finance KPIs (revenue, expenses, profit) with time granularity (month/department) -> SAP_HANA.\n"
            "6. No filters is OK: still classify; DO NOT return CLARIFY just because filters are missing.\n"
            "7. Return CLARIFY ONLY if: (a) ambiguous between two sources, (b) no table/column/semantic hint matches any source, or (c) user asks something outside provided schema.\n"
            "8. Never invent a new source. Never output explanations.\n\n"
            f"METADATA (for reference): {json.dumps(MOCK_TABLE_METADATA, indent=2)}\n\n"
            "EXAMPLES:\n"
            "User: show me vendor payments last quarter -> EXCEL\n"
            "User: list fixed assets with net book value > 10000 -> EXCEL\n"
            "User: get sales by product for July -> BIGQUERY\n"
            "User: customer loyalty points distribution -> BIGQUERY\n"
            "User: monthly profit and loss variance -> SAP_HANA\n"
            "User: withholding tax documents this year -> SAP_HANA\n"
            "User: compare budget vs actual for marketing -> SAP_HANA\n"
            "User: fetch revenue, expenses, profit -> SAP_HANA\n"
            "User: give me something interesting -> CLARIFY\n"
            "User: show table structure -> CLARIFY (no target domain)\n\n"
            "OUTPUT FORMAT: Return ONLY one of: SAP_HANA | BIGQUERY | EXCEL | CLARIFY"
        )
    }
    user   = {"role": "user", "content": text}

    # 3) Invoke your LLM synchronously (deterministic)
    llm = create_openai_chat_client(
        model="gpt-4.1",
        config=config,
        api_version="2024-10-21",
        temperature=0.0,
        max_tokens=10
    )
    resp = llm.invoke([system, user])
    print(f"LLM response: {resp.content.strip()}")
    if resp.content.strip() == "SAP_HANA":
        # record the dialect in state
        return "SAP_HANA"
    elif resp.content.strip() == "BIGQUERY":
        return "BIGQUERY"
    elif resp.content.strip() == "EXCEL":
        return "DUCKDB"
    else:  # unknown table: ask for clarification
        return "CLARIFY"



def sql_generator(state: State) -> dict:
    """
    Generate a single SQL statement and execute it, storing both the SQL and result.
    """
    config = state.get("app_config")
    print("Generating SQL from chat history...")
    dialect = route_db(state)
    print(f"dialect: {dialect}")

    last_msg = state["messages"][-1]
    last_text = last_msg.content if hasattr(last_msg, "content") else last_msg.get("content", "")

    if dialect == "CLARIFY":
        return {"sql": "", "needs_clarification": True}

    llm = create_openai_chat_client(
        model="gpt-4.1",
        config=config,
        api_version="2024-10-21",
        temperature=0.0,
        max_tokens=256
    )

    system_msg = {
        "role": "system",
        "content": _build_sql_generator_system_prompt(dialect)
    }
    prompt_messages = [system_msg] + state["messages"]
    response = llm.invoke(prompt_messages)
    sql = response.content.strip()
    print(f"Generated SQL: {sql}")

    used_fallback = False
    # If model didn't return SQL, use a sensible starter query
    if not _is_probably_sql(sql) or sql.strip() == last_text.strip():
        sql = _fallback_sql(dialect, last_text)
        used_fallback = True
        print("Model did not return valid SQL. Using fallback starter query.")


    # Execute according to dialect; always keep sql in returned state
    if dialect == 'SAP_HANA':
        data = sap_hana.hana_query(sql, config.get('conn_hana'))
    elif dialect == 'BIGQUERY':
        # bigquery_query expects a state-like dict containing sql
        data = bigquery.bigquery_query(state={"sql": sql}, client=config.get('conn_bigq')) 
    elif dialect == 'DUCKDB':
        data = duckdb_excel.execute_sql(sql=sql, con=config.get('conn_duckdb')) 
    else:
        data = {"raw_table": {"cols": [], "rows": []}}

    print("sql_generator : ", data)
    return {
        "sql": sql,
        "raw_table": data.get("raw_table", {}),
        "needs_clarification": False
    }