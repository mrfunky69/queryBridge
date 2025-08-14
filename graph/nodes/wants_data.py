
from graph.state_schema import State
from agents.openai_chat_client import create_openai_chat_client
from utils.get_content import get_content


def wants_data(state: State) -> bool:
    """
    Ask the LLM to decide whether the user is requesting
    data (i.e. should we fire the sql_generator node?).
    Returns True or False.
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
            "You are a binary classifier. "
            "Given a single user request, you must output exactly "
            "`true` if they are asking to retrieve or query data from the database, "
            "or `false` otherwise. Respond with only `true` or `false`."
        )
    }
    user   = {"role": "user", "content": text}

    # 3) Invoke your LLM synchronously (deterministic)
    llm = create_openai_chat_client(
        model="gpt-4.1",
        config = config,
        api_version="2024-10-21",
        temperature=0.0,
        max_tokens=1
    )
    resp = llm.invoke([system, user])

    # 4) Parse the model’s answer
    answer = resp.content.strip().lower()
    return answer == "true"