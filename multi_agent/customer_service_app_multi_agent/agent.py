"""
Customer Service App — Multi-Agent Capstone

Step 1: Intake agent extracts ticket details.
Step 2: Parallel billing + technical researchers (you implement next).
Step 3: Responder creates the final answer (you implement last).

Reference: https://google.github.io/adk-docs/agents/multi-agents
"""

from pathlib import Path

from dotenv import load_dotenv
from google.adk.agents import LlmAgent, ParallelAgent, SequentialAgent

load_dotenv(Path(__file__).parent / ".env")

MODEL = "gemini-3.6-flash"

# ---------------------------------------------------------------------------
# Step 1: Intake — extract ticket details → state['ticket_info']
# ---------------------------------------------------------------------------

intake_agent = LlmAgent(
    model=MODEL,
    name="intake",
    description="Extracts structured ticket details from the customer request",
    output_key="ticket_info",
    instruction="""You are a customer service intake specialist.

Extract and summarize the customer's request into a clear ticket:
- Issue type (billing, technical, or both)
- What happened
- What the customer wants resolved
- Any relevant details (dates, amounts, error messages)

Be concise and factual. Output only the ticket summary.""",
)

# ---------------------------------------------------------------------------
# Step 2: Parallel specialists — billing + technical (implement next)
# ---------------------------------------------------------------------------

billing_researcher = LlmAgent(
    model=MODEL,
    name="billing_researcher",
    output_key="billing_findings",
    instruction="""Research billing aspects of this ticket:

{ticket_info}

Provide billing policy guidance, refund eligibility, and recommended actions.
If the ticket has no billing aspects, respond: "No billing issues identified for this ticket.""",
)

technical_researcher = LlmAgent(
    model=MODEL,
    name="technical_researcher",
    output_key="technical_findings",
    instruction="""Research technical aspects of this ticket:

{ticket_info}

Provide troubleshooting steps, likely causes, and recommended fixes.
If the ticket has no technical aspects, respond: "No technical issues identified for this ticket.""",
)

parallel_specialists = ParallelAgent(
    name="specialists",
    sub_agents=[billing_researcher, technical_researcher],
)

# ---------------------------------------------------------------------------
# Step 3: Responder — final answer (implement last)
# ---------------------------------------------------------------------------

responder = LlmAgent(
    model=MODEL,
    name="responder",
    description="Creates the final customer-facing response",
    instruction="""Create a helpful, professional customer response using:

Ticket: {ticket_info}
Billing findings: {billing_findings}
Technical findings: {technical_findings}

Be empathetic, clear, and actionable.""",
)

# ---------------------------------------------------------------------------
# Root pipeline (uncomment when Steps 2–3 are complete)
# ---------------------------------------------------------------------------

root_agent = SequentialAgent(
    name="customer_service_app_multi_agent",
    sub_agents=[intake_agent, parallel_specialists, responder],
)
