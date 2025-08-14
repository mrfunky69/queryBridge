
from graph.state_schema import State
from agents.openai_chat_client import create_openai_chat_client
from utils.get_content import get_content
import json
import datetime
import decimal

def _json_safe(v):
    if isinstance(v, (str, int, float, bool)) or v is None:
        return v
    if isinstance(v, decimal.Decimal):
        return float(v)
    if isinstance(v, (datetime.datetime, datetime.date, datetime.time)):
        return v.isoformat()
    if isinstance(v, (bytes, bytearray, memoryview)):
        try:
            return bytes(v).decode("utf-8", errors="replace")
        except Exception:
            return str(v)
    if isinstance(v, (list, tuple)):
        return [_json_safe(x) for x in v]
    if isinstance(v, dict):
        return {str(k): _json_safe(val) for k, val in v.items()}
    # hdbcli ResultRow and other custom objects -> coerce to list/str
    try:
        return [_json_safe(x) for x in list(v)]
    except Exception:
        return str(v)

def postprocess(state: State) -> dict:
    """
    Take raw_table + original user request + executed SQL and produce:
    Insights, Chart_Type, Columns
    If multiple charts: Chart_Type is an array of objects: {type, columns}
    Output MUST be valid JSON with exactly these top-level keys:
      "Insights": string or array of strings
      "Chart_Type": object or array
      "Columns": array (union of columns referenced for main insight)
    """

    config = state.get("app_config")
    if "raw_table" not in state or not state["raw_table"]:
        return {"messages": [{"role": "assistant", "content": "No data available to analyze."}]}

    cols = state["raw_table"].get("cols", [])
    rows = state["raw_table"].get("rows", [])
    sample_rows = rows[:10]
    sql_text = state.get("sql", "")
    last_user = ""
    # find last user message
    for m in reversed(state["messages"]):
        role = m.get("role") if isinstance(m, dict) else getattr(m, "role", "")
        content = m.get("content") if isinstance(m, dict) else getattr(m, "content", "")
        if role == "user":
            last_user = content
            break
    suggested = []
    llm = create_openai_chat_client(
        model="gpt-4.1",
        config=config,
        api_version="2024-10-21",
        temperature=0.0,
        max_tokens=300
    )

    system_prompt = {
        "role": "system",
        "content": (
            "You are a senior financial data analyst. "
            "Given: (1) the user's request, (2) the executed SQL, (3) table columns, (4) sample rows, "
            "produce concise analytical insights and chart recommendations.\n"
            "RULES:\n"
            "- Output ONLY valid JSON (no markdown, no commentary).\n"
            "- Top-level keys EXACTLY: Insights, Chart_Type, Columns.\n"
            "- Insights: 1–5 short bullet-style sentences (can be string OR array of strings).\n"
            "- Chart_Type: If one chart is best, output an object {{\"type\": \"...\", \"columns\": [..]}}. "
            "If multiple useful charts, output an array of such objects.\n"
            "- Columns: array of the distinct column names central to the main insight (not all columns).\n"
            "- Do not invent columns; only use provided columns.\n"
            "- If data is empty, Insights should explain it's empty and Chart_Type an empty array.\n"
            "- Prefer line charts for time series; bar for categorical comparisons; pie only for small share distributions; heatmap for two categorical axes with a metric.\n"
            "- Keep it under 1200 characters.\n"
        )
    }

    safe_cols = [str(c) for c in cols]
    safe_sample_rows = []
    for r in sample_rows:
        if isinstance(r, dict):
            safe_sample_rows.append({str(k): _json_safe(v) for k, v in r.items()})
        else:
            # ResultRow/tuple/list -> list of json-safe values
            try:
                seq = list(r)
            except Exception:
                seq = [r]
            safe_sample_rows.append([_json_safe(v) for v in seq])


    user_payload = {
        "role": "user",
        "content": json.dumps({
            "original_user_request": last_user,
            "executed_sql": sql_text,
            "columns": safe_cols,
            "sample_rows": safe_sample_rows,
            "row_count": len(rows),
            "heuristic_chart_suggestions": suggested
        }, indent=2)
    }

    try:
        resp = llm.invoke([system_prompt, user_payload])
        content = resp.content.strip()
        # Basic validation: must start with { and contain required keys
        if not (content.startswith("{") and '"Insights"' in content and '"Chart_Type"' in content and '"Columns"' in content):
            # fallback JSON
            fallback = {
                "Insights": ["Could not parse model response; here are heuristic suggestions."],
                "Chart_Type": suggested or [],
                "Columns": cols[: min(5, len(cols))]
            }
            content = json.dumps(fallback, indent=2)
    except Exception as e:
        content = json.dumps({
            "Insights": [f"Postprocess error: {e}"],
            "Chart_Type": [],
            "Columns": []
        }, indent=2)

    return {
        "messages": state["messages"] + [{"role": "assistant", "content": content}]
    }
