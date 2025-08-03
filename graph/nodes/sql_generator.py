# graph/nodes/sql_generator.py

from agents.ollama_sql_generator import generate_sql_from_prompt

def sql_generator(state):
    prompt = state["prompt"]
    metadata = state["table_metadata"]
    app_config = state["app_config"]
    print("🧠 sql_generator ", state)
    metadata["source"]= metadata.get("source", "")
    sql_query = generate_sql_from_prompt(prompt, metadata, app_config)
    state["generated_sql"] = sql_query
    return state
