import os
import json
from typing import AsyncGenerator
from google.adk.agents import BaseAgent, LoopAgent, SequentialAgent
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
from google.adk.events import Event, EventActions
from google.adk.agents.invocation_context import InvocationContext
from google.adk.agents.callback_context import CallbackContext

from authenticated_httpx import create_authenticated_client

# --- Callbacks ---
def create_save_output_callback(key: str):
    """Creates a callback to save the agent's final response to session state."""
    def callback(callback_context: CallbackContext, **kwargs) -> None:
        ctx = callback_context
        # Find the last event from this agent that has content
        for event in reversed(ctx.session.events):
            if event.author == ctx.agent_name and event.content and event.content.parts:
                text = event.content.parts[0].text
                if text:
                    # Try to parse as JSON if it looks like it, for judge_feedback
                    if key == "judge_feedback" and text.strip().startswith("{"):
                        try:
                            ctx.state[key] = json.loads(text)
                        except json.JSONDecodeError:
                            ctx.state[key] = text
                    else:
                        ctx.state[key] = text
                    print(f"[{ctx.agent_name}] Saved output to state['{key}']")
                    return
    return callback

# --- Remote Agents ---

# TODO: Define connections to remote agents
# Connect to Researcher, Judge, and Content Builder using RemoteA2aAgent.
# Remember to use the environment variables for URLs (or localhost defaults).

# Conectar al Investigador (Puerto local 8001)
researcher_url = os.environ.get("RESEARCHER_AGENT_CARD_URL", "http://localhost:8001/a2a/agent/.well-known/agent-card.json")
researcher = RemoteA2aAgent(
    name="researcher",
    agent_card=researcher_url,
    description="Recopila información usando Google Search.",
    # IMPORTANTE: Guardar la salida en el estado para que el Juez pueda verla
    after_agent_callback=create_save_output_callback("research_findings"),
    # IMPORTANTE: Usar cliente autenticado para la comunicación
    httpx_client=create_authenticated_client(researcher_url)
)

# Conectar al Juez (Puerto local 8002)
judge_url = os.environ.get("JUDGE_AGENT_CARD_URL", "http://localhost:8002/a2a/agent/.well-known/agent-card.json")
judge = RemoteA2aAgent(
    name="judge",
    agent_card=judge_url,
    description="Evalúa la investigación.",
    after_agent_callback=create_save_output_callback("judge_feedback"),
    httpx_client=create_authenticated_client(judge_url)
)

# Constructor de Contenido (Puerto local 8003)
content_builder_url = os.environ.get("CONTENT_BUILDER_AGENT_CARD_URL", "http://localhost:8003/a2a/agent/.well-known/agent-card.json")
content_builder = RemoteA2aAgent(
    name="content_builder",
    agent_card=content_builder_url,
    description="Construye el curso.",
    httpx_client=create_authenticated_client(content_builder_url)
)

# --- Escalation Checker ---

# TODO: Define EscalationChecker
# This agent should check the status of the judge's feedback.
# If status is "pass", it should escalate (break the loop).

class EscalationChecker(BaseAgent):
    """Verifica la retroalimentación del juez y escala (rompe el bucle) si fue aprobado."""

    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        # Recuperar la retroalimentación guardada por el Juez
        feedback = ctx.session.state.get("judge_feedback")
        print(f"[EscalationChecker] Retroalimentación: {feedback}")

        # Verificar el estado 'pass'
        is_pass = False
        if isinstance(feedback, dict) and feedback.get("status") == "pass":
            is_pass = True
        # Manejar fallback de cadena si el parseo JSON falló
        elif isinstance(feedback, str) and '"status": "pass"' in feedback:
            is_pass = True

        if is_pass:
            # 'escalate=True' le indica al LoopAgent padre que deje de iterar
            yield Event(author=self.name, actions=EventActions(escalate=True))
        else:
            # Continuar el bucle
            yield Event(author=self.name)

escalation_checker = EscalationChecker(name="escalation_checker")

# --- Loop Agents ---

# --- Orchestration ---

# TODO: Define the Research Loop
# Use LoopAgent to cycle through Researcher -> Judge -> EscalationChecker.

research_loop = LoopAgent(
    name="research_loop",
    description="Investiga y evalúa iterativamente hasta que se cumplan los estándares de calidad.",
    sub_agents=[researcher, judge, escalation_checker],
    max_iterations=3,
)


# TODO: Define the Root Agent (Pipeline)
# Use SequentialAgent to run the Research Loop followed by the Content Builder.

root_agent = SequentialAgent(
    name="course_creation_pipeline",
    description="Un pipeline que investiga un tema y luego construye un curso a partir de él.",
    sub_agents=[research_loop, content_builder],
)
