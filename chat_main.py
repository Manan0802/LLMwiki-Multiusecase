"""
chat_main.py — Entry point for the Wiki Chatbot (Use Case 2).

Usage:
    python chat_main.py
    python chat_main.py --mcat-name "AAC Blocks"

The chatbot keeps a full conversation history so you can ask follow-up
questions. Type 'exit' or 'quit' to end the session.
"""
import argparse
import logging
from pipelines.chatbot.graph.edges import build_chat_graph

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description="Wiki Chatbot")
    parser.add_argument("--mcat-name", required=False, help="MCAT name of the category (e.g. 'AAC Blocks')")
    args = parser.parse_args()

    mcat_name = args.mcat_name or input("Enter Category Name : ").strip()
    if not mcat_name:
        logger.error("❌ Category name is required.")
        return

    logger.info("📚 [Wiki Chat] Loading wiki for '%s'…", mcat_name)

    graph = build_chat_graph()

    # ── Load wiki once at session start ──────────────────────────────────────
    state = graph.invoke({"mcat_name": mcat_name, "user_message": "__init__"})

    if state.get("status") == "abort":
        logger.warning("⛔ Aborted — wiki not found for '%s'.", mcat_name)
        return

    print(f"\n{'─'*60}")
    print(f"  📚 Wiki Chat — {mcat_name}")
    print(f"  I will answer questions using ONLY the wiki for this category.")
    print(f"  Type 'exit' to quit.")
    print(f"{'─'*60}\n")

    # ── Conversation loop ─────────────────────────────────────────────────────
    conversation = []
    wiki_content = state.get("wiki_content", "")
    wiki_index = state.get("wiki_index", "")
    wiki_references = state.get("wiki_references", "")

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n👋 Goodbye!")
            break

        if user_input.lower() in ("exit", "quit", "bye"):
            print("👋 Goodbye!")
            break

        if not user_input:
            continue

        # Run the answer node with updated state
        result = graph.invoke({
            "mcat_name": mcat_name,
            "wiki_content": wiki_content,
            "wiki_index": wiki_index,
            "wiki_references": wiki_references,
            "user_message": user_input,
            "conversation": conversation,
            "status": "ready",
        })

        reply = result.get("assistant_reply", "(No reply)")
        conversation = result.get("conversation", conversation)

        print(f"\nAssistant: {reply}\n")


if __name__ == "__main__":
    main()
