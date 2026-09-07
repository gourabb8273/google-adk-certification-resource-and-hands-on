"""
Namespace Demo - Shows all four state namespaces

Demonstrates temp:, session, user:, and app: persistence scopes.

Reference: https://google.github.io/adk-docs/sessions/state.md
"""

from pathlib import Path
import sys

# Allow importing shared course_template from repo root
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.agents.readonly_context import ReadonlyContext

from course_template import resolve_course_template

load_dotenv(Path(__file__).parent / ".env")

INSTRUCTION = """You are a demo assistant showing state namespaces.

=== App State (global for all users) ===
App name: {app:name?Namespace Demo}
App version: {app:version?1.0}

=== User State (persists across sessions) ===
User preference: {user:theme?not set}

=== Session State (persists this conversation) ===
Conversation topic: {topic?not set}

=== Temp State (current turn only) ===
Current step: {temp:step?not set}

Respond with a friendly message showing these namespace values."""


async def _instruction(ctx: ReadonlyContext) -> str:
    return resolve_course_template(
        INSTRUCTION, dict(ctx._invocation_context.session.state)
    )


root_agent = LlmAgent(
    model="gemini-3.6-flash",
    name="namespace_demo",
    instruction=_instruction,
    output_key="response",
)
