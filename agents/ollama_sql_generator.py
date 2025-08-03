# agents/ollama_sql_generator.py

import requests
import json


def generate_sql_from_prompt(prompt: str, metadata: dict, config) -> str:
    source = metadata.get('source', '')
    system_prompt = ''
    if source == 'SAP_HANA' :
        system_prompt = """
            You are an expert SAP SQL developer. who have knowledge on sap tables and how they are related to each other,Based on the user's question and table metadata, generate a SQL query.
            Only use available tables and columns. Do not hallucinate columns or table names.

            Return only the SQL query string. No explanations.
            """
    else:
        system_prompt = """
            You are an expert SQL developer. Based on the user's question and table metadata, generate a SQL query.
            Only use available tables and columns. Do not hallucinate columns or table names.

            Return only the SQL query string. No explanations.
            """

    user_prompt = f"""
User Prompt: {prompt}

Available Tables and Columns:
{json.dumps(metadata, indent=2)}
"""

    res = requests.post(
        config.get("llm_url", ""),
        json={
            "model": config.get("llm_model", ""),
            "prompt": system_prompt + user_prompt,
            "stream": False
        }
    )

    print('response generate_sql_from_prompt', res.json()["response"])

    return res.json()["response"].strip()
