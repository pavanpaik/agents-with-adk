"""
Architecture Reviewer Agent for Python design patterns and SOLID principles.
"""
from google.adk.agents import Agent
from ...shared_libraries import constants
from . import prompt

architecture_reviewer = Agent(
    model=constants.REVIEWER_MODEL,
    name="architecture_reviewer",
    description=(
        "Evaluates software design patterns, architectural patterns, and SOLID "
        "principles in Python code. Identifies design anti-patterns, assesses "
        "modularity, coupling, cohesion, and testability."
    ),
    instruction=prompt.ARCHITECTURE_REVIEWER_PROMPT,
    tools=[
        # Tools can be added here when available:
        # - dependency_graph_tool
        # - complexity_analyzer_tool
        # - pattern_detector_tool
    ]
)
