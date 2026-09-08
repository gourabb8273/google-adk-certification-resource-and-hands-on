#!/usr/bin/env python3
"""Sync ADK agent docs: README, .env.example, and per-agent .gitignore."""

from __future__ import annotations

import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("PyYAML required: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "agents.yaml"
README = ROOT / "README.md"
ROOT_GITIGNORE = ROOT / ".gitignore"

ENV_IGNORE_LINES = [".env", "**/.env"]
ROOT_GITIGNORE_EXTRA = [
    "",
    "# Virtual environment",
    ".venv/",
    "",
    "# ADK local storage",
    ".adk/",
    "**/.adk/",
    "",
    "# Python",
    "__pycache__/",
    "*.py[cod]",
    "*.egg-info/",
    ".pytest_cache/",
]


def load_manifest() -> dict:
    with MANIFEST.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def agent_path(agent: dict, tracks: dict) -> str:
    track = tracks[agent.get("track", "foundational")]
    return f"{track['dir']}/{agent['folder']}"


def adk_agent_name(agent: dict, tracks: dict) -> str:
    track = tracks[agent.get("track", "foundational")]
    return f"{track['dir']}.{agent['folder']}"


def render_env_example(agent: dict, manifest: dict) -> str:
    template_key = agent.get("env_template", "enterprise")
    template = manifest["env_templates"][template_key]
    lines = [f"{key}={value}" for key, value in template.items()]
    return "\n".join(lines) + "\n"


def ensure_env_example(agent_dir: Path, content: str) -> bool:
    path = agent_dir / ".env.example"
    changed = not path.exists() or path.read_text(encoding="utf-8") != content
    path.write_text(content, encoding="utf-8")
    return changed


def ensure_agent_gitignore(agent_dir: Path, lines: list[str]) -> bool:
    path = agent_dir / ".gitignore"
    desired = "\n".join(lines) + "\n"
    changed = not path.exists() or path.read_text(encoding="utf-8") != desired
    path.write_text(desired, encoding="utf-8")
    return changed


def ensure_root_gitignore() -> bool:
    lines = [
        "# Environment secrets (use .env.example as a template)",
        *ENV_IGNORE_LINES,
        *ROOT_GITIGNORE_EXTRA,
    ]
    desired = "\n".join(lines).rstrip() + "\n"
    changed = (
        not ROOT_GITIGNORE.exists()
        or ROOT_GITIGNORE.read_text(encoding="utf-8") != desired
    )
    ROOT_GITIGNORE.write_text(desired, encoding="utf-8")
    return changed


def render_track_courses(tracks: dict) -> list[str]:
    lines = [
        "## Learning paths",
        "",
        "| Track | Path | Focus |",
        "|-------|------|-------|",
    ]
    for track in tracks.values():
        path_url = track.get("path_url")
        if path_url:
            link = f"[{track['title']}]({path_url})"
        else:
            link = track["title"]
        lines.append(
            f"| `{track['dir']}/` — {track['label']} | {link} | {track['summary']} |"
        )
    lines.append("")

    for track in tracks.values():
        path_id = track.get("path_id")
        path_url = track.get("path_url")
        if path_id and path_url:
            lines.append(
                f"- **{track['label']}** (`{track['dir']}/`): "
                f"[Path {path_id}]({path_url})"
            )
        elif path_url:
            lines.append(
                f"- **{track['label']}** (`{track['dir']}/`): "
                f"[{track['title']}]({path_url})"
            )
        else:
            lines.append(f"- **{track['label']}** (`{track['dir']}/`)")
        badge_name = track.get("badge_name")
        badge_url = track.get("badge_url")
        if badge_name and badge_url:
            lines.append(
                f"  - Badge: [{badge_name}]({badge_url})"
            )
    lines.append("")
    return lines


def render_foundational_reference(manifest: dict) -> list[str]:
    lines: list[str] = []

    recap = manifest.get("module_recap")
    if recap:
        lines.extend(
            [
                f"### {recap['title']}",
                "",
                recap["summary"],
                "",
                f"**{recap['question']}** → {recap['answer']}",
                "",
                "You can now:",
                "- Use `session.state` as a dictionary",
                "- Use `output_key` to save agent responses to state",
                "- Use `{key}` templating to inject state into instructions",
                "",
            ]
        )

    ns_block = manifest.get("state_namespaces", {})
    namespaces = ns_block.get("namespaces", ns_block if isinstance(ns_block, list) else [])
    if namespaces:
        lines.extend(
            [
                "### State namespaces",
                "",
                "| Prefix | Lifetime | Example |",
                "|--------|----------|---------|",
            ]
        )
        for ns in namespaces:
            prefix = f"`{ns['prefix']}`" if ns["prefix"] != "(none)" else "(none)"
            lines.append(
                f"| {prefix} | {ns['lifetime']} | `{ns['example']}` |"
            )
        lines.append("")

    tool_types = manifest.get("tool_types")
    if tool_types:
        lines.extend(
            [
                "### ADK tool types",
                "",
                "| Type | Complexity | Setup | Use when | Example |",
                "|------|------------|-------|----------|---------|",
            ]
        )
        for tool in tool_types:
            lines.append(
                f"| {tool['type']} | {tool['complexity']} | {tool['setup']} | "
                f"{tool['use_when']} | `{tool['example']}` |"
            )
        lines.append("")
        lines.extend(
            [
                "**Note:** `google_search` is a built-in tool and cannot be combined",
                "with custom function tools on the same agent directly. Use",
                "`GoogleSearchTool(bypass_multi_tools_limit=True)` to wrap it as a",
                "sub-agent (`GoogleSearchAgentTool`).",
                "",
            ]
        )

    mcp_info = manifest.get("mcp_info")
    if mcp_info:
        lines.extend(
            [
                "### MCP tools",
                "",
                f"Official MCP server catalog: [{mcp_info['registry']}]({mcp_info['registry']})",
                "",
                "| Connection | Use for |",
                "|------------|---------|",
            ]
        )
        for conn in mcp_info["connection_types"]:
            lines.append(f"| `{conn['name']}` | {conn['use']} |")
        lines.append("")

    memory = manifest.get("memory_bank")
    if memory:
        lines.extend(render_memory_bank_docs(memory))

    return lines


def render_memory_bank_docs(memory: dict) -> list[str]:
    lines = [
        f"### {memory['title']}",
        "",
        memory["intro"],
        "",
        "| | Session state | Memory Bank |",
        "|---|---------------|-------------|",
        f"| Question | {memory['session_vs_memory']['session']} | "
        f"{memory['session_vs_memory']['memory_bank']} |",
        "",
        "**Lifecycle (conceptual):**",
        "",
    ]
    for i, step in enumerate(memory.get("lifecycle", []), 1):
        lines.append(f"{i}. {step}")
    lines.extend(["", "**Key features:**", ""])
    for feat in memory.get("features", []):
        lines.append(f"- **{feat['name']}** — {feat['description']}")

    local = memory.get("local_vs_production", {})
    if local:
        lines.extend(
            [
                "",
                "**Local vs production:**",
                "",
                f"| | {local.get('local_service', 'Local')} | "
                f"{local.get('production_service', 'Production')} |",
                "|---|-------|------------|",
                f"| Use | {local.get('local_use', '')} | "
                f"{local.get('production_use', '')} |",
            ]
        )

    pattern = memory.get("pattern", {})
    if pattern:
        lines.extend(
            [
                "",
                f"- **Save:** `{pattern.get('save', '')}`",
                f"- **Recall:** `{pattern.get('recall', '')}`",
            ]
        )

    prod_cfg = memory.get("production_config")
    if prod_cfg:
        lines.extend(["", "**Production config:**", "", f"```bash\n{prod_cfg}\n```"])

    demo = memory.get("demo")
    if demo:
        lines.append(f"\nDemo: `foundational/{demo}/`")

    ref = memory.get("reference")
    if ref:
        lines.append(f"[ADK memory docs]({ref})")
    lines.append("")
    return lines


def render_multi_agent_reference(manifest: dict) -> list[str]:
    workflow = manifest.get("workflow_agents")
    if not workflow:
        return []

    lines = [
        "### Multi-agent patterns",
        "",
        "**Coordinator** (`sub_agents` on `LlmAgent`) — LLM decides which specialist "
        "handles each request. See `customer_service/`.",
        "",
        "### Workflow agents (deterministic)",
        "",
        workflow["intro"],
        "",
        "**Use cases:**",
    ]
    for item in workflow["use_cases"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.extend(
        [
            "| Type | Pattern | Use when | Demo |",
            "|------|---------|----------|------|",
        ]
    )
    for wf in workflow["types"]:
        demo = wf.get("demo", "")
        demo_link = f"`multi_agent/{demo}/`" if demo else "—"
        lines.append(
            f"| `{wf['name']}` | {wf['pattern']} | {wf['use_when']} | {demo_link} |"
        )
    lines.append("")

    for wf in workflow["types"]:
        lines.extend(
            [
                f"#### {wf['name']} (`{wf['pattern']}`)",
                "",
                f"{wf['use_when']}.",
                "",
            ]
        )
        for key in wf.get("keys", []):
            lines.append(f"- {key}")
        ref = wf.get("reference")
        if ref:
            lines.append(f"- [ADK docs]({ref})")
        lines.append("")

    guide = manifest.get("workflow_decision_guide")
    if guide:
        lines.extend(
            [
                f"### {guide['title']}",
                "",
                "| Situation | Use this | Why |",
                "|-----------|----------|-----|",
            ]
        )
        for row in guide.get("rows", []):
            lines.append(
                f"| {row['situation']} | `{row['agent']}` | {row['why']} |"
            )
        coord = guide.get("parallel_coordination", {})
        if coord:
            lines.extend(
                [
                    "",
                    f"#### {coord['title']}",
                    "",
                ]
            )
            for rule in coord.get("rules", []):
                lines.append(f"- {rule}")
            demo = coord.get("demo")
            pattern = coord.get("pattern", "")
            if demo:
                lines.append(
                    f"- Demo: `multi_agent/{demo}/` — `{pattern}`"
                )
            ref = guide.get("reference")
            if ref:
                lines.append(f"- [ADK workflow agents docs]({ref})")
        lines.append("")

    comm = manifest.get("agent_communication")
    if comm:
        lines.extend(
            [
                "### Agent communication (shared state)",
                "",
                comm["intro"],
                "",
                f"**Primary pattern:** {comm['primary_pattern']['write']}; "
                f"{comm['primary_pattern']['read']}.",
                "",
                f"**Data flow:** {comm['flow']}.",
                "",
                "| Pattern | Use when | Demo |",
                "|---------|----------|------|",
            ]
        )
        for pattern in comm["patterns"]:
            demo = pattern.get("demo", "")
            if demo.startswith("foundational/"):
                demo_link = f"`{demo}/`"
            elif demo:
                demo_link = f"`multi_agent/{demo}/`"
            else:
                demo_link = "—"
            lines.append(
                f"| `{pattern['name']}` | {pattern['use_when']} | {demo_link} |"
            )
        ref = comm.get("reference")
        if ref:
            lines.append("")
            lines.append(f"[ADK docs — multi-agent communication]({ref})")
        lines.append("")

    capstone = manifest.get("customer_service_app_multi_agent")
    if capstone:
        lines.extend(render_customer_service_app_docs(capstone))

    film = manifest.get("film_concept_workflow")
    if film:
        lines.extend(render_film_concept_workflow_docs(film))

    ns_workflow = manifest.get("state_namespaces_workflow")
    if ns_workflow:
        lines.extend(render_state_namespaces_workflow_docs(ns_workflow))

    custom = manifest.get("custom_agents")
    if custom:
        lines.extend(render_custom_agents_docs(custom))

    a2a = manifest.get("a2a_protocol")
    if a2a:
        lines.extend(render_a2a_docs(a2a))

    agent_tool = manifest.get("agent_as_tool")
    if agent_tool:
        lines.extend(render_agent_as_tool_docs(agent_tool))

    return lines


def render_agent_as_tool_docs(block: dict) -> list[str]:
    lines = [
        f"### {block['title']}",
        "",
        block.get("intro", ""),
        "",
        "| Pattern | Control | Use when | Demo |",
        "|---------|---------|----------|------|",
    ]
    for row in block.get("comparison", []):
        demo = row.get("demo", "")
        if demo.startswith("foundational/"):
            demo_link = f"`{demo}/`"
        elif demo:
            demo_link = f"`multi_agent/{demo}/`" if "/" not in demo else f"`{demo}`"
        else:
            demo_link = "—"
        lines.append(
            f"| `{row['pattern']}` | {row['control']} | {row['use_when']} | {demo_link} |"
        )

    before = block.get("before_structure")
    after = block.get("after_structure")
    if before and after:
        lines.extend(
            [
                "",
                "**Before (both as sub_agents):**",
                "",
                "```text",
                before.rstrip(),
                "```",
                "",
                "**After (search as AgentTool):**",
                "",
                "```text",
                after.rstrip(),
                "```",
            ]
        )

    steps = block.get("migration_steps", [])
    if steps:
        lines.extend(["", "**Migration:**", ""])
        for i, step in enumerate(steps, 1):
            lines.append(f"{i}. {step}")

    code = block.get("code_example")
    if code:
        lines.extend(["", "**Code pattern:**", "", "```python", code.rstrip(), "```"])

    skip = block.get("skip_summarization")
    if skip:
        lines.extend(["", f"**skip_summarization:** {skip}"])

    ref = block.get("reference")
    if ref:
        lines.append(f"\n[ADK multi-agent docs]({ref})")
    lines.append("")
    return lines


def render_a2a_docs(a2a: dict) -> list[str]:
    lines = [
        f"### {a2a['title']}",
        "",
        a2a["intro"],
        "",
        "**Core concepts:**",
        "",
        "| Concept | What it means |",
        "|---------|---------------|",
    ]
    for concept in a2a.get("concepts", []):
        lines.append(f"| **{concept['name']}** | {concept['description']} |")
    lines.extend(
        [
            "",
            "**When to use A2A:**",
        ]
    )
    for item in a2a.get("when_to_use", []):
        lines.append(f"- {item}")
    lines.extend(["", "**When you do NOT need A2A:**"])
    for item in a2a.get("when_not_to_use", []):
        lines.append(f"- {item}")

    arch = a2a.get("architecture", {})
    if arch:
        lines.extend(
            [
                "",
                "**Two-agent architecture (this repo):**",
                "",
                "```text",
                "┌─────────────────────────┐     A2A HTTP      ┌──────────────────────────────┐",
                "│  research_coordinator   │ ────────────────▶ │  research_specialist         │",
                "│  (local — adk run)      │   agent card +    │  (remote — uvicorn :8001)    │",
                "│  RemoteA2aAgent         │   protocol        │  to_a2a(root_agent)          │",
                "└─────────────────────────┘                   └──────────────────────────────┘",
                "```",
                "",
                f"- **Local:** {arch.get('local', '')}",
                f"- **Remote:** {arch.get('remote', '')}",
                f"- **Flow:** {arch.get('flow', '')}",
            ]
        )

    install = a2a.get("install")
    demo = a2a.get("demo")
    card_path = a2a.get("agent_card_path", "/.well-known/agent-card.json")
    port_note = a2a.get("port_note")
    if install or demo:
        lines.extend(["", "**Run the demo:**", ""])
        if install:
            lines.append(f"```bash\n{install}\n```")
            lines.append("")
        if demo:
            lines.append(f"Demo folder: `multi_agent/{demo}/`")
            lines.append("")
            lines.append("```bash")
            lines.append(
                f"uvicorn multi_agent.{demo}.remote_research_specialist.agent:a2a_app "
                "--host localhost --port 8001"
            )
            lines.append(f"adk run multi_agent/{demo}")
            lines.append("```")
            lines.append("")
        lines.append(
            f"Verify the remote agent card: `http://localhost:8001{card_path}`"
        )
        if port_note:
            lines.append(f"- {port_note}")

    expose_methods = a2a.get("expose_methods", [])
    if expose_methods:
        lines.extend(["", "**Ways to expose an A2A agent:**", ""])
        for method in expose_methods:
            lines.append(f"#### {method['name']}")
            lines.append("")
            lines.append(f"- **Use when:** {method.get('use_when', '')}")
            if method.get("note"):
                lines.append(f"- {method['note']}")
            if method.get("command"):
                lines.extend(["", "```bash", method["command"], "```", ""])
            ref = method.get("reference")
            if ref:
                lines.append(f"[Docs]({ref})")
            lines.append("")

    cloud = a2a.get("cloud_a2a_deploy")
    if cloud:
        lines.extend(
            [
                f"#### {cloud['title']}",
                "",
                cloud.get("intro", ""),
                "",
                f"**Agent folder:** `{cloud.get('folder', '')}`",
                "",
                "**Files required:**",
                "",
                "| File | Purpose |",
                "|------|---------|",
            ]
        )
        for f in cloud.get("files", []):
            lines.append(f"| `{f['name']}` | {f['purpose']} |")

        fields = cloud.get("agent_json_fields", [])
        if fields:
            lines.extend(
                [
                    "",
                    "**agent.json fields:**",
                    "",
                    "| Field | Description |",
                    "|-------|-------------|",
                ]
            )
            for row in fields:
                lines.append(f"| `{row['field']}` | {row['description']} |")

        url_pattern = cloud.get("url_pattern")
        if url_pattern:
            lines.extend(["", f"**URL pattern:** `{url_pattern}`", ""])

        req = cloud.get("requirements")
        if req:
            lines.extend(["", "**requirements.txt:**", "", f"```\n{req}\n```", ""])

        example = cloud.get("agent_json_example")
        if example:
            lines.extend(["**agent.json example:**", "", "```json"])
            lines.append(example.rstrip())
            lines.extend(["```", ""])

        deploy_cmd = cloud.get("deploy_command")
        if deploy_cmd:
            lines.extend(["**Deploy command:**", "", "```bash", deploy_cmd, "```", ""])

        for note in cloud.get("deploy_notes", []):
            lines.append(f"- {note}")
        lines.append("")

    client = a2a.get("a2a_client")
    if client:
        lines.extend(
            [
                f"#### {client['title']}",
                "",
                client.get("intro", ""),
                "",
                "**Agent card sources:**",
                "",
                "| Source | Example | Use when |",
                "|--------|---------|----------|",
            ]
        )
        for row in client.get("agent_card_sources", []):
            lines.append(
                f"| {row['source']} | `{row['example']}` | {row['use_when']} |"
            )

        local_ex = client.get("local_file_example")
        if local_ex:
            lines.extend(
                [
                    "",
                    "**Client — local agent card file:**",
                    "",
                    "```python",
                    local_ex.rstrip(),
                    "```",
                ]
            )

        url_ex = client.get("url_example")
        if url_ex:
            lines.extend(
                [
                    "",
                    "**Client — agent card URL (this repo demo):**",
                    "",
                    "```python",
                    url_ex.rstrip(),
                    "```",
                ]
            )

        demo_card = client.get("demo_card")
        demo_consumer = client.get("demo_consumer")
        if demo_card or demo_consumer:
            lines.append("")
            if demo_card:
                lines.append(f"Sample card: `{demo_card}`")
            if demo_consumer:
                lines.append(f"Consumer demo: `{demo_consumer}`")
        ref = client.get("reference")
        if ref:
            lines.append(f"[ADK consuming docs]({ref})")
        lines.append("")

    refs = [
        ("A2A protocol", a2a.get("official_site")),
        ("ADK A2A overview", a2a.get("adk_docs")),
        ("Exposing an agent", a2a.get("exposing_docs")),
        ("Consuming a remote agent", a2a.get("consuming_docs")),
    ]
    link_lines = [f"- [{label}]({url})" for label, url in refs if url]
    if link_lines:
        lines.extend(["", "**References:**", ""])
        lines.extend(link_lines)
    lines.append("")
    return lines


def render_custom_agents_docs(custom: dict) -> list[str]:
    lines = [
        f"### {custom['title']}",
        "",
        custom["rule_of_thumb"],
        "",
        "**Rare scenarios requiring custom logic:**",
        "",
    ]
    for item in custom.get("when_needed", []):
        lines.append(f"- **{item['name']}** — `{item['example']}`")
        lines.append(f"  - {item['why']}")
    lines.extend(["", "**Decision framework:**", ""])
    for step in custom.get("decision_framework", []):
        if "question" in step:
            lines.append(f"1. {step['question']}")
            if step.get("yes"):
                lines.append(f"   - YES → {step['yes']}")
            if step.get("no"):
                lines.append(f"   - NO → {step['no']}")
            if step.get("simple"):
                lines.append(f"   - Simple if/else → {step['simple']}")
            if step.get("complex"):
                lines.append(f"   - Complex logic → {step['complex']}")
    lines.extend(
        [
            "",
            "**Trade-offs:**",
            "",
            "| Factor | Workflow agents | Custom agents |",
            "|--------|-----------------|---------------|",
        ]
    )
    for row in custom.get("tradeoffs", []):
        lines.append(
            f"| {row['factor']} | {row['workflow']} | {row['custom']} |"
        )
    preview = custom.get("preview_pattern")
    demo = custom.get("demo")
    if preview:
        lines.extend(["", f"**Preview pattern:** {preview}"])
    if demo:
        lines.append(f"Demo: `multi_agent/{demo}/`")
    ref = custom.get("reference")
    if ref:
        lines.append(f"[ADK custom agents docs]({ref})")
    lines.append("")
    lines.extend(
        [
            "```python",
            "class ConditionalRouter(BaseAgent):",
            '    async def _run_async_impl(self, ctx):',
            "        request_type = ctx.session.state.get('request_type')",
            "        if request_type == 'billing':",
            "            async for event in self.find_sub_agent('billing').run_async(ctx):",
            "                yield event",
            "        else:",
            "            async for event in self.find_sub_agent('general').run_async(ctx):",
            "                yield event",
            "```",
            "",
        ]
    )
    return lines


def render_state_namespaces_workflow_docs(ns: dict) -> list[str]:
    lines = [
        f"### {ns['title']}",
        "",
        ns["intro"],
        "",
        "| Namespace | Workflow use | Examples |",
        "|-----------|--------------|----------|",
    ]
    for row in ns.get("namespaces", []):
        prefix = row["prefix"]
        examples = ", ".join(f"`{e}`" for e in row.get("examples", []))
        lines.append(
            f"| {prefix} | {row['workflow_use']} | {examples} |"
        )
    lines.extend(["", "**Parallel state coordination:**", ""])
    for rule in ns.get("parallel_rules", []):
        lines.append(f"- {rule}")
    demo = ns.get("demo")
    if demo:
        lines.append(f"- Demo: `multi_agent/{demo}/`")
    ref = ns.get("reference")
    if ref:
        lines.append(f"- [ADK state docs]({ref})")
    lines.extend(["", "**Test scenarios:**", ""])
    for scenario in ns.get("test_scenarios", []):
        lines.append(f"#### {scenario['name']}")
        lines.append("")
        lines.append("**You:**")
        lines.append("")
        for line in scenario["query"].strip().splitlines():
            lines.append(f"> {line.strip()}")
        lines.append("")
        lines.append("**Expected:**")
        for i, step in enumerate(scenario.get("expected", []), 1):
            lines.append(f"{i}. {step}")
        lines.append("")
    return lines


def render_deployment_docs(deploy: dict) -> list[str]:
    lines = [
        f"### {deploy['title']}",
        "",
        deploy["intro"],
        "",
        "**Local vs cloud:**",
        "",
        "| Factor | Local (`adk web`) | Cloud (Agent Engine / Cloud Run) |",
        "|--------|-------------------|----------------------------------|",
    ]
    for row in deploy.get("local_vs_cloud", []):
        lines.append(f"| {row['factor']} | {row['local']} | {row['cloud']} |")

    lines.extend(["", "**Deploy commands:**", ""])
    for platform in deploy.get("platforms", []):
        lines.extend(
            [
                f"#### {platform['name']}",
                "",
                platform.get("tagline", ""),
                "",
                f"- **Languages:** {platform.get('languages', '')}",
                f"- **Session:** {platform.get('session_service', '')}",
                "",
                "```bash",
                platform.get("command", ""),
                "```",
                "",
                "**Best for:**",
            ]
        )
        for item in platform.get("best_for", []):
            lines.append(f"- {item}")
        lines.append("")

    lines.extend(
        [
            "**Comparison:**",
            "",
            "| Factor | Agent Engine | Cloud Run |",
            "|--------|--------------|-----------|",
        ]
    )
    for row in deploy.get("comparison", []):
        lines.append(
            f"| {row['factor']} | {row['agent_engine']} | {row['cloud_run']} |"
        )

    rec = deploy.get("recommendation")
    if rec:
        lines.extend(["", f"**Recommendation:** {rec}"])

    prereqs = deploy.get("prerequisites", [])
    if prereqs:
        lines.extend(["", "**Prerequisites:**", ""])
        for item in prereqs:
            lines.append(f"- {item}")

    demo = deploy.get("demo")
    if demo:
        lines.extend(
            [
                "",
                f"**Hands-on:** `deployment/{demo}/` — see steps in Hands-on below.",
            ]
        )

    refs = [
        ("ADK deployment overview", deploy.get("adk_docs")),
        ("Agent Engine", deploy.get("agent_engine_docs")),
        ("Cloud Run", deploy.get("cloud_run_docs")),
    ]
    link_lines = [f"- [{label}]({url})" for label, url in refs if url]
    if link_lines:
        lines.extend(["", "**References:**", ""])
        lines.extend(link_lines)
    lines.append("")
    return lines


def render_film_concept_workflow_docs(film: dict) -> list[str]:
    arch_note = film.get("architecture_note", "")
    lines = [
        f"### {film['title']}",
        "",
        film["description"],
        "",
    ]
    if arch_note:
        lines.extend([arch_note, ""])

    lines.extend(
        [
            "**Architecture:**",
            "",
            "```mermaid",
            "flowchart TB",
            "    USER[User: Ada Lovelace] --> GREETER[greeter]",
            "    GREETER --> TEAM[film_concept_team SequentialAgent]",
            "    subgraph TEAM",
            "        subgraph LOOP[writers_room LoopAgent]",
            "            R[researcher] --> SW[screenwriter] --> C[critic]",
            "            C -.->|CRITICAL_FEEDBACK| R",
            "            R -.-> WIKI[wikipedia tool]",
            "        end",
            "        subgraph PAR[preproduction_team ParallelAgent]",
            "            BO[box_office_researcher]",
            "            CA[casting_agent]",
            "        end",
            "        FW[file_writer]",
            "    end",
            "    LOOP --> PAR",
            "    PAR --> FW",
            "    C -.->|exit_loop| PAR",
            "```",
            "",
            "**Loop iteration (sequential each pass):**",
            "",
        ]
    )
    for step in film.get("loop_flow", []):
        lines.append(f"- {step}")

    parallel_flow = film.get("parallel_flow", [])
    if parallel_flow:
        lines.extend(["", "**Parallel stage (after loop exits):**", ""])
        for step in parallel_flow:
            lines.append(f"- {step}")

    steps = film.get("steps", [])
    if steps:
        lines.extend(["", "**Agents:**", ""])
        for step in steps:
            status = step.get("status", "implemented")
            tag = " *(course extension)*" if status == "course_only" else ""
            lines.append(f"- `{step['agent']}` — {step['note']}{tag}")

    folder = film.get("folder", "film_concept_team")
    lines.extend(
        [
            "",
            f"Demo: `multi_agent/{folder}/`",
            "",
            "**State via tools (`tool_context.state`):**",
            "",
            "| State key | Written by | Read by |",
            "|-----------|------------|---------|",
        ]
    )
    for row in film.get("state_keys", []):
        lines.append(
            f"| `{row['key']}` | {row['writer']} | {row['readers']} |"
        )

    pattern = film.get("tool_state_pattern", {})
    if pattern:
        lines.extend(
            [
                "",
                f"- **Write:** `{pattern.get('write', '')}`",
                f"- **Read:** `{pattern.get('read', '')}`",
            ]
        )
        if pattern.get("exit"):
            lines.append(f"- **Exit loop:** `{pattern.get('exit', '')}`")
        if pattern.get("parallel"):
            lines.append(f"- **Parallel:** `{pattern.get('parallel', '')}`")
        if pattern.get("note"):
            lines.append(f"- {pattern.get('note', '')}")

    output = film.get("output")
    if output:
        lines.append(f"\n**Output:** `{output}`")

    ref = film.get("reference")
    if ref:
        lines.append(f"\n[ADK LoopAgent docs]({ref})")

    lines.extend(["", "**Test scenario:**", ""])
    for scenario in film.get("test_scenarios", []):
        lines.append(f"#### {scenario['name']}")
        lines.append("")
        lines.append(f"> {scenario['query']}")
        lines.append("")
        for i, step in enumerate(scenario.get("expected", []), 1):
            lines.append(f"{i}. {step}")
        lines.append("")
    return lines


def render_customer_service_app_docs(capstone: dict) -> list[str]:
    lines = [
        f"### Capstone: {capstone['title']}",
        "",
        capstone["description"],
        "",
        "**Build steps:**",
    ]
    for step in capstone.get("steps", []):
        status = "done" if step.get("status") == "implemented" else "todo"
        lines.append(f"{step['id']}. `{step['name']}` — {step['note']} (`{status}`)")
    lines.extend(
        [
            "",
            "```mermaid",
            "flowchart TB",
            "    USER[User Request] --> INTAKE[intake]",
            '    INTAKE -->|"ticket_info"| PARALLEL',
            "    subgraph PARALLEL[Parallel specialists]",
            "        BILLING[billing_researcher]",
            "        TECH[technical_researcher]",
            "    end",
            '    BILLING -->|"billing_findings"| RESPONDER[responder]',
            '    TECH -->|"technical_findings"| RESPONDER',
            "    RESPONDER --> OUTPUT[Final Response]",
            "```",
            "",
            "**State communication:**",
            "",
            "| Agent | Role | Writes to state | Reads from state |",
            "|-------|------|-----------------|------------------|",
        ]
    )
    for row in capstone.get("state_agents", []):
        writes = f"`{row['output_key']}`" if row.get("output_key") else "—"
        lines.append(
            f"| `{row['agent']}` | {row['role']} | {writes} | {row['reads']} |"
        )
    folder = capstone.get("folder", "customer_service_app_multi_agent")
    lines.extend(
        [
            "",
            f"Folder: `multi_agent/{folder}/` — "
            f"`adk run multi_agent.{folder}`",
            "",
            "**Test scenarios:**",
            "",
        ]
    )
    for scenario in capstone.get("test_scenarios", []):
        lines.append(f"#### {scenario['name']}")
        lines.append("")
        lines.append("**You:**")
        lines.append("")
        for line in scenario["query"].strip().splitlines():
            lines.append(f"> {line.strip()}")
        lines.append("")
        lines.append("**Expected flow:**")
        for i, step in enumerate(scenario.get("expected", []), 1):
            lines.append(f"{i}. {step}")
        lines.append("")
    return lines


def render_agent_entry(agent: dict, tracks: dict) -> list[str]:
    rel_path = agent_path(agent, tracks)
    adk_name = adk_agent_name(agent, tracks)
    run_cmd = agent.get("run", f"adk run {adk_name}")
    deploy_only = agent.get("deploy_only", False)

    lines = [
        f"#### `{rel_path}` — {agent['topic']}",
        "",
        f"- **Module:** {agent['module']}",
        f"- **Agent name:** `{agent['name']}`",
        f"- **ADK name:** `{adk_name}`",
    ]

    if deploy_only:
        lines.append("- **How to deploy:**")
        lines.append(f"  - Test locally: `adk run {rel_path}`")
    else:
        lines.extend(
            [
                "- **How to run:**",
                f"  - `adk run {rel_path}`",
            ]
        )

    if run_cmd.startswith("python"):
        lines.append(f"  - `{run_cmd}` (programmatic test)")
    elif not deploy_only and run_cmd != f"adk run {adk_name}" and run_cmd != f"adk run {rel_path}":
        lines.append(f"  - `{run_cmd}`")

    install_extra = agent.get("install_extra")
    if install_extra:
        lines.append(f"  - Prerequisite: `{install_extra}`")

    run_steps = agent.get("run_steps")
    if run_steps:
        for step in run_steps:
            label = step.get("label", "Step")
            command = step.get("command", "")
            lines.append(f"  - **{label}:** `{command}`")

    try_queries = agent.get("try_queries")
    if try_queries:
        lines.append("- **Try asking:**")
        for query in try_queries:
            lines.append(f'  - "{query}"')

    lines.append("- **What we learned:**")
    for item in agent["learned"]:
        lines.append(f"  - {item}")
    lines.append("")
    return lines


def render_readme(manifest: dict) -> str:
    tracks = manifest.get("tracks", {})
    agents = manifest["agents"]

    lines = [
        "# ADK Certification — Resources & Hands-on",
        "",
        "Google Agent Development Kit (ADK) learning project organized by track.",
        "Each agent folder is a self-contained demo of one concept.",
        "",
    ]

    if tracks:
        lines.extend(render_track_courses(tracks))

    lines.extend(
        [
            "## Quick start",
            "",
            "```bash",
            "python -m venv .venv",
            "source .venv/bin/activate",
            "pip install google-adk python-dotenv pyyaml",
            "pip install 'mcp>=1.0,<2'  # MCP tools (foundational/file_reader_mcp)",
            "pip install 'google-adk[a2a]'  # A2A protocol (multi_agent/a2a_demo)",
            "pip install 'google-cloud-aiplatform[adk,agent_engines]>=1.111'  # deployment/",
            "",
            "# Per agent:",
            "cp <track>/<agent_folder>/.env.example <track>/<agent_folder>/.env",
            "# Edit .env with your GOOGLE_API_KEY",
            "",
            "adk web .                                    # browse all agents",
            "adk run foundational.geography_assistant     # one agent (dot path)",
            "python foundational/geography_assistant/test_tools.py",
            "```",
            "",
            "## Project structure",
            "",
            "```text",
            "google-adk-certification-resource-and-hands-on/",
            "├── agents.yaml",
            "├── course_template.py       # shared helper (state templating)",
            "├── scripts/sync_adk_agent_docs.py",
            "├── foundational/              # Path 3545 — single-agent",
            "│   ├── simple_agent_module1/",
            "│   ├── geography_assistant/",
            "│   └── ...",
            "├── multi_agent/               # Path 3877 — multi-agent",
            "│   ├── customer_service/",
            "│   ├── sequential_pipeline/",
            "│   ├── ...",
            "│   ├── film_concept_team/       # workflow + tool state",
            "│   └── customer_service_app_multi_agent/  # capstone",
            "└── deployment/                # GCP deploy (Agent Engine, Cloud Run)",
            "    └── weather_agent/           # hands-on deploy",
            "```",
            "",
            "Sync docs after adding agents:",
            "",
            "```bash",
            "python scripts/sync_adk_agent_docs.py",
            "```",
            "",
        ]
    )

    agents_by_track: dict[str, list[dict]] = {}
    for agent in agents:
        track_id = agent.get("track", "foundational")
        agents_by_track.setdefault(track_id, []).append(agent)

    for track_id, track in tracks.items():
        track_agents = agents_by_track.get(track_id, [])
        lines.append(f"## {track['label']} (`{track['dir']}/`)")
        lines.append("")
        path_id = track.get("path_id")
        path_url = track.get("path_url")
        if path_id and path_url:
            lines.append(
                f"[Path {path_id}]({path_url}) — {track['summary']}"
            )
        elif path_url:
            lines.append(
                f"[{track['title']}]({path_url}) — {track['summary']}"
            )
        else:
            lines.append(track["summary"])
        lines.append("")

        if track_id == "foundational":
            lines.extend(render_foundational_reference(manifest))

        if track_id == "multi_agent":
            lines.extend(render_multi_agent_reference(manifest))

        if track_id == "deployment":
            deploy = manifest.get("deployment")
            if deploy:
                lines.extend(render_deployment_docs(deploy))

        if track_agents:
            section_title = "Hands-on" if track_id == "deployment" else "Agents"
            lines.append(f"### {section_title}")
            lines.append("")
            if track_id == "deployment":
                lines.append(
                    "Deploy to Google Cloud — prerequisites and commands in the section above. "
                    "Per-agent deploy steps below."
                )
            else:
                lines.append(
                    "Browse every agent in the web UI from the repo root: `adk web .` "
                    f"(select e.g. `{track['dir']}.<agent_folder>`). "
                    "Per-agent commands below."
                )
            lines.append("")
            for agent in track_agents:
                lines.extend(render_agent_entry(agent, tracks))
        else:
            empty_msg = (
                "_No agents yet — add folders under `deployment/` as you progress._"
                if track_id == "deployment"
                else "_No agents yet — add folders under `multi_agent/` as you progress._"
            )
            lines.append(empty_msg)
            lines.append("")

    lines.extend(
        [
            "## Environment & secrets",
            "",
            "- `.env` files are gitignored at the **root** (`.env`, `**/.env`) and in",
            "  **each agent folder** (`.gitignore` with `.env`).",
            "- `.env.example` templates are committed; copy to `.env` per agent.",
            "- Never commit real API keys.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    if not MANIFEST.exists():
        print(f"Missing manifest: {MANIFEST}", file=sys.stderr)
        return 1

    manifest = load_manifest()
    tracks = manifest.get("tracks", {})
    changes: list[str] = []

    if ensure_root_gitignore():
        changes.append("updated root .gitignore")

    gitignore_lines = manifest.get("gitignore_lines", [".env", ".adk/"])
    for agent in manifest["agents"]:
        track_id = agent.get("track", "foundational")
        track = tracks.get(track_id)
        if not track:
            print(f"Warning: unknown track {track_id!r} for {agent['folder']}", file=sys.stderr)
            continue

        agent_dir = ROOT / track["dir"] / agent["folder"]
        rel_path = f"{track['dir']}/{agent['folder']}"
        if not agent_dir.is_dir():
            print(f"Warning: missing agent folder: {rel_path}", file=sys.stderr)
            continue

        env_content = render_env_example(agent, manifest)
        if ensure_env_example(agent_dir, env_content):
            changes.append(f"updated {rel_path}/.env.example")

        if ensure_agent_gitignore(agent_dir, gitignore_lines):
            changes.append(f"updated {rel_path}/.gitignore")

    readme = render_readme(manifest)
    readme_changed = (
        not README.exists() or README.read_text(encoding="utf-8") != readme
    )
    README.write_text(readme, encoding="utf-8")
    if readme_changed:
        changes.append("updated README.md")

    if changes:
        print("Synced:")
        for item in changes:
            print(f"  - {item}")
    else:
        print("Already up to date.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
