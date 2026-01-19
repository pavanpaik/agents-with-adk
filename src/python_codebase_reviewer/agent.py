"""
Python Codebase Reviewer - Root Agent

This is the main orchestrator agent that coordinates specialized review agents
to perform comprehensive Python code reviews.
"""
import logging
import os
from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters
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

# Create GitHub MCP toolset for GitHub API operations
logger.info("Initializing GitHub MCP toolset")
github_mcp_toolset = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command='npx',
            args=[
                '-y',
                '@modelcontextprotocol/server-github'
            ],
            env={
                'GITHUB_PERSONAL_ACCESS_TOKEN': os.getenv('GITHUB_TOKEN', ''),
            }
        ),
    ),
)
logger.debug("GitHub MCP toolset initialized")

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
        github_mcp_toolset,  # Add GitHub MCP tools
    ]
)

logger.info(f"Root orchestrator agent '{constants.AGENT_NAME}' initialized successfully")
logger.info(f"Available reviewers: security, architecture, code_quality, performance, python_expert")
logger.info("GitHub MCP toolset enabled (51+ GitHub API tools available)")

# Create a wrapper class that adds run() method
class AgentWrapper:
    """Wrapper to provide a simple run() interface for the ADK Agent."""

    def __init__(self, agent):
        self._agent = agent

    def run(self, prompt: str) -> str:
        """
        Run the agent with a given prompt.

        Args:
            prompt: The review request/prompt

        Returns:
            str: The agent's response
        """
        response = self._agent.query(prompt)
        # The query method returns a response object, extract the text
        if hasattr(response, 'text'):
            return response.text
        elif hasattr(response, 'content'):
            return response.content
        elif isinstance(response, str):
            return response
        else:
            return str(response)

    def __getattr__(self, name):
        """Delegate all other attributes to the wrapped agent."""
        return getattr(self._agent, name)

# Wrap the agent to add run() method
root_agent = AgentWrapper(root_agent)

logger.debug("Wrapped root_agent with run() method")

# Export the root agent for the ADK framework
__all__ = ['root_agent']
