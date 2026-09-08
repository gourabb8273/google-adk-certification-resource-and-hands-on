"""
Refinement Loop Example

Draft, then check quality and improve in a loop (up to max_iterations).

Reference: https://google.github.io/adk-docs/agents/workflow-agents/loop-agents/
"""

from pathlib import Path

from dotenv import load_dotenv
from google.adk.agents import LlmAgent, LoopAgent, SequentialAgent

load_dotenv(Path(__file__).parent / ".env")

MODEL = "gemini-3.6-flash"

drafter = LlmAgent(
    model=MODEL,
    name="drafter",
    output_key="draft",
    instruction="Write a short paragraph about the given topic.",
)

checker = LlmAgent(
    model=MODEL,
    name="checker",
    output_key="feedback",
    instruction="Rate this draft 1-10 and give feedback: {draft}",
)

improver = LlmAgent(
    model=MODEL,
    name="improver",
    output_key="draft",
    instruction="Improve the draft based on feedback: {feedback}",
)

refinement = LoopAgent(
    name="refinement",
    sub_agents=[checker, improver],
    max_iterations=2,
)

root_agent = SequentialAgent(
    name="writing_pipeline",
    sub_agents=[drafter, refinement],
)
