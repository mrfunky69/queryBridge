
from graph.state_schema import State
from agents.openai_chat_client import create_openai_chat_client
from utils.get_content import get_content

def clarify(state: State) -> dict:
    """
    LLM-based clarification node: when the user’s last turn
    wasn’t recognized as a data request, ask them to clarify
    which table/metric and time period they want.
    """
    # 1) Spin up a deterministic LLM
    config = state.get("app_config")
    llm = create_openai_chat_client(
        model="gpt-4.1",
        config=config,
        api_version="2024-10-21",
        temperature=0.0,
        max_tokens=128
    )

    # 2) Prime it with a system prompt
    system_msg = {
        "role": "system",
        "content": (
            "You are a multi‑source finance data assistant. "
            "You can fetch data from: 1) SAP HANA (finance tables), "
            "2) BigQuery (sales & customers), 3) Uploaded Excel files (queried via DuckDB after user uploads). "
            "If the user's request is NOT a data retrieval or is unrelated to available finance domains, "
            "politely steer them back: ask what finance metric, table, time range, or filter they need. "
            "If they want to query an Excel file and none is loaded, instruct them to upload it first. "
            "Be concise; do not fabricate capabilities outside these sources."
        )
    }

    # 3) Pass only the user’s last message as context
    last = state["messages"][-1]
    text = get_content(last)
    user_msg = {
        "role": "user",
        "content": text
    }

    # 4) Invoke the LLM
    resp = llm.invoke([system_msg, user_msg])

    # 5) Extract and return its reply
    clar_text = resp.content.strip()
    return {
        "messages": [
            {"role": "assistant", "content": clar_text}
        ]
    }