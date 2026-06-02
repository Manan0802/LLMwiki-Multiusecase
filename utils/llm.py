"""
llm.py — Thin wrapper around the custom LLM gateway.

Uses raw ``requests.post`` (NOT any LangChain LLM wrapper).
Includes robust retry logic for network and timeout errors.
All configuration is pulled from ``config.py``.

Supports Gemini 2.5 Pro **thinking mode** — the raw thinking content
is extracted separately and saved alongside the final answer.
"""
import time
import json
import logging
import requests
from pathlib import Path
from requests.exceptions import RequestException

from config import API_URL, API_KEY, MODEL, MAX_TOKENS

logger = logging.getLogger(__name__)


def call_llm(
    system_prompt: str,
    user_prompt: str,
    max_retries: int = 4,
    retry_delay: int = 30,
    override_model: str = None,
    dump_raw_response_path: Path = None,
    enable_thinking: bool = False,
    conversation_history: list = None,
) -> str:
    """Send a chat-completion request to the LLM gateway and return the
    assistant's response text.

    Parameters
    ----------
    conversation_history : list of {role, content} dicts
        Prior conversation turns. When provided, these are prepended before the
        current user_prompt so the LLM has full multi-turn context.
        Leave as None for single-turn calls.
    enable_thinking : bool
        When True, adds ``thinking: {type: "enabled", budget_tokens: 10000}``
        to the payload so Gemini 2.5 Pro returns its reasoning chain.

    Raises
    ------
    RuntimeError
        If the HTTP request fails after all retries or the response is malformed.
    ValueError
        If the API key is not configured.
    """
    if not API_KEY:
        raise ValueError(
            "LLM_GATEWAY_API_KEY is not set.  "
            "Add it to your .env file or environment."
        )

    active_model = override_model or MODEL

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}",
    }

    # ── Build message list ────────────────────────────────────────────────────
    messages = [{"role": "system", "content": system_prompt}]
    if conversation_history:
        messages.extend(conversation_history)
    messages.append({"role": "user", "content": user_prompt})

    payload = {
        "model": active_model,
        "temperature": 0,
        "messages": messages,
        "max_tokens": MAX_TOKENS,
    }

    # ── Enable thinking for Gemini 2.5 Pro ───────────────────────────────
    if enable_thinking:
        payload["thinking"] = {
            "type": "enabled",
            "budget_tokens": 10000
        }

    logger.debug(
        "LLM request → model=%s  system_len=%d  user_len=%d  thinking=%s",
        active_model,
        len(system_prompt),
        len(user_prompt),
        enable_thinking,
    )

    for attempt in range(1, max_retries + 1):
        try:
            response = requests.post(
                API_URL,
                headers=headers,
                json=payload,
                timeout=180,
            )
            response.raise_for_status()

            data = response.json()

            # ── Extract final answer ─────────────────────────────────────
            content = data["choices"][0]["message"]["content"]

            # ── Dump full raw response (includes thinking if present) ────
            if dump_raw_response_path:
                dump_raw_response_path.parent.mkdir(parents=True, exist_ok=True)
                dump_raw_response_path.write_text(
                    json.dumps(data, indent=2, ensure_ascii=False),
                    encoding="utf-8"
                )
                logger.info(
                    "📝 Raw LLM response (thinking + answer) saved → %s",
                    dump_raw_response_path.name
                )

            logger.debug("LLM response ← %d chars", len(content))
            return content

        except RequestException as exc:
            if attempt < max_retries:
                logger.warning(
                    "⚠️ LLM request failed (attempt %d/%d): %s. Retrying in %ds…",
                    attempt, max_retries, exc, retry_delay
                )
                time.sleep(retry_delay)
            else:
                logger.error(
                    "❌ LLM gateway request failed after %d attempts: %s",
                    max_retries, exc
                )
                raise RuntimeError(
                    f"LLM gateway request failed after {max_retries} attempts: {exc}"
                ) from exc

        except (KeyError, IndexError) as exc:
            try:
                raw_data = response.json()
            except Exception:
                raw_data = response.text

            logger.error("Unexpected LLM response shape: %s", raw_data)
            raise RuntimeError(
                f"Malformed LLM response — missing choices[0].message.content: {raw_data}"
            ) from exc
