# agents/ollama_router_agent.py

import requests

def call_ollama(prompt: str, metadata: dict, config) -> dict:
    """
    Calls local Ollama server to determine:
    - Whether it's a SQL query
    - Which data source
    """
    system_prompt = """
You are an intelligent AI assistant that helps route user prompts to correct data sources.
Based on the prompt and given metadata, determine if the query should be answered via SQL

If the question is general knowledge (like 'who is the president of...'), mark it as non-SQL.

You have to strictly Respond in JSON with given format below:
{
    "is_sql_prompt": True/False,
    "data_source": "SAP_HANA" | "BIGQUERY" | "EXCEL"
}
fields included in json response are is_sql_prompt, data_source only, do not add any other fields 
and no explanation required
"""

    user_prompt = f"""
User Prompt: {prompt}

Metadata:
{metadata}
"""
    url = config.get("llm_url", "")
    model = config.get("llm_model", "")
    res = requests.post(
        url,
        json={
            "model": model,  # or whichever model you pulled with Ollama
            "prompt": system_prompt + user_prompt,
            "stream": False
        }
    )
    print("call_ollama", res)
    raw_output = res.json()["response"]
    

    try:
        response = eval(raw_output.strip())
        return response
    except Exception:

        return {
            "is_sql_prompt": False,
            "data_source": None
        }
