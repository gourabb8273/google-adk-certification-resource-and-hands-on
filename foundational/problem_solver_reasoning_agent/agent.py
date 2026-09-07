"""
Problem-solving agent with built-in planning capabilities.

Demonstrates ADK's BuiltInPlanner with ThinkingConfig.
"""

from pathlib import Path

from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.planners import BuiltInPlanner
from google.genai import types

load_dotenv(Path(__file__).parent / ".env")


# Planning-enabled agent for complex problem solving
root_agent = LlmAgent(
    model="gemini-3.6-flash",
    name="strategic_problem_solver",
    description="Solves complex problems using multi-step reasoning and planning",
    instruction="""You are a Strategic Problem Solver.

Your approach to complex problems:
1. **Understand** - Break down the problem into components
2. **Analyze** - Consider multiple approaches and trade-offs
3. **Plan** - Develop a step-by-step solution strategy
4. **Execute** - Provide clear, actionable recommendations

For complex problems:
- Think through implications and edge cases
- Consider short-term vs long-term consequences
- Identify potential risks and mitigation strategies
- Provide reasoning for your recommendations

Be thorough, analytical, and systematic in your approach.""",
    planner=BuiltInPlanner(
        thinking_config=types.ThinkingConfig(
            include_thoughts=True,  # Show reasoning process
            thinking_budget=2048,  # Large budget for complex thinking
        )
    ),
)

# Questions:
# How should I prepare for a career transition from software engineering to product
# management over the next 12 months?
#
# What is the capital of France?
#
# Which planner should you use?
# Use BuiltInPlanner when working with Gemini models (2.5 Flash, 2.5 Pro, 2.0 Flash)
# More natural reasoning process
# Configurable thinking depth with
# Optional visibility into reasoning with
# Use PlanReActPlanner when:
# Working with non-Gemini models that lack built-in thinking
# You need strict output structure (PLANNING/ACTION/REASONING/FINAL_ANSWER)
# Building tool-heavy agents where explicit action phases help
# For this course, we focus on BuiltInPlanner since we're using Gemini models.
# PlanReActPlanner is covered in advanced multi-agent courses.
