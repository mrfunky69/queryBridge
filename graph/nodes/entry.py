from graph.state_schema import State
from agents.openai_chat_client import create_openai_chat_client
from utils.get_content import get_content

def entry(state: State) -> dict:
    # returns no state change
    return {}
