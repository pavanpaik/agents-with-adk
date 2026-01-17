"""
Python Domain Expert Agent for advanced Python expertise.
"""
from google.adk.agents import Agent
from ...shared_libraries import constants
from . import prompt

python_expert = Agent(
    model=constants.PYTHON_EXPERT_MODEL,
    name="python_expert",
    description=(
        "Master-level Python expert with deep knowledge of standard library, frameworks "
        "(Django, Flask, FastAPI), advanced features (metaclasses, descriptors, async/await), "
        "modern Python (3.8-3.12+), and testing best practices."
    ),
    instruction=prompt.PYTHON_EXPERT_PROMPT,
    tools=[
        # Tools can be added here when available:
        # - stdlib_advisor_tool
        # - framework_checker_tool
    ]
)
