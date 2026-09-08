"""
Cross-session memory demo — two conversations, one memory store.

Session 1: user shares preferences → saved to memory via after_agent_callback.
Session 2: new session → agent searches memory with load_memory tool.

Run: python foundational/memory_bank/test_memory.py
"""

from google.adk.memory import InMemoryMemoryService
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part

from agent import root_agent

APP_NAME = "memory_bank_app"
USER_ID = "demo_user"
MODEL = root_agent.model


def run_turn(runner: Runner, session_id: str, message: str) -> str:
    user_message = Content(role="user", parts=[Part(text=message)])
    final_text = "(No response)"
    for event in runner.run(
        user_id=USER_ID,
        session_id=session_id,
        new_message=user_message,
    ):
        if event.is_final_response() and event.content and event.content.parts:
            final_text = event.content.parts[0].text or final_text
    return final_text


def main() -> None:
    session_service = InMemorySessionService()
    memory_service = InMemoryMemoryService()

    runner = Runner(
        agent=root_agent,
        app_name=APP_NAME,
        session_service=session_service,
        memory_service=memory_service,
    )

    # Session 1 — capture preferences (auto-saved to memory after agent responds)
    print("=" * 60)
    print("Session 1 — sharing preferences")
    print("=" * 60)
    session_service.create_session_sync(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id="session_prefs",
    )
    response1 = run_turn(
        runner,
        "session_prefs",
        "My favorite color is blue and I love hiking on weekends.",
    )
    print(f"Agent: {response1}\n")

    # Session 2 — new conversation, recall from memory bank
    print("=" * 60)
    print("Session 2 — recall from memory (new session)")
    print("=" * 60)
    session_service.create_session_sync(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id="session_recall",
    )
    response2 = run_turn(
        runner,
        "session_recall",
        "What do you remember about my hobbies and favorite color?",
    )
    print(f"Agent: {response2}\n")

    print("Cross-session memory demo complete.")
    print("In production, VertexAiMemoryBankService adds LLM extraction + semantic search.")


if __name__ == "__main__":
    main()
