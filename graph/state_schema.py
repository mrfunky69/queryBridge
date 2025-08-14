# graph/state_schema.py
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages


class State(TypedDict):
    messages: Annotated[list, add_messages]
    sql:        str         # filled by sql_generator
    raw_table:  dict        # filled by hana_query
    needs_clarification: bool
    app_config: dict

