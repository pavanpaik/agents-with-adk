from google.adk.agents import Agent
from . import prompt
from ...shared_libraries import constants
from ...tools.search import google_search_grounding

researcher = Agent(
    model=constants.BASE_MODEL,
    name="researcher",
    description="Searches the web for information on a topic.",
    instruction=prompt.RESEARCHER_PROMPT,
    tools=[google_search_grounding]
)
