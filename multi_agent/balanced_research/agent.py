"""
Balanced Research System

Demonstrates Sequential + Parallel workflow with proper state coordination.
Parallel researchers gather benefits and challenges; summarizer aggregates both.

Reference: https://google.github.io/adk-docs/agents/workflow-agents
"""

from pathlib import Path

from dotenv import load_dotenv
from google.adk.agents import LlmAgent, ParallelAgent, SequentialAgent

load_dotenv(Path(__file__).parent / ".env")

MODEL = "gemini-3.6-flash"

# =============================================================================
# PARALLEL STAGE: Two researchers run at the same time
# =============================================================================

benefits_researcher = LlmAgent(
    model=MODEL,
    name="benefits_researcher",
    output_key="benefits",
    instruction="""Research the BENEFITS of the given topic.

Provide:
- 3-5 key advantages
- Supporting evidence
- Real-world examples""",
)

challenges_researcher = LlmAgent(
    model=MODEL,
    name="challenges_researcher",
    output_key="challenges",
    instruction="""Research the CHALLENGES of the given topic.

Provide:
- 3-5 key challenges
- Why these matter
- Potential mitigations""",
)

parallel_research = ParallelAgent(
    name="parallel_research",
    sub_agents=[benefits_researcher, challenges_researcher],
)

# =============================================================================
# SEQUENTIAL STAGE: Aggregator combines parallel results
# =============================================================================

summarizer = LlmAgent(
    model=MODEL,
    name="summarizer",
    instruction="""Create a balanced summary using both research perspectives:

BENEFITS:
{benefits}

CHALLENGES:
{challenges}

Your summary should:
- Present both sides fairly
- Highlight trade-offs
- Provide a balanced conclusion""",
)

# =============================================================================
# COMPLETE WORKFLOW: Parallel research → Sequential summary
# =============================================================================

root_agent = SequentialAgent(
    name="balanced_research",
    sub_agents=[parallel_research, summarizer],
)
