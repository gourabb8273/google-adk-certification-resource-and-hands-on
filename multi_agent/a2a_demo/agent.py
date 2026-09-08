"""
Research Coordinator — A2A client (consume side)

Delegates research questions to a remote specialist over the A2A protocol.
The remote agent must be running before you start this coordinator.

Terminal 1 — expose the specialist:
  uvicorn multi_agent.a2a_demo.remote_research_specialist.agent:a2a_app \\
    --host localhost --port 8001

Terminal 2 — run this coordinator:
  adk run multi_agent.a2a_demo

Reference: https://google.github.io/adk-docs/a2a/quickstart-consuming/
"""

from pathlib import Path

from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.agents.remote_a2a_agent import AGENT_CARD_WELL_KNOWN_PATH
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent

load_dotenv(Path(__file__).parent / ".env")

MODEL = "gemini-3.6-flash"
REMOTE_BASE_URL = "http://localhost:8001"
AGENT_CARD_URL = f"{REMOTE_BASE_URL}{AGENT_CARD_WELL_KNOWN_PATH}"

research_specialist = RemoteA2aAgent(
    name="research_specialist",
    description="Remote research expert exposed via the A2A protocol",
    agent_card=AGENT_CARD_URL,
)

root_agent = LlmAgent(
    model=MODEL,
    name="research_coordinator",
    description="Coordinates research requests via a remote A2A specialist",
    instruction="""You are a research coordinator.

For research questions, delegate to research_specialist to gather deep analysis.
For simple greetings or clarifications, answer directly.

When delegating:
1. Pass the user's topic clearly to research_specialist
2. Present the specialist's findings in a friendly summary""",
    sub_agents=[research_specialist],
)
