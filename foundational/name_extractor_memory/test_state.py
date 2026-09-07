"""Test that output_key persists name in session state across turns."""

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part

from agent import root_agent

APP_NAME = "name_extractor_app"
USER_ID = "test_user"
SESSION_ID = "test_session"

# Setup session and runner
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


def print_final_response(events) -> None:
    for event in events:
        if event.is_final_response() and event.content and event.content.parts:
            print(f"Agent response: {event.content.parts[0].text}")


# Test: Extract name
print("--- Turn 1: Extract name ---")
user_message = Content(
    role="user",
    parts=[Part(text="Hi, my name is Alex Johnson")],
)
print_final_response(
    runner.run(
        user_id=USER_ID,
        session_id=SESSION_ID,
        new_message=user_message,
    )
)

# Access state programmatically
session = session_service.get_session_sync(
    app_name=APP_NAME,
    user_id=USER_ID,
    session_id=SESSION_ID,
)
print(f"\nFull state: {session.state}")
print(f"user_name from state: {session.state.get('user_name')}")

if session.state.get("user_name"):
    print("✓ Name successfully stored in session state!")
else:
    print("✗ Name NOT found in session state")

# Test accessing in subsequent turns
print("\n--- Turn 2: Recall name ---")
follow_up = Content(role="user", parts=[Part(text="What's my name?")])
print_final_response(
    runner.run(
        user_id=USER_ID,
        session_id=SESSION_ID,
        new_message=follow_up,
    )
)

session = session_service.get_session_sync(
    app_name=APP_NAME,
    user_id=USER_ID,
    session_id=SESSION_ID,
)
if session.state.get("user_name"):
    print("State persists across turns!")
