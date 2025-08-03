# graph/graph_builder.py

from langgraph.graph import StateGraph, END
from graph.nodes.llm_router import llm_router
from graph.nodes.fallback_handler import fallback_handler
from graph.nodes.table_metadata_fetcher import table_metadata_fetcher
from graph.nodes.sql_generator import sql_generator
from graph.nodes.sql_executor import sql_executor
from graph.state_schema import ChatState

def build_graph():
    builder = StateGraph(state_schema=ChatState)

    builder.add_node("llm_router", llm_router)
    builder.add_node("fallback_handler", fallback_handler)
    builder.add_node("table_metadata_fetcher", table_metadata_fetcher)
    builder.add_node("sql_generator", sql_generator)
    builder.add_node("sql_executor", sql_executor)

    builder.set_entry_point("llm_router")

    builder.add_conditional_edges(
        "llm_router",
        lambda state: "fallback_handler" if not state.get("is_sql_prompt") else "table_metadata_fetcher"
    )

    builder.add_edge("fallback_handler", END)

    builder.add_edge("table_metadata_fetcher", "sql_generator")
    builder.add_edge("sql_generator", "sql_executor")
    builder.add_edge("sql_executor", END)


    return builder.compile()
