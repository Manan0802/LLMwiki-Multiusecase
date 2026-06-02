"""
graph/nodes.py — LangGraph node functions for the Spec-Creation Agent.

Flow:
  validate_wiki_node  →  create_specs_node
"""
import logging
import json
from pathlib import Path
from utils.llm import call_llm
from config import WIKI_DIR, SELLER_SPECS_OUTPUT_DIR, RAW_THINKING_DIR, SKILLS_DIR, USE_THINKING, MODEL
from pipelines.seller_specs.graph.state import FlowState

logger = logging.getLogger(__name__)


def sanitize_filename(item_name: str) -> str:
    """Convert a category name to a safe wiki filename slug."""
    safe = item_name.lower().strip().replace(" ", "_").replace("/", "_")
    return "".join(c for c in safe if c.isalnum() or c == "_")


# ──────────────────────────────────────────────────────────────────────────────
# Node 1: Validate Wiki Exists
# ──────────────────────────────────────────────────────────────────────────────

def validate_wiki_node(state: FlowState) -> dict:
    """Check if a wiki page exists for this category in wiki/items/.

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
        "wiki_path": str(wiki_path),
        "wiki_content": wiki_content,
        "wiki_index": wiki_index,
        "wiki_references": wiki_references,
        "status": "wiki_found"
    }


# ──────────────────────────────────────────────────────────────────────────────
# Node 2: Create / Audit Specs via LLM (Thinking ON)
# ──────────────────────────────────────────────────────────────────────────────

def create_specs_node(state: FlowState) -> dict:
    """Send pure wiki knowledge + agent prompts to Gemini 2.5 Pro.

    The LLM receives:
      - The agent prompt (agent_prompt_FINAL.md)
      - The skill rulebook (spec_creation_FINAL.md)
      - The full wiki content, index, and references (ground truth)
      
    No platform seller specs are passed. The agent builds from scratch.

    Output is saved to specs_output/{mcat_id}_final_specs.json
    Raw thinking is saved to raw_thinking/{mcat_id}_thinking.json
    """
    mcat_id = state["mcat_id"]
    mcat_name = state["mcat_name"]
    wiki_content = state["wiki_content"]
    wiki_index = state.get("wiki_index", "")
    wiki_references = state.get("wiki_references", "")
    slug = sanitize_filename(mcat_name)

    # ── Load skill prompts ───────────────────────────────────────────────────
    agent_prompt_path = SKILLS_DIR / "seller_specs" / "agent_prompt_spec-creation.md"
    agent_prompt = agent_prompt_path.read_text(encoding="utf-8")
    
    spec_skill_path = SKILLS_DIR / "seller_specs" / "spec_creation.md"
    spec_skill = spec_skill_path.read_text(encoding="utf-8")

    # ── Build system prompt ──────────────────────────────────────────────────
    system_prompt = f"{agent_prompt}\n\n---\n\n# Input 1: spec_creation.md\n\n{spec_skill}"

    # ── Build user prompt ────────────────────────────────────────────────────
    user_prompt_parts = [
        f"You are operating on the category: **{mcat_name}** (MCAT {mcat_id}).\n",
        "# Input 2: Product Knowledge (output/ folder)\n",
        f"--- [ FILE: output/output_{slug}/index.md ] ---",
        wiki_index if wiki_index else "(No index available)\n",
        f"\n--- [ FILE: output/output_{slug}/{slug}.md ] ---",
        wiki_content,
        f"\n--- [ FILE: output/output_{slug}/references.md ] ---",
        wiki_references if wiki_references else "(No references available)\n",
        "\nAll files loaded. Now begin evaluating your OPERATING PROCEDURE STEP BY STEP."
    ]
    user_prompt = "\n".join(user_prompt_parts)

    dump_path = RAW_THINKING_DIR / f"{mcat_id}_thinking.json"

    logger.info(f"🧠 Generating Specs via {MODEL} (Thinking {'ON' if USE_THINKING else 'OFF'}) …")
    final_output_str = call_llm(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        dump_raw_response_path=dump_path,
        enable_thinking=USE_THINKING
    )

    # ── Clean markdown fences if LLM wraps output ────────────────────────────
    final_output_str = final_output_str.strip()
    
    # Try looking for a JSON block explicitly if the LLM outputted thought process in markdown
    if "```json" in final_output_str:
        try:
            final_output_str = final_output_str.split("```json")[-1].split("```")[0].strip()
        except Exception:
            pass
    elif final_output_str.startswith("{") == False:
        # LLM might have output text then json, find the first { and last }
        start_idx = final_output_str.find("{")
        end_idx = final_output_str.rfind("}")
        if start_idx != -1 and end_idx != -1:
            final_output_str = final_output_str[start_idx:end_idx+1]

    # ── Parse & save ─────────────────────────────────────────────────────────
    try:
        final_specs_dict = json.loads(final_output_str)
    except json.JSONDecodeError as exc:
        # Save the raw output for debugging even if parsing fails
        err_file = SELLER_SPECS_OUTPUT_DIR / f"{mcat_id}_raw_output.txt"
        err_file.write_text(final_output_str, encoding="utf-8")
        logger.error("❌ Failed to parse LLM output as JSON. Raw saved → %s", err_file.name)
        raise RuntimeError(f"LLM output is not valid JSON. See {err_file.name}") from exc

    out_file = SELLER_SPECS_OUTPUT_DIR / f"{mcat_id}_final_specs.json"
    out_file.write_text(
        json.dumps(final_specs_dict, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )
    logger.info("✅ Final specs saved → %s", out_file.name)

    return {"final_specs": final_specs_dict, "status": "complete"}
