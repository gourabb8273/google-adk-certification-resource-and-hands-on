"""
Test state namespaces to see persistence differences.

Run with: python test_namespaces.py

Namespace lifetimes:
  temp:step     → current turn only (discarded after invocation)
  topic         → current session only (lost when session ends)
  user:theme    → all sessions for this user
  app:version   → global for all users of this app
"""

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part

from agent import root_agent

APP_NAME = "namespace_demo_app"
USER_ID = "user1"
SESSION1 = "session1"
SESSION2 = "session2"


def get_merged_state(session_service, session_id: str) -> dict:
    session = session_service.get_session_sync(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=session_id,
    )
    return session.state if session else {}


def print_namespace_state(label: str, state: dict) -> None:
    print(label)
    print(f"  Full merged state: {state}")
    print(f"  temp:step  → {state.get('temp:step')!r}  (turn-only)")
    print(f"  topic      → {state.get('topic')!r}  (session-only)")
    print(f"  user:theme → {state.get('user:theme')!r}  (user-scoped)")
    print(f"  app:version→ {state.get('app:version')!r}  (app-scoped)")
    print()


def run_turn(runner, session_id: str, message: str, state_delta: dict | None = None):
    events = runner.run(
        user_id=USER_ID,
        session_id=session_id,
        new_message=Content(parts=[Part(text=message)]),
        state_delta=state_delta,
    )
    for event in events:
        if event.is_final_response() and event.content and event.content.parts:
            print(f"Agent: {event.content.parts[0].text}\n")
    return events


# Setup
session_service = InMemorySessionService()
session_service.create_session_sync(
    app_name=APP_NAME,
    user_id=USER_ID,
    session_id=SESSION1,
    state={
        "app:name": "Namespace Demo",
        "app:version": "2.0",
        "user:theme": "dark",
        "topic": "refunds",
    },
)
runner = Runner(
    agent=root_agent,
    app_name=APP_NAME,
    session_service=session_service,
)

# Turn 1 — include temp: state for this invocation only
print("=== Turn 1: set all namespaces (temp via state_delta) ===")
run_turn(
    runner,
    SESSION1,
    "Show me the namespace values",
    state_delta={"temp:step": "validation"},
)
print_namespace_state("After Turn 1:", get_merged_state(session_service, SESSION1))

# Turn 2 — same session, no new temp: state
print("=== Turn 2: same session, no temp: in state_delta ===")
run_turn(runner, SESSION1, "Check state again")
print_namespace_state("After Turn 2:", get_merged_state(session_service, SESSION1))

# New session — same user, session-scoped data should reset
print("=== New session (session2) — same user ===")
session_service.create_session_sync(
    app_name=APP_NAME,
    user_id=USER_ID,
    session_id=SESSION2,
)
print_namespace_state(
    "New session2 (before any message):",
    get_merged_state(session_service, SESSION2),
)

run_turn(runner, SESSION2, "What persisted from my last session?")
print_namespace_state(
    "After message in session2:",
    get_merged_state(session_service, SESSION2),
)

print("=== Summary ===")
print("  temp:step   — gone after turn ends (not in state_delta on Turn 2)")
print("  topic       — gone in session2 (session-scoped)")
print("  user:theme  — still dark in session2 (user-scoped)")
print("  app:version — still 2.0 in session2 (app-scoped)")
