"""
Configurable Document Processor

Demonstrates state namespaces in multi-agent workflows:
- Session state for pipeline outputs (document_content, topics, sentiment, summary)
- user: namespace for summary format preferences

Reference: https://google.github.io/adk-docs/sessions/state
"""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from dotenv import load_dotenv
from google.adk.agents import LlmAgent, ParallelAgent, SequentialAgent
from google.adk.agents.readonly_context import ReadonlyContext

from course_template import resolve_course_template

load_dotenv(Path(__file__).parent / ".env")

MODEL = "gemini-3.6-flash"

# =============================================================================
# STAGE 1: Intake — extract document content (session state)
# =============================================================================

intake_agent = LlmAgent(
    model=MODEL,
    name="intake",
    output_key="document_content",
    instruction="""Extract and structure the document content from the user's input.

Return a clean, structured version of the content.""",
)

# =============================================================================
# STAGE 2: Parallel analysis — topics + sentiment (distinct output_key each)
# =============================================================================

topic_analyzer = LlmAgent(
    model=MODEL,
    name="topic_analyzer",
    output_key="topics",
    instruction="""Analyze the document for main topics:

{document_content}

Return the top 3-5 topics.""",
)

sentiment_analyzer = LlmAgent(
    model=MODEL,
    name="sentiment_analyzer",
    output_key="sentiment",
    instruction="""Analyze the document sentiment:

{document_content}

Return: positive, negative, or neutral with explanation.""",
)

parallel_analysis = ParallelAgent(
    name="parallel_analysis",
    sub_agents=[topic_analyzer, sentiment_analyzer],
)

# =============================================================================
# STAGE 3: Summary — respects user:summary_format preference
# =============================================================================

SUMMARIZER_INSTRUCTION = """Create a document summary.

Document content: {document_content}
Topics identified: {topics}
Sentiment: {sentiment}

User preference for format: {user:summary_format?bullet points}

Create summary matching the user's preferred format."""


async def _summarizer_instruction(ctx: ReadonlyContext) -> str:
    return resolve_course_template(
        SUMMARIZER_INSTRUCTION, dict(ctx._invocation_context.session.state)
    )


summarizer = LlmAgent(
    model=MODEL,
    name="summarizer",
    output_key="summary",
    instruction=_summarizer_instruction,
)

# =============================================================================
# COMPLETE WORKFLOW
# =============================================================================

root_agent = SequentialAgent(
    name="document_processor",
    sub_agents=[intake_agent, parallel_analysis, summarizer],
)
