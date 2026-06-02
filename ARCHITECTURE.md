# Automated Spec-Creation Agent

This project automates the creation of high-quality, deterministic product specifications for an Indian B2B marketplace. It eliminates random AI hallucination by restricting the LLM to output structured parameters exclusively derived from curated Wikipedia-style product catalogs.

## 🌟 Project Overview

The **Spec-Creation Agent** translates human-readable, unstructured markdown wikis into rigorous, JSON-formatted product filters (Primary, Secondary, and Tertiary specs). These outputs are primarily used for:
1. **Seller Front-Ends**: Defining the forms sellers use to list their products.
2. **Buyer Discovery**: Defining the exact filters buyers use to narrow down search results.

Instead of writing custom spec creation rules dynamically, the project strictly uses a unified **Zero-Shot Chain-of-Thought (CoT)** reasoning mechanism to mechanically force the LLM to justify its choices based on literal quotes from a local `wiki/` directory before generating actual JSON outputs.

## 🛠️ Technology Stack

| Component | Technology / Library | Description |
|-----------|----------------------|-------------|
| **Core Language** | Python 3 | Main scripting and backend logic. |
| **Agent Framework**| LangGraph | Orchestrates stateful, multi-node AI workflows and decision pipelines. |
| **Language Model** | Gemini 2.5 Pro | Advanced reasoning LLM configured with `temperature: 0` for completely deterministic output. |
| **Data Storage** | Local File System (`.md`, `.json`) | Markdown for knowledge sources (prompts/wiki) and JSON for generated specs/raw output parsing. |
| **Configuration** | `python-dotenv` | Loads environment configurations like API tokens and thinking-mode toggles. |

---

## 🏗️ Architecture Flow

The system runs a fully disconnected and deterministic pipeline, orchestrating data injection purely through local Markdown.

```mermaid
graph TD
    classDef startEnd fill:#f9f,stroke:#333,stroke-width:2px;
    classDef llmNode fill:#bfb,stroke:#333,stroke-width:2px;
    classDef inputNode fill:#bbf,stroke:#333,stroke-width:1px;
    classDef outputNode fill:#fbb,stroke:#333,stroke-width:1px;

    User([👤 User Trigger: CLI / Script]) --> StateInitializer((Initialize FlowState))
    
    subgraph Data Sources
        W_Index[📝 wiki/index.md]:::inputNode
        W_Item[📖 wiki/items/category.md]:::inputNode
        W_Ref[📜 wiki/references/ref.md]:::inputNode
    end
    
    subgraph LangGraph Orchestration
        StateInitializer --> ValidateWikiNode[🔎 validate_wiki_node]
        ValidateWikiNode -- If Not Found --> Abort([❌ Abort]):::startEnd
        
        ValidateWikiNode -- "Loads Wiki Files" --> CreateSpecsNode[🧠 create_specs_node]:::llmNode
    end
    
    subgraph Instruction Rules
        Skill1[📜 skills/agent_prompt.md <br> Agent Instructions]:::inputNode
        Skill2[📜 skills/spec_creation.md <br> Schema & Hard Constraints]:::inputNode
    end
    
    Data Sources -. Inject into Prompt .-> CreateSpecsNode
    Instruction Rules -. Inject into Prompt .-> CreateSpecsNode
    
    CreateSpecsNode -- "HTTP POST (Temp = 0)" --> Gemini[🤖 Google Gemini]
    
    Gemini -- "Raw Thought Execution" --> RawThinking[📂 raw_thinking/mcat_thinking.json]:::outputNode
    Gemini -- "Clean Extracted Specs" --> FinalJSON[📂 specs_output/mcat_final_specs.json]:::outputNode
```

### ⚙️ Node Breakdown
1. **`validate_wiki_node`**: Rapidly validates that the `mcat_name` has a matching Wikipedia file inside the `wiki/items/` folder. It aggressively fails and aborts to prevent empty LLM runs, avoiding API waste. If valid, it pulls the `index.md`, item `wiki.md`, and `references.md` into the active LangGraph `FlowState`.
2. **`create_specs_node`**: Takes the `FlowState` and assembles an intricate User Prompt and System Prompt. It injects the `agent_prompt.md` and `spec_creation.md` logic rules alongside the pulled knowledge block. It initiates an HTTP POST request to the LLM Gateway with `enable_thinking=True` and `temperature=0`.

## 🛡️ Anti-Hallucination & Determinism

This project achieves highly deterministic runs (~85%-90% consistency across executions) by utilizing specific prompt engineering constraints:

- **Hard Rule Enforcements**: The agent is strictly commanded to use spec labels identical to those mentioned in the wiki language. No re-phrasing.
- **Enforced Self-Audits**: The LLM output MUST contain a checklist stage internally (using explicit string matches like `[PASS / FAIL]`) where the AI audits its own JSON schema draft before physically building it.
- **Zero Temperature Payload**: The LLM API is explicitly throttled at `temperature: 0`, completely removing probabilistic variance and making the final output mathematically sequential.
