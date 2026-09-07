"""
Name Extractor - Demonstrates Session State Basics

Shows how to use output_key to save data and access it via session.state.

Reference: https://google.github.io/adk-docs/sessions/state.md
"""

from pathlib import Path

from dotenv import load_dotenv
from google.adk.agents import LlmAgent

load_dotenv(Path(__file__).parent / ".env")

# Single agent that extracts and saves name
root_agent = LlmAgent(
    model="gemini-3.6-flash",
    name="name_extractor",
    instruction=(
        "Extract the person's name from the message. "
        "Return ONLY the name, nothing else."
    ),
    output_key="user_name",  # Saves response to state["user_name"]
)
