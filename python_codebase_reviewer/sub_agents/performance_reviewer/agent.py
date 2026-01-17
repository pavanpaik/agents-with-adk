"""
Performance Reviewer Agent for Python optimization.
"""
from google.adk.agents import Agent
from ...shared_libraries import constants
from . import prompt

performance_reviewer = Agent(
    model=constants.ANALYZER_MODEL,
    name="performance_reviewer",
    description=(
        "Identifies performance bottlenecks and optimization opportunities in Python code. "
        "Analyzes algorithm complexity, memory efficiency, database query patterns, "
        "caching opportunities, and suggests concurrency improvements."
    ),
    instruction=prompt.PERFORMANCE_REVIEWER_PROMPT,
    tools=[
        # Tools can be added here when available:
        # - complexity_calculator_tool
        # - query_analyzer_tool
        # - resource_profiler_tool
    ]
)
