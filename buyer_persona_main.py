"""
buyer_persona_main.py — Entry point for the Buyer Persona Spec-Creation Agent (Use Case 3).

Usage:
    python buyer_persona_main.py
      → prompts for mcat_id and mcat_name interactively

    python buyer_persona_main.py --mcat-id 68865 --mcat-name "AAC Block"
      → CLI mode (no prompts)
"""
import argparse
import logging
from pipelines.buyer_persona_specs.graph.edges import build_buyer_persona_graph

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description="Buyer Persona Spec-Creation Agent")
    parser.add_argument("--mcat-id", required=False, help="MCAT ID of the category")
    parser.add_argument("--mcat-name", required=False, help="MCAT name of the category")
    args = parser.parse_args()

    # ── Interactive fallback if CLI args not provided ────────────────────────
    mcat_id = args.mcat_id
    mcat_name = args.mcat_name

    if not mcat_id:
        mcat_id = input("Enter MCAT ID: ").strip()
    if not mcat_name:
        mcat_name = input("Enter MCAT Name: ").strip()

    if not mcat_id or not mcat_name:
        logger.error("❌ Both MCAT ID and MCAT Name are required. Exiting.")
        return

    logger.info("🚀 Starting Buyer Persona Spec-Creation Agent for %s (MCAT %s)", mcat_name, mcat_id)

    graph = build_buyer_persona_graph()
    initial = {"mcat_id": mcat_id, "mcat_name": mcat_name}
    result = graph.invoke(initial)

    status = result.get("status", "unknown")
    if status == "abort":
        logger.warning("⛔ Agent aborted — wiki not found for '%s'. No specs created.", mcat_name)
    elif status == "complete":
        logger.info("✅ Agent finished successfully! Final buyer persona specs saved to buyer_persona_spec_output/")
    else:
        logger.info("Agent finished with status: %s", status)


if __name__ == "__main__":
    main()
