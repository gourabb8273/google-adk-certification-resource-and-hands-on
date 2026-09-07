"""
Personalized Greeter - Demonstrates State Templating

Reference: https://google.github.io/adk-docs/sessions/state.md
"""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.agents.readonly_context import ReadonlyContext

from course_template import resolve_course_template

load_dotenv(Path(__file__).parent / ".env")

INSTRUCTION = """You are a friendly assistant.

User information:
- Name: {user_name?there}
- Preferred language: {user_language?English}
- Membership: {membership_tier?free}

{membership_tier?Your membership level is: {membership_tier}}

Greet the user warmly and offer assistance.
Respond in {user_language?English}."""


async def _instruction(ctx: ReadonlyContext) -> str:
    return resolve_course_template(
        INSTRUCTION, dict(ctx._invocation_context.session.state)
    )


root_agent = LlmAgent(
    model="gemini-3.6-flash",
    name="personalized_greeter",
    instruction=_instruction,
)
