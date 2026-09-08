"""
Simple Weather Agent — Agent Engine deployment hands-on

Deploy:
  adk deploy agent_engine \\
    --project=$GOOGLE_CLOUD_PROJECT \\
    --region=us-central1 \\
    --staging_bucket=gs://$BUCKET_NAME \\
    --display_name="Weather Agent" \\
    deployment/weather_agent

Test locally first:
  adk run deployment/weather_agent

Reference: https://google.github.io/adk-docs/deploy/agent-engine/
"""

from pathlib import Path

from dotenv import load_dotenv
from google.adk.agents import LlmAgent

load_dotenv(Path(__file__).parent / ".env")

root_agent = LlmAgent(
    model="gemini-3.6-flash",
    name="weather_agent",
    description="Provides weather information and forecasts",
    instruction="""You are a helpful weather assistant.

When users ask about weather:
1. Ask for the city if not provided
2. Provide weather information (simulated for this demo)
3. Be friendly and concise

Example: "The current weather in San Francisco is 68°F (20°C) with partly cloudy skies."

Note: This demo uses simulated weather. In production, integrate a real weather API.""",
)
