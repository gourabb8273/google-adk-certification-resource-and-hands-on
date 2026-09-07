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
        link = f"[{track['title']}]({track['path_url']})"
        lines.append(
            f"| `{track['dir']}/` — {track['label']} | {link} | {track['summary']} |"
        )
    lines.append("")

    for track in tracks.values():
        lines.append(
            f"- **{track['label']}** (`{track['dir']}/`): "
            f"[Path {track['path_id']}]({track['path_url']})"
        )
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

    return lines


def render_agent_entry(agent: dict, tracks: dict) -> list[str]:
    rel_path = agent_path(agent, tracks)
    adk_name = adk_agent_name(agent, tracks)
    lines = [
        f"#### `{rel_path}` — {agent['topic']}",
        "",
        f"- **Module:** {agent['module']}",
        f"- **Agent name:** `{agent['name']}`",
        f"- **ADK name:** `{adk_name}`",
        f"- **Run:** `{agent['run']}`",
        "- **What we learned:**",
    ]
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
            "└── multi_agent/               # Path 3877 — multi-agent",
            "    └── (agents added as you learn)",
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
        lines.append(
            f"[Path {track['path_id']}]({track['path_url']}) — {track['summary']}"
        )
        lines.append("")

        if track_id == "foundational":
            lines.extend(render_foundational_reference(manifest))

        if track_agents:
            lines.append("### Agents")
            lines.append("")
            for agent in track_agents:
                lines.extend(render_agent_entry(agent, tracks))
        else:
            lines.append("_No agents yet — add folders under `multi_agent/` as you progress._")
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
