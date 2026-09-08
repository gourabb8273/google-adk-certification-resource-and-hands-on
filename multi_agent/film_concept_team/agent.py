"""
Film Concept Team — workflow agents + tool_context.state

Architecture (course):
  greeter → film_concept_team (SequentialAgent)
    → writers_room (LoopAgent: researcher → screenwriter → critic)
    → preproduction_team (ParallelAgent: box office + casting)
    → file_writer

This demo implements the core sequential pipeline:
  greeter → researcher → screenwriter → file_writer

State is shared via tool_context.state in custom tools and {key?} templating.

Reference: https://google.github.io/adk-docs/agents/workflow-agents/
"""

from __future__ import annotations

import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.tools.langchain_tool import LangchainTool
from google.adk.tools.tool_context import ToolContext
from google.genai import types
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper

load_dotenv(Path(__file__).parent / ".env")

MODEL = "gemini-3.6-flash"
OUTPUT_DIR = Path(__file__).parent / "movie_pitches"

# ---------------------------------------------------------------------------
# Tools — write to session state and filesystem
# ---------------------------------------------------------------------------


def append_to_state(
    tool_context: ToolContext, field: str, response: str
) -> dict[str, str]:
    """Append text to a session state list (e.g. PROMPT, research, PLOT_OUTLINE)."""
    existing = tool_context.state.get(field, [])
    tool_context.state[field] = existing + [response]
    logging.info("[Added to %s] %s", field, response[:80])
    return {"status": "success"}


def write_file(
    tool_context: ToolContext,
    directory: str,
    filename: str,
    content: str,
) -> dict[str, str]:
    """Write pitch content to a text file under movie_pitches/."""
    base = OUTPUT_DIR if directory == "movie_pitches" else Path(directory)
    target = base / f"{filename}.txt" if not filename.endswith(".txt") else base / filename
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    logging.info("Wrote pitch file: %s", target)
    return {"status": "success", "path": str(target)}


wikipedia_tool = LangchainTool(
    tool=WikipediaQueryRun(
        api_wrapper=WikipediaAPIWrapper(),
        handle_tool_error=True,
    )
)

# ---------------------------------------------------------------------------
# Specialists
# ---------------------------------------------------------------------------

file_writer = LlmAgent(
    model=MODEL,
    name="file_writer",
    description="Creates marketing details and saves a pitch document.",
    instruction="""
INSTRUCTIONS:
- Create a marketable, contemporary movie title for the movie in PLOT_OUTLINE.
  Use an existing title from PLOT_OUTLINE or suggest a better one.
- Use write_file to save a txt file:
    - filename: the movie title
    - directory: movie_pitches
    - content: logline + synopsis/plot outline from PLOT_OUTLINE

PLOT_OUTLINE:
{PLOT_OUTLINE?}
""",
    generate_content_config=types.GenerateContentConfig(temperature=0),
    tools=[write_file],
)

screenwriter = LlmAgent(
    model=MODEL,
    name="screenwriter",
    description="Write a logline and three-act plot outline for a biopic.",
    instruction="""
INSTRUCTIONS:
Write a logline and three-act plot outline for an inspiring biopic about the
historical figure(s) in PROMPT: {PROMPT?}

- If CRITICAL_FEEDBACK exists, use it to improve the outline.
- If RESEARCH exists, use relevant details (not required to use all).
- If PLOT_OUTLINE exists, improve upon it.
- Use append_to_state to write your logline and outline to field 'PLOT_OUTLINE'.
- Summarize what you focused on in this pass.

PLOT_OUTLINE:
{PLOT_OUTLINE?}

RESEARCH:
{research?}

CRITICAL_FEEDBACK:
{CRITICAL_FEEDBACK?}
""",
    generate_content_config=types.GenerateContentConfig(temperature=0),
    tools=[append_to_state],
)

researcher = LlmAgent(
    model=MODEL,
    name="researcher",
    description="Answer research questions using Wikipedia.",
    instruction="""
PROMPT:
{PROMPT?}

PLOT_OUTLINE:
{PLOT_OUTLINE?}

CRITICAL_FEEDBACK:
{CRITICAL_FEEDBACK?}

INSTRUCTIONS:
- If CRITICAL_FEEDBACK exists, use Wikipedia to research suggestions.
- If PLOT_OUTLINE exists, use Wikipedia to add historical detail.
- Otherwise, research the person in PROMPT.
- Use append_to_state to add findings to field 'research'.
- Summarize what you learned, then use Wikipedia.
""",
    generate_content_config=types.GenerateContentConfig(temperature=0),
    tools=[wikipedia_tool, append_to_state],
)

film_concept_team = SequentialAgent(
    name="film_concept_team",
    description="Research, write a plot outline, and save a pitch file.",
    sub_agents=[researcher, screenwriter, file_writer],
)

root_agent = LlmAgent(
    model=MODEL,
    name="greeter",
    description="Guides the user in crafting a movie plot pitch.",
    instruction="""
- Tell the user you will help them write a pitch for a hit movie.
  Ask for a historical figure to base the film on.
- When they respond, use append_to_state to store their answer in the
  'PROMPT' state key, then delegate to film_concept_team.
""",
    generate_content_config=types.GenerateContentConfig(temperature=0),
    tools=[append_to_state],
    sub_agents=[film_concept_team],
)
