from langgraph.graph import StateGraph, END
from pipelines.buyer_persona_specs.graph.state import BuyerPersonaFlowState
from pipelines.buyer_persona_specs.graph.nodes import validate_wiki_node, create_specs_node


def route_after_validate(state: BuyerPersonaFlowState) -> str:
    if state.get("status") == "abort":
        return END
    return "create_specs_node"


def build_buyer_persona_graph() -> StateGraph:
    workflow = StateGraph(BuyerPersonaFlowState)
    workflow.add_node("validate_wiki_node", validate_wiki_node)
    workflow.add_node("create_specs_node", create_specs_node)
    workflow.set_entry_point("validate_wiki_node")
    workflow.add_conditional_edges("validate_wiki_node", route_after_validate)
    workflow.add_edge("create_specs_node", END)
    return workflow.compile()
