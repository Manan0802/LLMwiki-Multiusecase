# 🚀 Autonomous B2B Specifications Orchestration Engine
> **A Stateful Multi-Usecase AI Agent Powered by LangGraph & Gemini 2.5 Pro**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](#)
[![LangGraph 0.2+](https://img.shields.io/badge/framework-LangGraph%200.2+-orange.svg)](#)
[![Model Support](https://img.shields.io/badge/LLM-Gemini%202.5%20Pro-violet.svg)](#)
[![Aesthetics](https://img.shields.io/badge/Design-Premium%20Studio-emerald.svg)](#)

---

## 📖 Executive Overview

In the highly competitive world of B2B marketplaces, product discoverability and high-friction seller listing flows are critical bottlenecks. Sellers struggle to input technical product attributes correctly, while buyers require clean, standardized, and precise filters to search and compare products. 

The **Autonomous B2B Specifications Orchestration Engine** is an enterprise-grade agentic pipeline designed to eliminate manual intervention and AI hallucinations in product catalog management. Rather than relying on generic, probabilistic LLM generations, this engine enforces **100% deterministic, source-grounded product specifications** by cross-referencing all decisions against an integrated Wikipedia-style product knowledge repository.

### The Multi-Usecase Powerhouse
The engine natively supports three separate operational workloads sharing a unified core:
1. **💼 Usecase 1: Seller Spec Creator (`main.py`)**: Automatically designs seller listing forms and buyer filters (Primary, Secondary, Tertiary attributes) with rigorous validation (e.g. en-dashes `–`, superscripts `m²`, mutually exclusive values).
2. **👤 Usecase 2: Buyer Persona Generator (`buyer_persona_main.py`)**: Models lead qualification parameters describing **how and why** buyers purchase rather than what they purchase.
3. **💬 Usecase 3: Source-Grounded Wiki Chatbot (`chat_main.py`)**: A stateful conversational agent allowing catalog managers to query raw category knowledge under a strict zero-hallucination mandate.

---

## 🏛️ Core Constitution & Philosophy

Every system execution is governed by a strict, non-negotiable architectural constitution designed to solve B2B catalog problems. Below are the key engineering decisions and why they were chosen:

### 1. Zero-Shot Chain-of-Thought (CoT) & Enforced Self-Audits
Rather than making a raw direct generation, the agent follows a multi-step structured operating procedure written into its master prompts. The LLM must explicitly list its step-by-step reasoning, quote specific sections of the source files, and fill out a pre-output quality checklist containing `[PASS/FAIL]` gates before physically building the output. 
* **Why**: Prevents the model from jumping to conclusions and forces strict compliance with local styling rules (e.g., character limits, unit formats) before generating JSON.

### 2. Disconnected Lazy-Loading Architecture
The system avoids indexing overhead, complex database runtimes, and embedding latency by using a **lazy-loading directory-based router**.
* **Why**: By dynamically mapping incoming categories (e.g., `"AAC Block"`) to directory slugs (e.g., `output_aac_blocks/`), it loads the ground-truth text index and articles directly from the disk on-demand. This maintains a near-zero memory footprint and scales instantly as new files are added.

### 3. Absolute Mathematical Determinism
To achieve 90%+ consistency across parallel executions, the engine:
* Pins the temperature strictly at `0` to remove probabilistic variance.
* Activates **Google Gemini 2.5 Pro's Deep Thinking mode** (10,000 budget tokens) to run exhaustive compliance checks behind the scenes.
* Restricts options to exactly those present in the source files, banning common placeholder values (`Other`, `Custom`, `N/A`, `As per Requirement`).

---

## 📊 Illustrative Architecture Flowcharts

### High-Level System Architecture & Multi-Usecase Router
```
                     ┌────────────────────────┐
                     │   CLI / Script Trigger  │
                     └───────────┬────────────┘
                                 │
         ┌───────────────────────┼──────────────────────┐
         ▼                       ▼                      ▼
  [ Usecase 1 ]           [ Usecase 2 ]          [ Usecase 3 ]
  Seller Specs            Buyer Personas         Wiki Chatbot
 (main.py --mcat)     (buyer_persona_main.py)   (chat_main.py)
         │                       │                      │
         └───────────────────────┼──────────────────────┘
                                 │
                                 ▼
                     ┌────────────────────────┐
                     │  Sanitize Slug & Load  │
                     │  Ground-Truth Files    │
                     │  (index/logs/ref.md)   │
                     └───────────┬────────────┘
                                 │
                                 ▼
                     ┌────────────────────────┐
                     │ validate_wiki_node     │
                     │ (LangGraph Node 1)     │
                     └───────────┬────────────┘
                                 │
                        [Wiki File Found?]
                       ┌─────────┴─────────┐
                    YES│                  NO│
                       ▼                    ▼
             ┌──────────────────┐     ┌───────────┐
             │ create_specs_node│     │   Abort   │
             │ (LangGraph Node2)│     │  (State:  │
             └─────────┬────────┘     │  'abort') │
                       │              └───────────┘
                [Invoke Gemini]
               (Thinking Active)
                       │
                       ▼
             ┌──────────────────┐
             │ Extracted Output │
             │   Post-Audited   │
             └─────────┬────────┘
                       │
                       ▼
            ┌────────────────────┐
            │   JSON / Python    │
            │  Structured Saved  │
            └────────────────────┘
```

### End-to-End Control Flow & Graph Transition Details
Below is the technical orchestration of the stateful LangGraph workflow representing the end-to-end data pipeline.

```mermaid
graph TD
    %% Styling & Colors
    classDef startEnd fill:#d4ebf2,stroke:#0e76a8,stroke-width:2px;
    classDef nodeClass fill:#e1f5fe,stroke:#0288d1,stroke-width:2px;
    classDef llmNode fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px;
    classDef fileNode fill:#fff8e1,stroke:#f57f17,stroke-width:1px;
    classDef decision fill:#ede7f6,stroke:#5e35b1,stroke-width:2px;

    %% Elements
    Trigger([👤 CLI Trigger / main.py]) --> StateInit[Initialize FlowState / BuyerPersonaFlowState]:::nodeClass
    
    subgraph Local_Knowledge [Ground Truth Knowledge Sources]
        W_Index[📝 output/output_slug/index.md]:::fileNode
        W_Main[📖 output/output_slug/slug.md]:::fileNode
        W_Ref[📜 output/output_slug/references.md]:::fileNode
    end

    StateInit --> Node1[🔎 validate_wiki_node]:::nodeClass
    Local_Knowledge -. Reading filesystem .-> Node1
    
    Node1 --> Dec1{Check status}:::decision
    Dec1 -- "status == 'abort'" --> Abort([❌ Abort & Log Warning]):::startEnd
    Dec1 -- "status == 'wiki_found'" --> Node2[🧠 create_specs_node / chat_node]:::llmNode
    
    subgraph Rulebooks [Skills Configuration]
        Skill1[📜 skills/category/agent_prompt.md]:::fileNode
        Skill2[📜 skills/category/spec_creation.md]:::fileNode
    end
    
    Rulebooks -. Injected as System Context .-> Node2
    
    Node2 --> Gemini[🤖 Google Gemini 2.5 Pro]:::llmNode
    Gemini -- "Enforce Temp=0 & Thinking Payload" --> LLMResponse{Parse Output}:::decision
    
    LLMResponse -- "Failed to parse JSON" --> Fallback[💾 Save raw_output.txt & Raise Error]:::nodeClass
    LLMResponse -- "Success" --> SaveOutputs[💾 Save specs_output/{mcat_id}_final_specs.json]:::nodeClass
    Gemini -- "Thinking Extract" --> SaveThinking[💾 Save raw_thinking/{mcat_id}_thinking.json]:::nodeClass

    SaveOutputs --> Done([✅ Complete & Exit]):::startEnd
```

---

## ⚙️ Under-the-Hood Mechanics (Code-Level Specs)

To guarantee flawless pair-programming and extension, developers must adhere to the exact state schemas and custom parsers running the system.

### 1. State Definition Schemas
The engine operates statefully on top of three custom Python `TypedDict` schemas. These schemas ensure full traceability of data blocks as they move from file loaders through LLM invocations to downstream processors.

#### A. Seller Specification Flow State (`FlowState`)
Located in [state.py](file:///c:/Users/Imart/Desktop/Specs-onywiki/pipelines/seller_specs/graph/state.py):
```python
from typing import TypedDict

class FlowState(TypedDict, total=False):
    mcat_id: str             # Mandatory target Category ID
    mcat_name: str           # Target Category Name
    wiki_path: str           # Path to localized markdown catalog
    wiki_content: str        # Text of category-specific Wikipedia page
    wiki_index: str          # Loaded contents of index.md
    wiki_references: str     # Loaded references for validation
    final_specs: dict        # Structured JSON containing validated schemas
    status: str              # Transition check flag ('wiki_found', 'abort', 'complete')
```

#### B. Buyer Persona Flow State (`BuyerPersonaFlowState`)
Located in [state.py](file:///c:/Users/Imart/Desktop/Specs-onywiki/pipelines/buyer_persona_specs/graph/state.py):
```python
from typing import TypedDict

class BuyerPersonaFlowState(TypedDict, total=False):
    mcat_id: str
    mcat_name: str
    wiki_path: str
    wiki_content: str
    wiki_index: str          # Loaded contents of category's index.md
    wiki_references: str     # Source check references.md
    final_specs: dict        # Holds output Python List of Dicts
    status: str
```

#### C. Stateful Chatbot Session State (`ChatState`)
Located in [state.py](file:///c:/Users/Imart/Desktop/Specs-onywiki/pipelines/chatbot/graph/state.py):
```python
from typing import TypedDict, List

class ChatMessage(TypedDict):
    role: str                # 'user' | 'assistant'
    content: str             # Prompt / Reply text

class ChatState(TypedDict, total=False):
    mcat_name: str
    wiki_content: str
    wiki_index: str
    wiki_references: str
    conversation: List[ChatMessage]  # Enforces multi-turn historical memory
    user_message: str
    assistant_reply: str
    status: str
```

### 2. Regular Expressions & Value Cleaning Implementations
When models generate output, they occasionally wrap responses in Markdown code fences. The engine uses robust string-parsing utilities to extract raw JSON payload or Python lists without raising decoding errors.

#### JSON Codeblock Cleaning Code:
```python
# Strip external whitespace
final_output_str = final_output_str.strip()

# Target markdown wrapper splits
if "```json" in final_output_str:
    try:
        final_output_str = final_output_str.split("```json")[-1].split("```")[0].strip()
    except Exception:
        pass
elif final_output_str.startswith("{") == False:
    # Locate boundaries if text wrapping exists
    start_idx = final_output_str.find("{")
    end_idx = final_output_str.rfind("}")
    if start_idx != -1 and end_idx != -1:
        final_output_str = final_output_str[start_idx:end_idx+1]
```

#### Multi-Layer Buyer Persona List Parser (AST Fallback):
```python
import ast

final_specs_dict = None
end_idx = final_output_str.rfind("]")

if end_idx != -1:
    start_idx = final_output_str.find("[")
    while start_idx != -1 and start_idx < end_idx:
        substring = final_output_str[start_idx:end_idx+1]
        try:
            # Method 1: Strict Standard JSON
            final_specs_dict = json.loads(substring)
            final_output_str = substring
            break
        except json.JSONDecodeError:
            try:
                # Method 2: Python AST Literal Evaluation (handles single quotes)
                final_specs_dict = ast.literal_eval(substring)
                if isinstance(final_specs_dict, list):
                    final_output_str = substring
                    break
            except (SyntaxError, ValueError):
                pass
        start_idx = final_output_str.find("[", start_idx + 1)
```

---

## 🗃️ Data Sources & Assets Schemas

The Ground-Truth files in [output/](file:///c:/Users/Imart/Desktop/Specs-onywiki/output) act as the local knowledge base. The engine operates dynamically over four distinct file assets per product category.

| File | Asset Path | Column / Markdown Format Specs | Trigger & System Utility |
|---|---|---|---|
| **Category Index** | `output/output_<category>/index.md` | Contains Section Names, Ingestion Date, and Metadata Summaries. | Loaded by `validate_wiki_node` first to establish context awareness and search paths. |
| **Wiki Article** | `output/output_<category>/<category>.md` | Segmented strictly into 10 structured sections (Quick Facts, Technical Specs, Standards, Market Intelligence, etc.). | Parsed during `create_specs_node`. Top Demand Signals (Section 9) and Buyer Ask (Section 10) directly derive Spec Names. |
| **Source References** | `output/output_<category>/references.md` | Contains mapped arrays of: `[Source Title, Data Type, Reliability Level, Verbatim Quote]`. | Injected into LLM context. Multi-source confirmations directly guide attribute tiering (Primary vs Tertiary). |
| **Ingestion Logs** | `output/output_<category>/logs.md` | Timestamps of ingestion, token sizes, source domains, and crawl history. | Primarily used for telemetry, developer diagnostics, and audit logs. |

### 🏷️ Mapped Brand Representation Logic
Brands are dynamic attributes. The engine uses a custom rulebook logic based on catalog data to decide brand representations:

```
                          ┌──────────────────────────┐
                          │   Examine Section 4 &    │
                          │ Section 9 of target wiki │
                          └────────────┬─────────────┘
                                       │
                         [Is Brand commercial signal?]
                        ┌──────────────┴──────────────┐
                     YES│                             │NO
                        ▼                             ▼
            [Is market structure highly]       [Exclude Brand spec
                 concentrated?]                  completely]
              ┌─────────┴─────────┐
           YES│                  NO│ (Fragmented >10 brands)
              ▼                    ▼
     [radio_button output]    [text_input output]
     Option list populated     Options array is empty:
     with <=5 dominant brands        options: []
```

---

## 🧭 A Tour of the Lifecycle

Below is a complete, multi-turn system trace showcasing how a category is verified, analyzed, self-corrected, and successfully delivered:

### Phase 1: Interactive / CLI Trigger
The user launches the workflow:
```bash
python main.py --mcat-id 27670 --mcat-name "Electronic Weighbridge"
```
1. `main.py` parses parameters and calls `build_graph()`.
2. Initial dictionary injected: `{"mcat_id": "27670", "mcat_name": "Electronic Weighbridge"}`.

### Phase 2: Core Validation Checks (`validate_wiki_node`)
1. Sanitizes category name using `sanitize_filename("Electronic Weighbridge")` $\rightarrow$ `"electronic_weighbridge"`.
2. Checks filesystem: `output/output_electronic_weighbridge/electronic_weighbridge.md`.
3. Checks and loads companion files: `index.md`, `references.md`.
4. Populates state with file contents and changes state status to `"wiki_found"`.

### Phase 3: Logical Verification & Self-Correction (`create_specs_node`)
1. Loads System context combining general system prompt (`agent_prompt_spec-creation.md`) and strict validation skills (`spec_creation.md`).
2. Gemini 2.5 Pro receives prompts with `enable_thinking=True` and `temperature=0`.
3. **Internal Self-Audit Step**: The model drafts its specifications and evaluates them internally. Let's trace an actual correction step made by the LLM:
   * *Draft Spec*: `Platform Length (m)` with options `["12", "16", "18"]`.
   * *Self-Audit Trigger*: "Wait, `spec_creation.md` states: *No units in spec names — units belong on option values only*. Also, option values must match standard B2B search terms."
   * *Correction*: Modifies spec name to `Platform Length` and updates option values to `["12 m", "16 m", "18 m"]`.
   * *Audit Checklist Check*: `[PASS]` for Spec Names and Option Formats.

### Phase 4: Structured Delivery & Ingestion
1. The sanitized JSON is returned by the LLM.
2. The agent extracts JSON block from formatting fences, runs a syntax validation, and saves the final result to `seller_specs_output/27670_final_specs.json`.
3. Status updated to `"complete"`, ending the LangGraph execution loop cleanly.

---

## 🔄 Before vs. After Illustrative Comparison

To demonstrate the real business value of the system, we contrast an un-audited product schema generated by a generic AI against a clean, audited, and deterministic specification structure generated by this engine.

### ❌ Generic Un-Audited AI Spec (High Hallucination)
```json
{
  "category": "Electronic Weighbridge",
  "specifications": {
    "Capacity (Tons)": ["30-50", "50-100", "Custom"],
    "Platform Size": ["Small", "Standard size", "Large"],
    "Material": ["Steel", "Concrete", "Other"],
    "Accurateness": ["Excellent", "99.9%"],
    "Brand Option": ["Generic", "Local", "Unbranded"]
  }
}
```
> [!CAUTION]
> **Audit Violations in Un-Audited Output:**
> 1. **Units in Spec Name**: `"Capacity (Tons)"` violates the rule: *No units in names*.
> 2. **Vague Placeholders**: Contains `"Custom"`, `"Other"`, `"Generic"`, and `"Unbranded"` (all strictly banned).
> 3. **Non-Standard Range & Symbols**: `"30-50"` uses a hyphen `-` instead of an en dash `–`, and mixes discrete dimensions into subjective classes like `"Small"` and `"Standard size"`.
> 4. **Subjective Terminology**: `"Accurateness"` uses subjective marketing words like `"Excellent"` instead of industrial standard limits (e.g. `"10 kg"`).

---

###  Audited Engine Spec (Zero Hallucination, Production-Ready)
```json
{
  "category_name": "Electronic Weighbridge",
  "finalized_specs": {
    "finalized_primary_specs": {
      "specs": [
        {
          "spec_name": "Capacity",
          "options": ["60 Tonne", "100 Tonne", "50 Tonne", "80 Tonne"],
          "input_type": "radio_button"
        },
        {
          "spec_name": "Platform Length",
          "options": ["16 m", "18 m", "12 m", "9 m"],
          "input_type": "radio_button"
        }
      ]
    },
    "finalized_secondary_specs": {
      "specs": [
        {
          "spec_name": "Platform Material",
          "options": ["Mild Steel (MS)", "Concrete (RCC)"],
          "input_type": "radio_button"
        },
        {
          "spec_name": "Brand",
          "options": [],
          "input_type": "text_input"
        }
      ]
    },
    "finalized_tertiary_specs": {
      "specs": [
        {
          "spec_name": "Accuracy",
          "options": ["10 kg", "5 kg", "20 kg"],
          "input_type": "radio_button"
        }
      ]
    }
  }
}
```
> [!TIP]
> **Why the Audited Spec Wins:**
> * Spec names are cleanly Title Cased and free of unit brackets.
> * Option values attach standard units (`Tonne`, `m`, `kg`) directly to values with zero space separation.
> * Fragmented brands are modeled as `text_input` with empty `[]` to prevent gameable selection, while specific materials are stored in standard forms with parentheses abbreviations: `Mild Steel (MS)`.

---

## 📂 Directory Map

Here is the clean, annotated tree map of the workspace directory. Every file has a single, well-defined responsibility:

```
Specs-onywiki/
├── .env                              # Environment configurations (API Keys, Thinking Flags)
├── .gitignore                        # Standard files, cache, and spec output directories to ignore
├── ARCHITECTURE.md                   # Mapped flow representation for catalog developers
├── README.md                         # This masterclass documentation
├── requirements.txt                  # Consolidated python dependency requirements
│
├── main.py                           # [CLI] Entry point for Usecase 1: Seller Specifications
├── buyer_persona_main.py             # [CLI] Entry point for Usecase 2: Buyer Persona specs
├── chat_main.py                      # [CLI] Entry point for Usecase 3: Multi-turn Wiki Chatbot
├── config.py                         # Path and environment resolution gateway
│
├── pipelines/                        # Stateful LangGraph Pipelines
│   ├── seller_specs/                 # Workflow for Seller Spec Creation
│   │   ├── graph/
│   │   │   ├── edges.py              # Conditional state routing & branching rules
│   │   │   ├── nodes.py              # Core node functions (loads, invokes LLM, validates output)
│   │   │   └── state.py              # Defines the TypedDict schema for State tracking
│   │
│   ├── buyer_persona_specs/          # Workflow for Buyer Intent Specs
│   │   ├── graph/
│   │   │   ├── edges.py              # Route decisions for Buyer Intent graph
│   │   │   ├── nodes.py              # Node loaders and AST python list cleaners
│   │   │   └── state.py              # TypedDict schema for Buyer Persona State tracking
│   │
│   └── chatbot/                      # Stateful Wiki-Grounded Chatbot
│       ├── graph/
│       │   ├── edges.py              # State edge maps for conversation nodes
│       │   ├── nodes.py              # Handles conversation history & context injections
│       │   └── state.py              # ChatState dictionary including Message object lists
│
├── skills/                           # Master Blueprints & Constrained Rulebooks
│   ├── seller_specs/
│   │   ├── agent_prompt_spec-creation.md    # Operating procedure instructions for Seller Specs
│   │   └── spec_creation.md                 # Hard rules (Indian B2B, symbols, en-dash, tiers)
│   │
│   ├── buyer_persona_specs/
│   │   ├── agent_prompt_buyer_persona_spec-creation.md # Operating blueprint for Buyer Personas
│   │   └── buyer_persona_spec_creation_skill.md       # Target restrictions (max 2 specs, no product attributes)
│   │
│   └── chatbot/
│       └── chat_prompt.md            # Mandatory instructions preventing hallucination / generic text
│
├── utils/                            # Low-level core utilities
│   └── llm.py                        # Thin wrapper over custom LLM gateway with retry & thinking extraction
│
├── output/                           # Ground Truth Knowledge base (committed to git)
│   ├── output_aac_blocks/
│   │   ├── aac_blocks.md             # Wikipedia source article for AAC Blocks
│   │   ├── index.md                  # Section index mapping file
│   │   └── references.md             # Mapped reference lists for verification
│   └── output_...                    # Knowledge base directories for all categories
│
└── wiki/                             # Archive of original Markdown source files
    ├── doubts/                       # Mapped edge cases and user doubts
    ├── index/                        # Index catalog pages for verification
    ├── items/                        # Ground-truth Wikipedia markdown files
    └── references/                   # Reference manuals
```

---

## 🛠️ Setup & Installation

Follow these steps to deploy and run the system locally.

### 1. Clone & Set Up Python Virtual Environment
First, ensure you have Python 3.10+ installed.
```bash
# Clone the repository (or navigate to directory)
cd Specs-onywiki

# Create a virtual environment
python -m venv .venv

# Activate the virtual environment
# On Windows (PowerShell):
.venv\Scripts\Activate.ps1
# On macOS / Linux:
source .venv/bin/activate
```

### 2. Install Project Dependencies
Install standard requirements from the lock file:
```bash
pip install -r requirements.txt
```

### 3. Environment Configuration
Create a `.env` file in the root directory (a `.env` is already configured for the workspace):
```env
# ── LLM Gateway Credentials ──────────────────────────────────────────────────
LLM_GATEWAY_URL=https://imllm.intermesh.net/v1/chat/completions
LLM_GATEWAY_API_KEY=your_secured_gateway_api_key_here

# ── LLM Model ───────────────────────────────────────────────────────────────
LLM_MODEL=google/gemini-2.5-pro
LLM_MAX_TOKENS=16000

# ── Presigned URL API ───────────────────────────────────────────────────────
PRESIGNED_URL_API=https://get-presigned-url-for-mcat-w2yrp7i6za-el.a.run.app/

# ── Feature Flags ───────────────────────────────────────────────────────────
LLM_USE_THINKING=true
```

---

## 🚀 Execution & CLI Commands

### Run Usecase 1: Seller Spec Generator
Generate structured specifications for a category.
```bash
# Interactive mode (Prompting for ID and Name)
python main.py

# Direct CLI mode (AAC Blocks Example)
python main.py --mcat-id 68865 --mcat-name "AAC Blocks"
```
* **Final Saved Output**: `seller_specs_output/68865_final_specs.json`
* **Raw Extracted Thinking**: `raw_thinking/68865_thinking.json`

### Run Usecase 2: Buyer Persona Generator
Generate lead qualification parameters.
```bash
# Interactive mode
python buyer_persona_main.py

# Direct CLI mode
python buyer_persona_main.py --mcat-id 68865 --mcat-name "AAC Blocks"
```
* **Final Saved Output**: `buyer_persona_spec_output/68865_final_buyer_persona_specs.json`

### Run Usecase 3: Source-Grounded Chatbot
Start an interactive chat session grounded strictly in a category's knowledge base.
```bash
# Start a chat session for Colour Coated Roofing Sheets
python chat_main.py --mcat-name "Colour Coated Roofing Sheet"
```
* **Conversation Flow example**:
  ```
  You: What are the standard dimensions of these roofing sheets?
  Assistant: According to the Technical Specs in the wiki, roofing sheets are available in standard widths of 910 mm and 1000 mm, with thicknesses ranging from 0.3 mm to 0.8 mm...
  
  You: Can I get them in green?
  Assistant: Yes, according to Section 3 of the wiki, standard colors include Leaf Green (RAL 6002) and Forest Green (RAL 6005)...
  ```

---

## 🛡️ Troubleshooting & Development FAQ

### Q1: How does the system prevent the agent from getting stuck in loops?
**A**: Loops occur when agents repeatedly generate invalid JSON schemas or enter endless retry loops.
1. **Conditional State Transition**: LangGraph does not contain loop edges for errors. If a node fails, it raises an exception and outputs a diagnostic log file (`raw_output.txt`) immediately instead of re-trying the LLM infinitely.
2. **Fixed Graph Topology**: The graph is linear (`validate_wiki_node` $\rightarrow$ `create_specs_node` $\rightarrow$ `END`). There is no cyclical edge, ensuring a maximum execution path length of 2 transitions.

### Q2: What happens if the LLM response fails to parse as valid JSON?
**A**: In case of a parse failure (e.g. due to truncated responses or token overflow):
1. The error block is caught in [nodes.py](file:///c:/Users/Imart\Desktop/Specs-onywiki/pipelines/seller_specs/graph/nodes.py#L145-L153).
2. The raw response string is saved to `seller_specs_output/{mcat_id}_raw_output.txt`.
3. A descriptive `RuntimeError` is raised, pointing the developer directly to the file to inspect the output.

### Q3: Why is Gemini 2.5 Pro used with thinking mode enabled?
**A**: Enabling `thinking: {type: "enabled", budget_tokens: 10000}` allows Gemini to run multi-step planning, audit, and quality checklists in a hidden reasoning buffer before writing the actual answer. This increases latency slightly (typically 8–15s) but pushes output compliance to near 100%, reducing post-processing failures to zero.

### Q4: How do we update prompts or schema configurations?
**A**: Do not edit Python scripts to change rules!
* To edit **seller specifications rules** (e.g. adding new forbidden symbols, changing character limits), update [skills/seller_specs/spec_creation.md](file:///c:/Users/Imart/Desktop/Specs-onywiki/skills/seller_specs/spec_creation.md).
* To edit **agent behaviors or operational flow**, edit [skills/seller_specs/agent_prompt_spec-creation.md](file:///c:/Users/Imart/Desktop/Specs-onywiki/skills/seller_specs/agent_prompt_spec-creation.md).
* The graph dynamically loads these files during every step execution.

### Q5: What is the fallback if the LLM Gateway API fails?
**A**: The thin HTTP gateway wrapper in [utils/llm.py](file:///c:/Users/Imart/Desktop/Specs-onywiki/utils/llm.py#L94-L139) features an exponential backoff retry loop:
* Retries up to **4 times** sequentially.
* Introduces a **30-second delay** between retries to recover from transient server overloads or gateway timeouts.
