# graph/nodes/fallback_handler.py

def fallback_handler(state):
    print("fallback_handler", state)
    return {
        "message": "❌ I'm only capable of answering questions that result in SQL-based outputs."
    }
