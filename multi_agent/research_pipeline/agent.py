"""
Research-to-Article Pipeline

Demonstrates agent communication via output_key and state templating.

Reference: https://google.github.io/adk-docs/agents/multi-agents#communication
"""

from pathlib import Path

from dotenv import load_dotenv
from google.adk.agents import LlmAgent, SequentialAgent

load_dotenv(Path(__file__).parent / ".env")

MODEL = "gemini-3.6-flash"

researcher = LlmAgent(
    model=MODEL,
    name="researcher",
    output_key="research_findings",
    instruction="""Research the given topic thoroughly.

Provide:
- 3-5 key facts
- Important statistics or data
- Current trends or developments

Be factual and informative.""",
)

writer = LlmAgent(
    model=MODEL,
    name="writer",
    output_key="draft_article",
    instruction="""Write a short article based on this research:

{research_findings}

Structure:
- Engaging introduction
- Key findings (2-3 paragraphs)
- Brief conclusion

Keep it under 300 words.""",
)

editor = LlmAgent(
    model=MODEL,
    name="editor",
    instruction="""Edit and polish this article:

{draft_article}

Fix any grammar issues, improve flow, and ensure clarity.
Return the final polished version.""",
)

root_agent = SequentialAgent(
    name="article_pipeline",
    sub_agents=[researcher, writer, editor],
)
