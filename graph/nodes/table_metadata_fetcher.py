# graph/nodes/table_metadata_fetcher.py

from metadata.table_registry import get_metadata_source_tables

def table_metadata_fetcher(state) :
    print("🧠 node table_metadata_fetcher ", state)
    source = state.get("data_source")
    all_metadata = {}
    if source is not None:
        all_metadata = get_metadata_source_tables(source)
    state["table_metadata"] = all_metadata
    return state
