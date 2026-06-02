import logging
from config import WIKI_DIR, RAW_THINKING_DIR, SKILLS_DIR, USE_THINKING
from utils.llm import call_llm
from pipelines.chatbot.graph.state import ChatState

logger = logging.getLogger(__name__)


def sanitize_filename(item_name: str) -> str:
    """Convert a category name to a safe wiki filename slug."""
    safe = item_name.lower().strip().replace(" ", "_").replace("/", "_")
    return "".join(c for c in safe if c.isalnum() or c == "_")


def validate_wiki_node(state: ChatState) -> dict:
    """Check if a wiki page exists for this category.
    If found → loads the wiki content, index, and references into state.
    If not   → sets status='abort' and the graph stops.
    """
    mcat_name = state["mcat_name"]
    slug = sanitize_filename(mcat_name)
    mcat_output_dir = WIKI_DIR / f"output_{slug}"
    wiki_path = mcat_output_dir / f"{slug}.md"

    if not wiki_path.exists():
        logger.warning("❌ Wiki does NOT exist at %s — aborting.", wiki_path)
        return {"status": "abort"}

    logger.info("✅ Wiki found → %s", wiki_path)

    # Read wiki content
    wiki_content = wiki_path.read_text(encoding="utf-8")

    # Read wiki index so the LLM knows what sections / categories exist
    index_path = mcat_output_dir / "index.md"
    wiki_index = ""
    if index_path.exists():
        wiki_index = index_path.read_text(encoding="utf-8")
        logger.info("📑 Wiki index loaded (%d chars)", len(wiki_index))

    # Read wiki references
    ref_path = mcat_output_dir / "references.md"
    wiki_references = ""
    if ref_path.exists():
        wiki_references = ref_path.read_text(encoding="utf-8")
        logger.info("📑 Wiki references loaded (%d chars)", len(wiki_references))

    return {
        "wiki_content": wiki_content,
        "wiki_index": wiki_index,
        "wiki_references": wiki_references,
        "conversation": [],
        "status": "ready"
    }


def chat_node(state: ChatState) -> dict:
    """Answer the user's query purely based on the loaded wiki files."""
    mcat_name = state["mcat_name"]
    wiki_content = state["wiki_content"]
    wiki_index = state.get("wiki_index", "")
    wiki_references = state.get("wiki_references", "")
    slug = sanitize_filename(mcat_name)
    
    user_message = state["user_message"]
    conversation = state.get("conversation", [])

    # ── Load chat system prompt ──────────────────────────────────────────────
    system_prompt_path = SKILLS_DIR / "chatbot" / "chat_prompt.md"
    system_prompt = system_prompt_path.read_text(encoding="utf-8")

    # ── Build user prompt ────────────────────────────────────────────────────
    user_prompt_parts = [
        f"You are operating on the category: **{mcat_name}**.\n",
        "# Input 2: Product Knowledge (output/ folder)\n",
        f"--- [ FILE: output/output_{slug}/index.md ] ---",
        wiki_index if wiki_index else "(No index available)\n",
        f"\n--- [ FILE: output/output_{slug}/{slug}.md ] ---",
        wiki_content,
        f"\n--- [ FILE: output/output_{slug}/references.md ] ---",
        wiki_references if wiki_references else "(No references available)\n",
        "\nAll files loaded. Now answer the user's question using ONLY this information.",
        "If the answer is not in the knowledge base, say: \"I don't have enough information about that in my knowledge base.\"",
        f"\nUSER QUESTION: {user_message}"
    ]
    full_user_prompt = "\n".join(user_prompt_parts)

    logger.info("💬 Sending query to LLM...")

    reply = call_llm(
        system_prompt=system_prompt,
        user_prompt=full_user_prompt,
        conversation_history=conversation,
        enable_thinking=False
    )

    # ── Update conversation history ──────────────────────────────────────────
    updated_conversation = list(conversation) + [
        {"role": "user", "content": user_message},
        {"role": "assistant", "content": reply},
    ]

    return {
        "assistant_reply": reply,
        "conversation": updated_conversation
    }
