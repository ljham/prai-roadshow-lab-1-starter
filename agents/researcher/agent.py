from google.adk.agents import Agent
from google.adk.tools.google_search_tool import google_search


MODEL = "gemini-2.5-pro"

# TODO: Define the Researcher Agent
# The researcher should be an Agent that uses the google_search tool
# and follows the instructions to gather information.

# Define the Researcher Agent
researcher = Agent(
    name="researcher",
    model=MODEL,
    description="Recopila información sobre un tema utilizando la Búsqueda de Google.",
    instruction="""
Eres un investigador experto. Tu objetivo es encontrar información completa y precisa sobre el tema del usuario.
Utiliza la herramienta `google_search` para encontrar información relevante.
Resume tus hallazgos con claridad.
Si recibes comentarios que indican que tu investigación es insuficiente, úsalos para mejorar tu próxima búsqueda.
    """,
    tools=[google_search],
)

root_agent = researcher