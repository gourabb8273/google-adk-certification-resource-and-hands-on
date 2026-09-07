"""
Geography Assistant Agent

Demonstrates ADK's tools parameter with a custom function tool and Google Search.

Reference: https://google.github.io/adk-docs/agents/llm-agents#tools
"""

from pathlib import Path

from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.tools.google_search_tool import GoogleSearchTool

load_dotenv(Path(__file__).parent / ".env")


# Step 1: Custom function tool
def get_capital_city(country: str) -> str:
    """Retrieves the capital city for a specified country.

    Args:
        country: The name of the country.

    Returns:
        The capital city name or an error message.
    """
    capitals = {
        "france": "Paris",
        "japan": "Tokyo",
        "canada": "Ottawa",
        "germany": "Berlin",
        "brazil": "Brasília",
        "australia": "Canberra",
        "india": "New Delhi",
        "mexico": "Mexico City",
    }
    return capitals.get(
        country.lower(),
        f"Sorry, I don't have information about the capital of {country}.",
    )


# Built-in Google Search — cannot share an agent with function tools directly.
# bypass_multi_tools_limit=True wraps it as a sub-agent (GoogleSearchAgentTool).
google_search_tool = GoogleSearchTool(bypass_multi_tools_limit=True)

# Step 2: Agent with custom + built-in tools
root_agent = LlmAgent(
    model="gemini-3.6-flash",
    name="geography_assistant",
    description="Helps users learn about world geography.",
    instruction="""You are a geography assistant that helps users learn about world capitals and geography.

When a user asks about a capital city:
1. Use the get_capital_city tool to find the answer
2. Provide the information in a friendly, educational way
3. You can add interesting facts if you know them

When get_capital_city does not have the country, or the user asks about current
events, population, or other live facts, use the google_search tool.

If a tool returns an error message, politely tell the user you don't have that information.""",
    tools=[get_capital_city, google_search_tool],
)

# Built-in-only pattern (use alone on its own agent):
# from google.adk.tools.google_search_tool import google_search
# search_only_agent = LlmAgent(
#     model="gemini-3.6-flash",
#     name="search_only_agent",
#     tools=[google_search],  # no custom function tools on same agent
# )
