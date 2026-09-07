# ADK Certification — Resources & Hands-on

Google Agent Development Kit (ADK) learning project organized by track.
Each agent folder is a self-contained demo of one concept.

## Learning paths

| Track | Path | Focus |
|-------|------|-------|
| `foundational/` — Foundational (single-agent) | [Develop Agents with Agent Development Kit (ADK)](https://www.skills.google/paths/3545) | Single LlmAgent concepts — setup, instructions, session state, tools, and MCP integration. |
| `multi_agent/` — Multi-agent | [Multi-Agent ADK](https://www.skills.google/paths/3877) | Orchestration patterns — sub-agents, pipelines, and coordinated multi-agent workflows. |

- **Foundational (single-agent)** (`foundational/`): [Path 3545](https://www.skills.google/paths/3545)
  - Badge: [Engineer AI Agents with Agent Development Kit (ADK)](https://www.credly.com/badges/14b4692b-b475-4b7f-adab-2b4ca2d532c2)
- **Multi-agent** (`multi_agent/`): [Path 3877](https://www.skills.google/paths/3877)

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install google-adk python-dotenv pyyaml
pip install 'mcp>=1.0,<2'  # MCP tools (foundational/file_reader_mcp)

# Per agent:
cp <track>/<agent_folder>/.env.example <track>/<agent_folder>/.env
# Edit .env with your GOOGLE_API_KEY

adk web .                                    # browse all agents
adk run foundational.geography_assistant     # one agent (dot path)
python foundational/geography_assistant/test_tools.py
```

## Project structure

```text
google-adk-certification-resource-and-hands-on/
├── agents.yaml
├── course_template.py       # shared helper (state templating)
├── scripts/sync_adk_agent_docs.py
├── foundational/              # Path 3545 — single-agent
│   ├── simple_agent_module1/
│   ├── geography_assistant/
│   └── ...
└── multi_agent/               # Path 3877 — multi-agent
    └── (agents added as you learn)
```

Sync docs after adding agents:

```bash
python scripts/sync_adk_agent_docs.py
```

## Foundational (single-agent) (`foundational/`)

[Path 3545](https://www.skills.google/paths/3545) — Single LlmAgent concepts — setup, instructions, session state, tools, and MCP integration.

### Modules 1–2 Recap

Session state is a dictionary. output_key writes agent output to state. {key} templating reads state into instructions.

**How long does state persist?** → State namespaces control persistence scope — not all state should live forever.

You can now:
- Use `session.state` as a dictionary
- Use `output_key` to save agent responses to state
- Use `{key}` templating to inject state into instructions

### State namespaces

| Prefix | Lifetime | Example |
|--------|----------|---------|
| `temp:` | Current turn only | `temp:step = validating` |
| (none) | Current session | `topic = refunds` |
| `user:` | All sessions for user | `user:theme = dark` |
| `app:` | Global for app | `app:version = 2.0` |

### ADK tool types

| Type | Complexity | Setup | Use when | Example |
|------|------------|-------|----------|---------|
| Built-in | Low | Import and use | Common capabilities (search, code execution, RAG) | `google_search` |
| Function Tools | Medium | Write Python function | Custom business logic | `get_capital_city` |
| Agent-as-Tool | Medium-High | Specialized sub-agent | Specialized reasoning (e.g. Google Search + other tools) | `GoogleSearchAgentTool` |

**Note:** `google_search` is a built-in tool and cannot be combined
with custom function tools on the same agent directly. Use
`GoogleSearchTool(bypass_multi_tools_limit=True)` to wrap it as a
sub-agent (`GoogleSearchAgentTool`).

### MCP tools

Official MCP server catalog: [https://registry.modelcontextprotocol.io](https://registry.modelcontextprotocol.io)

| Connection | Use for |
|------------|---------|
| `StdioConnectionParams` | Local servers via subprocess (development) |
| `SseConnectionParams` | Remote servers via HTTP (production) |

### Agents

#### `foundational/simple_agent_module1` — Simple agent & programmatic runner

- **Module:** Module 1–3
- **Agent name:** `math_tutor`
- **ADK name:** `foundational.simple_agent_module1`
- **Run:** `python foundational/simple_agent_module1/agent.py`
- **What we learned:**
  - Basic LlmAgent / Agent setup with gemini-3.6-flash
  - Agent folder naming (underscores, valid Python identifiers)
  - Running via adk run, adk api_server, and curl /run
  - Programmatic Runner + InMemorySessionService
  - load_dotenv and session state from environment variables

#### `foundational/agent_with_yaml` — Declarative agent configuration

- **Module:** Module — YAML
- **Agent name:** `root_agent`
- **ADK name:** `foundational.agent_with_yaml`
- **Run:** `adk run foundational.agent_with_yaml`
- **What we learned:**
  - Define agents in root_agent.yaml instead of agent.py
  - Instruction, model, and metadata without Python code
  - Same adk web / adk run workflow as code-based agents

#### `foundational/customer_support_agent` — Optimized instruction design

- **Module:** Module — Instructions
- **Agent name:** `support_specialist`
- **ADK name:** `foundational.customer_support_agent`
- **Run:** `adk run foundational.customer_support_agent`
- **What we learned:**
  - Structured prompts (identity, mission, methodology, boundaries)
  - Persona and tone control for production-style agents
  - load_dotenv for API credentials

#### `foundational/product_extractor` — Pydantic output_schema & output_key

- **Module:** Module — Structured output
- **Agent name:** `product_extractor`
- **ADK name:** `foundational.product_extractor`
- **Run:** `adk run foundational.product_extractor`
- **What we learned:**
  - Pydantic models to enforce JSON response shape
  - output_schema validates model output automatically
  - output_key stores parsed result in session state for reuse

#### `foundational/model_comparison` — generate_content_config tuning

- **Module:** Module — Model config
- **Agent name:** `data_extractor / creative_brainstormer`
- **ADK name:** `foundational.model_comparison`
- **Run:** `adk run foundational.model_comparison`
- **What we learned:**
  - temperature, top_p, top_k for factual vs creative behavior
  - max_output_tokens and multi-agent comparison patterns
  - safety_settings (HarmCategory, HarmBlockThreshold)

#### `foundational/problem_solver_reasoning_agent` — BuiltInPlanner & thinking

- **Module:** Module — Planning
- **Agent name:** `strategic_problem_solver`
- **ADK name:** `foundational.problem_solver_reasoning_agent`
- **Run:** `adk run foundational.problem_solver_reasoning_agent`
- **What we learned:**
  - BuiltInPlanner with ThinkingConfig for Gemini models
  - include_thoughts and thinking_budget for visible reasoning
  - When to use BuiltInPlanner vs PlanReActPlanner

#### `foundational/name_extractor_memory` — output_key & session memory

- **Module:** Module — Session state
- **Agent name:** `name_extractor`
- **ADK name:** `foundational.name_extractor_memory`
- **Run:** `python foundational/name_extractor_memory/test_state.py`
- **What we learned:**
  - output_key saves agent response to session.state automatically
  - Access state programmatically via session.state.get("user_name")
  - State persists across multiple turns in the same session
  - Programmatic testing with Runner and InMemorySessionService

#### `foundational/personalized_greeter` — {key} instruction templating

- **Module:** Module — State templating
- **Agent name:** `personalized_greeter`
- **ADK name:** `foundational.personalized_greeter`
- **Run:** `python foundational/personalized_greeter/test_templating.py`
- **What we learned:**
  - Inject session.state into instructions with {key} syntax
  - Optional defaults with {key?default} and conditional blocks
  - ADK resolves templates before sending instructions to the LLM
  - Instructions adapt dynamically based on available state

#### `foundational/namespace_demo` — temp / session / user / app scopes

- **Module:** Module — State namespaces
- **Agent name:** `namespace_demo`
- **ADK name:** `foundational.namespace_demo`
- **Run:** `python foundational/namespace_demo/test_namespaces.py`
- **What we learned:**
  - Four state namespaces with different persistence lifetimes
  - {'temp': 'current turn only, session (no prefix) per conversation'}
  - {'user': 'persists across sessions for same user'}
  - {'app': 'global config shared by all users'}

#### `foundational/geography_assistant` — Function tools + Google Search

- **Module:** Module — Tools
- **Agent name:** `geography_assistant`
- **ADK name:** `foundational.geography_assistant`
- **Run:** `python foundational/geography_assistant/test_tools.py`
- **What we learned:**
  - Custom function tools with Python functions and docstrings
  - Built-in google_search tool for live web facts
  - google_search cannot mix with function tools on one agent without bypass_multi_tools_limit
  - ADK wraps Google Search as a sub-agent when combined with custom tools

#### `foundational/file_reader_mcp` — McpToolset + filesystem server

- **Module:** Module — MCP tools
- **Agent name:** `file_reader_assistant`
- **ADK name:** `foundational.file_reader_mcp`
- **Run:** `python foundational/file_reader_mcp/test_mcp.py`
- **What we learned:**
  - Connect to MCP servers via McpToolset (stdio or SSE)
  - Browse MCP catalog at registry.modelcontextprotocol.io
  - StdioConnectionParams — local subprocess (development, e.g. npx)
  - SseConnectionParams — remote HTTP/SSE (production)
  - tool_filter limits exposed tools to safe read-only operations
  - Requires Node.js/npm and pip install 'mcp>=1.0,<2' (MCP SDK)

## Multi-agent (`multi_agent/`)

[Path 3877](https://www.skills.google/paths/3877) — Orchestration patterns — sub-agents, pipelines, and coordinated multi-agent workflows.

_No agents yet — add folders under `multi_agent/` as you progress._

## Environment & secrets

- `.env` files are gitignored at the **root** (`.env`, `**/.env`) and in
  **each agent folder** (`.gitignore` with `.env`).
- `.env.example` templates are committed; copy to `.env` per agent.
- Never commit real API keys.
