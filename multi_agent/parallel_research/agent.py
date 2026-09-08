"""
Parallel Research Example

Two researchers run simultaneously, then a summarizer combines results.

Reference: https://google.github.io/adk-docs/agents/workflow-agents/parallel-agents/
"""

from pathlib import Path

from dotenv import load_dotenv
from google.adk.agents import LlmAgent, ParallelAgent, SequentialAgent

load_dotenv(Path(__file__).parent / ".env")

MODEL = "gemini-3.6-flash"

researcher_benefits = LlmAgent(
    model=MODEL,
    name="benefits_researcher",
    output_key="benefits",
    instruction="Research the benefits of renewable energy.",
)

researcher_challenges = LlmAgent(
    model=MODEL,
    name="challenges_researcher",
    output_key="challenges",
    instruction="Research the challenges of renewable energy.",
)

parallel_research = ParallelAgent(
    name="research",
    sub_agents=[researcher_benefits, researcher_challenges],
)

summarizer = LlmAgent(
    model=MODEL,
    name="summarizer",
    instruction="Summarize: Benefits: {benefits}, Challenges: {challenges}",
)

root_agent = SequentialAgent(
    name="research_pipeline",
    sub_agents=[parallel_research, summarizer],
)
