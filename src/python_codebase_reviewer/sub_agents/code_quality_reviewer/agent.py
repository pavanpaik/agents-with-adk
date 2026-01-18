"""
Code Quality Reviewer Agent for PEP standards and Pythonic code.
"""
from google.adk.agents import Agent
from ...shared_libraries import constants
from . import prompt

code_quality_reviewer = Agent(
    model=constants.ANALYZER_MODEL,
    name="code_quality_reviewer",
    description=(
        "Enforces PEP standards (PEP 8, PEP 20, PEP 257, PEP 484/585) and promotes "
        "Pythonic idioms. Identifies code smells, improves readability, and ensures "
        "code follows Python community best practices."
    ),
    instruction=prompt.CODE_QUALITY_REVIEWER_PROMPT,
    tools=[
        # Tools can be added here when available:
        # - ast_parser_tool
        # - linter_tool
        # - code_smell_detector
    ]
)
