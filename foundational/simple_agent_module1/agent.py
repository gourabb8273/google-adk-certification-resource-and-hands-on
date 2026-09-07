# from google.adk.agents.llm_agent import Agent

# root_agent = Agent(
#     model='gemini-3.6-flash',
#     name='root_agent',
#     description='A helpful assistant for user questions.',
#     instruction='Answer user questions to the best of your knowledge',
# )

# module 2
# from google.adk.agents.llm_agent import Agent

# root_agent = Agent(
#     model='gemini-3.6-flash',
#     name='math_tutor_agent',  # More specific internal name
#     description='Helps students learn algebra by guiding them through problemsolving steps.',
#     instruction='You are a patient math tutor. Help students with algebra problems.',
# )

# module 3

"""
Complete example: Running an ADK agent programmatically

Install:
    pip install google-adk

Set your API key:
    export GOOGLE_API_KEY=your-api-key-here

Or set it in Python:
    os.environ["GOOGLE_API_KEY"] = "your-api-key-here"
"""

import asyncio
import os
from pathlib import Path

from dotenv import load_dotenv
from google.adk.agents.llm_agent import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part


# Step 1: Load config from .env
load_dotenv(Path(__file__).parent / ".env")


def get_session_state_from_env() -> dict:
    """Build initial session state from environment variables."""
    return {
        "google_genai_use_vertexai": os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "0"),
    }


# Step 2: Define your agent
agent = Agent(
    model="gemini-3.6-flash",
    name="math_tutor",
    instruction="""You are a patient math tutor.
Guide students through problems step-by-step.
Don't just give answers - help them discover solutions."""
)


# Step 3: Create a session service
session_service = InMemorySessionService()


# Step 4: Create a runner
runner = Runner(
    agent=agent,
    app_name="math_tutor_app",
    session_service=session_service,
)


# Step 5: Run the agent
async def run_agent():
    user_id = "user_1"
    session_id = "session_1"

    # Create a session with initial state from .env
    await session_service.create_session(
        app_name="math_tutor_app",
        user_id=user_id,
        session_id=session_id,
        state=get_session_state_from_env(),
    )

    # User message
    user_message = Content(
        role="user",
        parts=[
            Part(text="What is 2x + 5 = 13?")
        ],
    )

    # Run the agent
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=user_message,
    ):
        # Print only the final response
        if event.is_final_response():
            if event.content and event.content.parts:
                print(event.content.parts[0].text)


# Step 6: Run
if __name__ == "__main__":
    asyncio.run(run_agent())