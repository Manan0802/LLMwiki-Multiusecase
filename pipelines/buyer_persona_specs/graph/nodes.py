"""
buyer_persona_graph/nodes.py — LangGraph node functions for the Buyer Persona Spec-Creation Agent.

Flow:
  validate_wiki_node  →  create_specs_node
"""
import logging
import json
from pathlib import Path
from utils.llm import call_llm
from config import WIKI_DIR, BUYER_PERSONA_SPEC_OUTPUT_DIR, RAW_THINKING_DIR, SKILLS_DIR, USE_THINKING, MODEL
from pipelines.buyer_persona_specs.graph.state import BuyerPersonaFlowState

logger = logging.getLogger(__name__)


def sanitize_filename(item_name: str) -> str:
    """Convert a category name to a safe wiki filename slug."""
    safe = item_name.lower().strip().replace(" ", "_").replace("/", "_")
    return "".join(c for c in safe if c.isalnum() or c == "_")


# ──────────────────────────────────────────────────────────────────────────────
# Node 1: Validate Wiki Exists
# ──────────────────────────────────────────────────────────────────────────────

def validate_wiki_node(state: BuyerPersonaFlowState) -> dict:
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

def create_specs_node(state: BuyerPersonaFlowState) -> dict:
    """Send pure wiki knowledge + agent prompts to Gemini 2.5 Pro for Buyer Persona Specs.

    Output is saved to buyer_persona_spec_output/{mcat_id}_final_buyer_persona_specs.json
    Raw thinking is saved to raw_thinking/{mcat_id}_buyer_persona_thinking.json
    """
    mcat_id = state["mcat_id"]
    mcat_name = state["mcat_name"]
    wiki_content = state["wiki_content"]
    wiki_index = state.get("wiki_index", "")
    wiki_references = state.get("wiki_references", "")
    slug = sanitize_filename(mcat_name)

    # ── Load skill prompts ───────────────────────────────────────────────────
    agent_prompt_path = SKILLS_DIR / "buyer_persona_specs" / "agent_prompt_buyer_persona_spec-creation.md"
    agent_prompt = agent_prompt_path.read_text(encoding="utf-8")
    
    spec_skill_path = SKILLS_DIR / "buyer_persona_specs" / "buyer_persona_spec_creation_skill.md"
    spec_skill = spec_skill_path.read_text(encoding="utf-8")

    # ── Build system prompt ──────────────────────────────────────────────────
    system_prompt = f"{agent_prompt}\n\n---\n\n# Input 1: buyer_persona_spec_creation_skill.md\n\n{spec_skill}"

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

    dump_path = RAW_THINKING_DIR / f"{mcat_id}_buyer_persona_thinking.json"

    logger.info(f"🧠 Generating Buyer Persona Specs via {MODEL} (Thinking {'ON' if USE_THINKING else 'OFF'}) …")
    final_output_str = call_llm(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        dump_raw_response_path=dump_path,
        enable_thinking=USE_THINKING
    )

    # ── Clean markdown fences if LLM wraps output ────────────────────────────
    final_output_str = final_output_str.strip()
    
    if "```json" in final_output_str:
        try:
            final_output_str = final_output_str.split("```json")[-1].split("```")[0].strip()
        except Exception:
            pass
    elif "```python" in final_output_str:
        try:
            final_output_str = final_output_str.split("```python")[-1].split("```")[0].strip()
        except Exception:
            pass

    # ── Robustly extract JSON Array ──────────────────────────────────────────
    import ast
    final_specs_dict = None
    end_idx = final_output_str.rfind("]")
    
    if end_idx != -1:
        start_idx = final_output_str.find("[")
        while start_idx != -1 and start_idx < end_idx:
            substring = final_output_str[start_idx:end_idx+1]
            try:
                final_specs_dict = json.loads(substring)
                final_output_str = substring
                break
            except json.JSONDecodeError:
                try:
                    # Fallback for strict python lists
                    final_specs_dict = ast.literal_eval(substring)
                    if isinstance(final_specs_dict, list):
                        final_output_str = substring
                        break
                except (SyntaxError, ValueError):
                    pass
            start_idx = final_output_str.find("[", start_idx + 1)

    if final_specs_dict is None:
        # Fallback if the loop found nothing
        err_file = BUYER_PERSONA_SPEC_OUTPUT_DIR / f"{mcat_id}_buyer_persona_raw_output.txt"
        err_file.write_text(final_output_str, encoding="utf-8")
        logger.error("❌ Failed to parse LLM output as JSON/List. Raw saved → %s", err_file.name)
        raise RuntimeError(f"LLM output is not a valid list. See {err_file.name}")

    out_file = BUYER_PERSONA_SPEC_OUTPUT_DIR / f"{mcat_id}_final_buyer_persona_specs.json"
    out_file.write_text(
        json.dumps(final_specs_dict, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )
    logger.info("✅ Final buyer persona specs saved → %s", out_file.name)

    return {"final_specs": final_specs_dict, "status": "complete"}
