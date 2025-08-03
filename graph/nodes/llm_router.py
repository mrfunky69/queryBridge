# graph/nodes/llm_router.py

from metadata.table_registry import get_metadata
from agents.ollama_router_agent import call_ollama

def llm_router(state):
    prompt = state["prompt"]
    app_config = state["app_config"]
    # Merge all metadata for now (or refine based on config)
    metadata = get_metadata()
    decision = call_ollama(prompt, metadata, app_config)
    state.update(decision)
    return state
