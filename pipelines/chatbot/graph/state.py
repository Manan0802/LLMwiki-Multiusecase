from typing import TypedDict, List


class ChatMessage(TypedDict):
    role: str
    content: str


class ChatState(TypedDict, total=False):
    mcat_name: str
    wiki_content: str
    wiki_index: str
    wiki_references: str
    conversation: List[ChatMessage]
    user_message: str
    assistant_reply: str
    status: str
