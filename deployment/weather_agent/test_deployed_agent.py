"""
Test a deployed weather agent on Vertex AI Agent Engine.

Before running:
1. Deploy with adk deploy agent-engine (see README)
2. Set REASONING_ENGINE_RESOURCE in .env to your resource name, e.g.:
   projects/PROJECT/locations/us-central1/reasoningEngines/123456789

Or pass as first argument:
  python test_deployed_agent.py projects/.../reasoningEngines/123456789
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

from google.cloud import aiplatform


def main() -> int:
    project = os.environ.get("GOOGLE_CLOUD_PROJECT")
    location = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
    resource_name = (
        sys.argv[1] if len(sys.argv) > 1 else os.environ.get("REASONING_ENGINE_RESOURCE")
    )

    if not project:
        print("Set GOOGLE_CLOUD_PROJECT in .env", file=sys.stderr)
        return 1
    if not resource_name:
        print(
            "Set REASONING_ENGINE_RESOURCE in .env or pass resource name as argument",
            file=sys.stderr,
        )
        return 1

    aiplatform.init(project=project, location=location)
    remote_app = aiplatform.ReasoningEngine(resource_name)

    queries = [
        "What's the weather in San Francisco?",
        "Will it rain tomorrow in Seattle?",
    ]

    for i, query in enumerate(queries, 1):
        print("=" * 60)
        print(f"Test {i}: {query}")
        print("=" * 60)
        response = remote_app.query(input=query)
        print(f"Agent: {response}\n")

    print("Deployed agent working successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
