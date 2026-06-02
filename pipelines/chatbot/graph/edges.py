from langgraph.graph import StateGraph, END
from pipelines.chatbot.graph.state import ChatState
from pipelines.chatbot.graph.nodes import validate_wiki_node, chat_node


def route_after_validate(state: ChatState) -> str:
    if state.get("status") == "abort":
        return END
    return "chat_node"


def build_chat_graph() -> StateGraph:
    workflow = StateGraph(ChatState)
    workflow.add_node("validate_wiki_node", validate_wiki_node)
    workflow.add_node("chat_node", chat_node)
    workflow.set_entry_point("validate_wiki_node")
    workflow.add_conditional_edges("validate_wiki_node", route_after_validate)
    workflow.add_edge("chat_node", END)
    return workflow.compile()
