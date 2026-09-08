"""
Memory Bank — cross-session memory sharing

Session state = what's happening THIS conversation.
Memory Bank = what the agent learned ACROSS ALL conversations.

Local demo uses InMemoryMemoryService (same API pattern as production
VertexAiMemoryBankService). In production, Memory Bank is a managed GCP
service with LLM-powered extraction and semantic search.

Reference: https://google.github.io/adk-docs/sessions/memory/
"""

from pathlib import Path

from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.tools import load_memory

load_dotenv(Path(__file__).parent / ".env")

MODEL = "gemini-3.6-flash"


async def auto_save_session_to_memory(callback_context) -> None:
    """Save conversation to memory after each turn (automatic via callback)."""
    await callback_context.add_session_to_memory()


root_agent = LlmAgent(
    model=MODEL,
    name="memory_assistant",
    description="Personal assistant that remembers preferences across sessions",
    instruction="""You are a helpful personal assistant with long-term memory.

When users share preferences, interests, or facts about themselves, acknowledge them warmly.
When users ask about past information, use the load_memory tool to search previous conversations
before answering.

If memory has relevant context, use it naturally in your response.""",
    tools=[load_memory],
    after_agent_callback=auto_save_session_to_memory,
)
