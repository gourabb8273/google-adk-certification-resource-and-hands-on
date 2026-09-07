"""
Test geography assistant tools.

Run with: python test_tools.py

Examples:
  Custom tool  → "What is the capital of France?"
  Google Search → "What is the population of Tokyo today?"
"""

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part

from agent import root_agent

APP_NAME = "geography_app"
USER_ID = "user1"
SESSION_ID = "session1"

session_service = InMemorySessionService()
session_service.create_session_sync(
    app_name=APP_NAME,
    user_id=USER_ID,
    session_id=SESSION_ID,
)
runner = Runner(
    agent=root_agent,
    app_name=APP_NAME,
    session_service=session_service,
)


def ask(question: str) -> None:
    print(f"--- User: {question}")
    events = runner.run(
        user_id=USER_ID,
        session_id=SESSION_ID,
        new_message=Content(parts=[Part(text=question)]),
    )
    for event in events:
        if event.is_final_response() and event.content and event.content.parts:
            print(f"Agent: {event.content.parts[0].text}\n")


# Custom function tool (get_capital_city)
ask("What is the capital of France?")

# Built-in Google Search (via sub-agent wrapper)
ask("What is the current population of Tokyo?")
