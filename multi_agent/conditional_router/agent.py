"""
Conditional Router — Custom Agent Preview

Rare scenarios requiring custom logic that workflow agents cannot handle:
- Conditional skipping (IF condition THEN skip Agent B)
- Dynamic routing (IF billing → billing_agent ELSE general_agent)
- Complex early exit (IF quality_score > 8 THEN exit loop)

Default to workflow agents first. Use BaseAgent only when Sequential,
Parallel, and Loop cannot express your conditional logic.

Reference: https://google.github.io/adk-docs/agents/custom-agents
"""

from collections.abc import AsyncGenerator
from pathlib import Path

from dotenv import load_dotenv
from google.adk.agents import BaseAgent, LlmAgent, SequentialAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events.event import Event

load_dotenv(Path(__file__).parent / ".env")

MODEL = "gemini-3.6-flash"

# ---------------------------------------------------------------------------
# Specialists (routed to by custom agent)
# ---------------------------------------------------------------------------

billing_specialist = LlmAgent(
    model=MODEL,
    name="billing_specialist",
    description="Handles billing, refunds, and subscription issues",
    instruction="""You are a billing specialist.

Help with charges, refunds, subscriptions, and invoices.
Be clear about policies and next steps.""",
)

general_specialist = LlmAgent(
    model=MODEL,
    name="general_specialist",
    description="Handles general customer inquiries",
    instruction="""You are a general customer support specialist.

Answer product and account questions helpfully and concisely.""",
)

# ---------------------------------------------------------------------------
# Step 1: Classifier writes request_type to session state
# ---------------------------------------------------------------------------

classifier = LlmAgent(
    model=MODEL,
    name="classifier",
    output_key="request_type",
    instruction="""Classify the customer request as either billing or general.

Reply with exactly one word: billing or general

- billing: charges, refunds, subscriptions, invoices, payments
- general: everything else""",
)

# ---------------------------------------------------------------------------
# Step 2: Custom agent — conditional routing via _run_async_impl
# ---------------------------------------------------------------------------


class ConditionalRouter(BaseAgent):
    """Custom agent with if/else logic — workflow agents cannot skip or branch."""

    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        request_type = str(ctx.session.state.get("request_type", "general")).lower()

        if "billing" in request_type:
            agent = self.find_sub_agent("billing_specialist")
        else:
            agent = self.find_sub_agent("general_specialist")

        if agent is None:
            raise ValueError("Routing failed: specialist sub-agent not found")

        async for event in agent.run_async(ctx):
            yield event


router = ConditionalRouter(
    name="conditional_router",
    description="Routes to billing or general specialist based on request_type",
    sub_agents=[billing_specialist, general_specialist],
)

# Classifier → custom router (workflow + custom combined)
root_agent = SequentialAgent(
    name="conditional_pipeline",
    sub_agents=[classifier, router],
)
