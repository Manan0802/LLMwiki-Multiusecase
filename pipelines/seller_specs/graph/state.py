from typing import TypedDict

class FlowState(TypedDict, total=False):
    mcat_id: str
    mcat_name: str
    wiki_path: str
    wiki_content: str
    wiki_index: str          # contents of wiki/index.md for category awareness
    wiki_references: str     # contents of references.md for source check
    final_specs: dict
    status: str
