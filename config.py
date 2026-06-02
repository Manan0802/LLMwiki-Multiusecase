import os
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).parent.resolve()
load_dotenv(PROJECT_ROOT / ".env")

# ── LLM Gateway ─────────────────────────────────────────────────────────────
API_URL    = os.getenv("LLM_GATEWAY_URL", "https://imllm.intermesh.net/v1/chat/completions")
API_KEY    = os.getenv("LLM_GATEWAY_API_KEY")
MODEL      = os.getenv("LLM_MODEL", "google/gemini-2.5-pro")
MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "16000"))
USE_THINKING = os.getenv("LLM_USE_THINKING", "true").lower() == "true"

# ── Platform API ─────────────────────────────────────────────────────────────
PRESIGNED_URL_API = os.getenv(
    "PRESIGNED_URL_API",
    "https://get-presigned-url-for-mcat-w2yrp7i6za-el.a.run.app/"
)

# ── Paths ────────────────────────────────────────────────────────────────────
WIKI_DIR       = PROJECT_ROOT / "output"

SELLER_SPECS_OUTPUT_DIR = PROJECT_ROOT / "seller_specs_output"
BUYER_PERSONA_SPEC_OUTPUT_DIR   = PROJECT_ROOT / "buyer_persona_spec_output"
RAW_THINKING_DIR        = PROJECT_ROOT / "raw_thinking"
SKILLS_DIR              = PROJECT_ROOT / "skills"

SELLER_SPECS_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
BUYER_PERSONA_SPEC_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
RAW_THINKING_DIR.mkdir(parents=True, exist_ok=True)
