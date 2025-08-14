
from graph.state_schema import State
from agents.openai_chat_client import create_openai_chat_client
from utils.get_content import get_content

def route_after_sql_generator(state: State) -> bool:
    """
    Route after sql_generator based on whether clarification is needed
    """
    return state.get('needs_clarification', False) == True