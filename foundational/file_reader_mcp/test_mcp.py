"""
Test MCP filesystem tools.

Prerequisites: Node.js and npm (for npx)

Run with: python test_mcp.py
"""

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part

from agent import root_agent

APP_NAME = "file_reader_app"
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


ask("List all files in the allowed folder.")
ask("Read the contents of hello.txt")
