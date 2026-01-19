"""
Python Codebase Reviewer - Root Agent

This is the main orchestrator agent that coordinates specialized review agents
to perform comprehensive Python code reviews.
"""
import logging
from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
from .shared_libraries import constants
from . import prompt

# Configure logging
logger = logging.getLogger(__name__)

# Import all sub-agents
from .sub_agents.security_reviewer import security_reviewer
from .sub_agents.architecture_reviewer import architecture_reviewer
from .sub_agents.code_quality_reviewer import code_quality_reviewer
from .sub_agents.performance_reviewer import performance_reviewer
from .sub_agents.python_expert import python_expert

logger.info("Initializing Python Codebase Reviewer agents")
logger.debug(f"Orchestrator model: {constants.ORCHESTRATOR_MODEL}")
logger.debug(f"Reviewer model: {constants.REVIEWER_MODEL}")

# Wrap sub-agents as tools for the orchestrator to use
security_reviewer_tool = AgentTool(agent=security_reviewer)
architecture_reviewer_tool = AgentTool(agent=architecture_reviewer)
code_quality_reviewer_tool = AgentTool(agent=code_quality_reviewer)
performance_reviewer_tool = AgentTool(agent=performance_reviewer)
python_expert_tool = AgentTool(agent=python_expert)

logger.debug("Sub-agents wrapped as tools successfully")

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

logger.info(f"Root orchestrator agent '{constants.AGENT_NAME}' initialized successfully")
logger.info(f"Available reviewers: security, architecture, code_quality, performance, python_expert")

# Add a run() method wrapper for convenience
# The google.adk Agent class uses query() but we want a simpler interface
def _run_wrapper(self, prompt: str) -> str:
    """
    Wrapper to provide a simple run() interface.

    Args:
        prompt: The review request/prompt

    Returns:
        str: The agent's response
    """
    response = self.query(prompt)
    # The query method returns a response object, extract the text
    if hasattr(response, 'text'):
        return response.text
    elif hasattr(response, 'content'):
        return response.content
    elif isinstance(response, str):
        return response
    else:
        return str(response)

# Monkey-patch the run method onto the root_agent instance
root_agent.run = lambda prompt: _run_wrapper(root_agent, prompt)

logger.debug("Added run() method wrapper to root_agent")

# Export the root agent for the ADK framework
__all__ = ['root_agent']
