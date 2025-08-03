# graph/state_schema.py


from typing import Optional, List, Any
from typing_extensions import TypedDict


class ChatState(TypedDict):
    prompt: str
    is_sql_prompt: bool
    data_source: str
    tables: List[str]
    message: str
    table_metadata: dict
    generated_sql: str
    result: str
    app_config: dict
    query_result: Any
    error: str
