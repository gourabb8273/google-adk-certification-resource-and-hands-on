"""
Sequential Pipeline Example

Each step depends on the previous step's output.

Reference: https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/
"""

from pathlib import Path

from dotenv import load_dotenv
from google.adk.agents import LlmAgent, SequentialAgent

load_dotenv(Path(__file__).parent / ".env")

MODEL = "gemini-3.6-flash"

intake = LlmAgent(
    model=MODEL,
    name="intake",
    output_key="request",
    instruction="Extract and summarize the user request.",
)

analyzer = LlmAgent(
    model=MODEL,
    name="analyzer",
    output_key="analysis",
    instruction="Analyze this request: {request}",
)

responder = LlmAgent(
    model=MODEL,
    name="responder",
    instruction="Respond to the user based on: {analysis}",
)

root_agent = SequentialAgent(
    name="request_pipeline",
    sub_agents=[intake, analyzer, responder],
)
