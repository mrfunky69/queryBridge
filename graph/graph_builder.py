# graph/graph_builder.py

from langgraph.graph import StateGraph, END
from graph.state_schema import State
from langgraph.graph import StateGraph, START, END
from graph.nodes.clarify import clarify
from graph.nodes.sql_generator import sql_generator
from graph.nodes.post_process import postprocess
from graph.nodes.wants_data import wants_data
from graph.nodes.route_after_sql_generator import route_after_sql_generator
from graph.nodes.entry import entry



def build_graph():
    graph_builder = StateGraph(state_schema=State)


    graph_builder.add_node("sql_generator", sql_generator)
    graph_builder.add_node("postprocess",   postprocess)
    graph_builder.add_node("clarify",       clarify)
    graph_builder.add_node("wants_data",    wants_data)
    graph_builder.add_node("route_after_sql_generator",route_after_sql_generator)
    graph_builder.add_node("entry",         entry)

   

    # 3) Replace the two START→X edges with one conditional edge out of chatbot
    # graph_builder.add_edge(START, "chatbot")
    graph_builder.add_edge(START, "entry")  # entry point
    graph_builder.add_conditional_edges(
        "entry",
        wants_data,
        {
        True: "sql_generator",  # if router returns this
        False:       "clarify",        # if router returns this
        END:              END              # allow router to short-circuit to END if desired
        }
    )

    graph_builder.add_conditional_edges(
        "sql_generator",
        route_after_sql_generator,
        {
            True: "clarify",
            False: "postprocess",
            END:    END
        }
    )

    # 4) Chain your SQL path so it loops back into chatbot
    # graph_builder.add_edge("sql_generator", "postprocess")      # for SAP_HANA
    graph_builder.add_edge("postprocess",   END)
    graph_builder.add_edge("clarify",       END)


    return graph_builder.compile()
