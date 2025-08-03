# main.py

from graph.graph_builder import build_graph
from graph.state_schema import ChatState
from aap_config import config

graph = build_graph()

def run_chat():
    print("🔷 SQL LangChat Agent (LLM-powered)\nType 'exit' to quit.\n")

    app_config = config()
    print("app_config", app_config)

    while True:
        user_prompt = input("🧑‍💻 Prompt: ")
        if user_prompt.strip().lower() in ["exit", "quit"]:
            break
        
        state = {"prompt": user_prompt, "app_config": app_config}
        result = graph.invoke(state)

        print("🤖 Response:")
        print(result)

if __name__ == "__main__":
    run_chat()
