"""
Security Reviewer Agent for Python code security analysis.
"""
from google.adk.agents import Agent
from ...shared_libraries import constants
from . import prompt

security_reviewer = Agent(
    model=constants.REVIEWER_MODEL,
    name="security_reviewer",
    description=(
        "Identifies security vulnerabilities in Python code including "
        "OWASP Top 10, injection flaws, authentication issues, cryptographic "
        "failures, and Python-specific security vulnerabilities."
    ),
    instruction=prompt.SECURITY_REVIEWER_PROMPT,
    tools=[
        # Tools can be added here when available:
        # - security_scanner_tool
        # - secrets_detector_tool
        # - dependency_vuln_tool
    ]
)
