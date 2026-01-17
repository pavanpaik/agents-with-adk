from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools.google_search_tool import google_search
from ..shared_libraries import constants

_researcher = Agent(
    model=constants.BASE_MODEL,
    name="researcher",
    description="Searches the web for information on a topic.",
    instruction="""
    Answer the user's question directly using the Google search tool; provide a brief but concise response.
    Instead of a detailed answer, provide the immediate action item for the developer in a single sentence.
    Don't ask the user to check or look for information on their own; that's your role; do your best to be informative.
    """,
    tools=[google_search]
)

google_search_grounding = AgentTool(agent=_researcher)
