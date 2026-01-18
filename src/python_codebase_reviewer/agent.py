"""
Python Codebase Reviewer - Root Agent

This is the main orchestrator agent that coordinates specialized review agents
to perform comprehensive Python code reviews.
"""
from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
from .shared_libraries import constants
from . import prompt

# Import all sub-agents
from .sub_agents.security_reviewer import security_reviewer
from .sub_agents.architecture_reviewer import architecture_reviewer
from .sub_agents.code_quality_reviewer import code_quality_reviewer
from .sub_agents.performance_reviewer import performance_reviewer
from .sub_agents.python_expert import python_expert

# Wrap sub-agents as tools for the orchestrator to use
security_reviewer_tool = AgentTool(agent=security_reviewer)
architecture_reviewer_tool = AgentTool(agent=architecture_reviewer)
code_quality_reviewer_tool = AgentTool(agent=code_quality_reviewer)
performance_reviewer_tool = AgentTool(agent=performance_reviewer)
python_expert_tool = AgentTool(agent=python_expert)

# Create the root orchestrator agent
root_agent = Agent(
    model=constants.ORCHESTRATOR_MODEL,
    name=constants.AGENT_NAME,
    description=constants.DESCRIPTION,
    instruction=prompt.ROOT_PROMPT,
    tools=[
        security_reviewer_tool,
        architecture_reviewer_tool,
        code_quality_reviewer_tool,
        performance_reviewer_tool,
        python_expert_tool,
    ]
)

# Export the root agent for the ADK framework
__all__ = ['root_agent']
