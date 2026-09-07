---
name: sync-adk-agents
description: >-
  Sync ADK certification agent docs: regenerate README.md, ensure each agent
  folder has .env.example and .gitignore for .env, and update agents.yaml when
  adding new agents. Use when the user asks to sync agent docs, update the README,
  refresh env examples, or add a new ADK agent to the catalog.
---

# Sync ADK Agent Docs

Keep the agent catalog, environment templates, and gitignore rules in sync across the repo.

## When to use

- User adds a new agent folder
- User asks to update README, `.env.example`, or `.gitignore`
- User says "sync agents" or "update agent docs"

## Workflow

### 1. Run the sync script

```bash
python scripts/sync_adk_agent_docs.py
```

This reads `agents.yaml` and updates:
- `README.md` — agent catalog with topics and learnings
- `<agent_folder>/.env.example` — placeholder env per template
- `<agent_folder>/.gitignore` — ignores `.env` and `.adk/`
- Root `.gitignore` — ignores all `**/.env` files

### 2. When adding a new agent

1. Choose a track folder: `foundational/` (single-agent, Path 3545) or
   `multi_agent/` (Path 3877).
2. Create the agent folder with `agent.py` (or `root_agent.yaml`) and `__init__.py`
3. Add `load_dotenv(Path(__file__).parent / ".env")` in `agent.py`
4. Append an entry to `agents.yaml`:

```yaml
  - track: foundational          # or multi_agent
    folder: my_new_agent
    name: my_agent_name
    module: "Module X"
    topic: Short topic title
    learned:
      - Bullet 1
      - Bullet 2
    run: adk run foundational.my_new_agent
    env_template: enterprise   # or vertexai
```

5. Run `python scripts/sync_adk_agent_docs.py`
6. Copy `.env.example` → `.env` and add the real API key locally

ADK discovers nested agents with dot paths, e.g. `foundational.geography_assistant`.

### 3. Env templates

Defined in `agents.yaml` under `env_templates`:

| Key | Use when |
|-----|----------|
| `enterprise` | `GOOGLE_GENAI_USE_ENTERPRISE=0` (most agents) |
| `vertexai` | `GOOGLE_GENAI_USE_VERTEXAI=0` (simple_agent_module1) |

Never copy real keys from `.env` into `.env.example` or README.

### 4. Agent folder conventions

- Folder name: valid Python identifier (underscores, no hyphens)
- Export `root_agent` in `agent.py` for `adk web` / `adk run`
- Model default: `gemini-3.6-flash` unless the lesson requires otherwise

## Verification

After sync, confirm:

- [ ] Every agent in `agents.yaml` has a matching folder
- [ ] Each folder has `.env.example` and `.gitignore`
- [ ] `README.md` lists all agents with learnings
- [ ] No `.env` files contain committed secrets
