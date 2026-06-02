from langgraph.graph import StateGraph, END
from pipelines.seller_specs.graph.state import FlowState
from pipelines.seller_specs.graph.nodes import validate_wiki_node, create_specs_node

def route_after_validate(state: FlowState) -> str:
    if state.get("status") == "abort":
        return END
    return "create_specs_node"

def build_graph() -> StateGraph:
    workflow = StateGraph(FlowState)
    workflow.add_node("validate_wiki_node", validate_wiki_node)
    workflow.add_node("create_specs_node", create_specs_node)
    workflow.set_entry_point("validate_wiki_node")
    workflow.add_conditional_edges("validate_wiki_node", route_after_validate)
    workflow.add_edge("create_specs_node", END)
    return workflow.compile()
