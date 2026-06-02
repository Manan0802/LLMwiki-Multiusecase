from typing import TypedDict


class BuyerPersonaFlowState(TypedDict, total=False):
    mcat_id: str
    mcat_name: str
    wiki_path: str
    wiki_content: str
    wiki_index: str          # contents of wiki/index/<slug>_index.md
    wiki_references: str     # contents of references_<slug>.md
    final_specs: dict
    status: str
