# Multi-agent track

Multi-agent orchestration demos for [Path 3877](https://www.skills.google/paths/3877).

## Orchestration: `balanced_research/`

Parallel benefits + challenges researchers → balanced summarizer.

```bash
adk run multi_agent.balanced_research
```

**Try:** *"Research artificial intelligence in healthcare"*

## Capstone: `customer_service_app_multi_agent/`

Full pipeline: **intake → parallel specialists → responder**

```bash
adk run multi_agent.customer_service_app_multi_agent
```

See the main [README](../README.md#multi-agent-multi_agent) for decision guide, diagrams, and test scenarios.

## All agents

| Pattern | Folder |
|---------|--------|
| Coordinator (LLM routing) | `customer_service/` |
| Sequential pipeline | `sequential_pipeline/` |
| Parallel research | `parallel_research/` |
| Refinement loop | `refinement_loop/` |
| State communication | `research_pipeline/` |
| **Orchestration** — parallel + aggregate | `balanced_research/` |
| **State in workflows** — session + user: | `doc_processor/` |
| **Custom agents** — conditional routing | `conditional_router/` |
| **A2A protocol** — expose + consume | `a2a_demo/` |
| **Film concept team** — Sequential + Loop + Parallel capstone | `film_concept_team/` |
| **Capstone** | `customer_service_app_multi_agent/` |

### A2A demo (`a2a_demo/`)

**Local** — remote specialist over HTTP, local coordinator:

```bash
pip install 'google-adk[a2a]'
cp multi_agent/a2a_demo/.env.example multi_agent/a2a_demo/.env

# Terminal 1 — expose specialist (to_a2a + uvicorn)
uvicorn multi_agent.a2a_demo.remote_research_specialist.agent:a2a_app --host localhost --port 8001

# Terminal 2 — run coordinator
adk run multi_agent/a2a_demo
```

**Cloud Run A2A server** — deploy with `agent.json` + `--a2a`:

```bash
# Files: remote_research_specialist/agent.json, agent.py, requirements.txt
adk deploy cloud_run \
  --project=$GOOGLE_CLOUD_PROJECT \
  --region=us-central1 \
  --service_name=research-specialist \
  --a2a \
  multi_agent/a2a_demo/remote_research_specialist \
  -- \
  --set-env-vars="GOOGLE_CLOUD_LOCATION=global"
```

Update `agent.json` `url` to your Cloud Run service URL after deploy.

**A2A client** — `RemoteA2aAgent` with local card file or URL:

```python
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent

illustration_agent = RemoteA2aAgent(
    name="illustration_agent",
    description="Agent that generates illustrations.",
    agent_card="illustration-agent-card.json",  # or HTTPS URL
)
```

See `illustration-agent-card.json` and `agent.py` for full consume examples.

**Agent as Tool vs sub_agents** — see main README. Use `AgentTool(agent=search_agent)` in `tools` instead of listing the specialist in `sub_agents` when the parent should call it explicitly.

```bash
adk web .
```
