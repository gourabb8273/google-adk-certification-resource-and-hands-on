"""
Research Specialist — A2A server (expose side)

This agent runs as a separate process and is consumed by the coordinator
via the Agent2Agent (A2A) protocol.

Start the server (local):
  uvicorn multi_agent.a2a_demo.remote_research_specialist.agent:a2a_app \\
    --host localhost --port 8001

Deploy as A2A server (Cloud Run):
  See agent.json + requirements.txt in this folder.
  adk deploy cloud_run --project=$GOOGLE_CLOUD_PROJECT \\
    --region=us-central1 --service_name=research-specialist --a2a .

Agent card (local): http://localhost:8001/.well-known/agent-card.json
Agent card (cloud): agent.json url field after deploy

Reference: https://google.github.io/adk-docs/a2a/quickstart-exposing/
"""

from pathlib import Path

from dotenv import load_dotenv
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.adk.agents import LlmAgent

load_dotenv(Path(__file__).parent.parent / ".env")

MODEL = "gemini-3.6-flash"
A2A_PORT = 8001

root_agent = LlmAgent(
    model=MODEL,
    name="research_specialist",
    description="Deep research on topics — trends, facts, and key points",
    instruction="""You are a research specialist.

When given a topic, provide:
1. A brief overview (2–3 sentences)
2. Three key facts or trends
3. One practical implication

Be factual and concise. Structure your answer clearly.""",
)

# ADK auto-generates an agent card from this agent's metadata.
a2a_app = to_a2a(root_agent, host="localhost", port=A2A_PORT)
