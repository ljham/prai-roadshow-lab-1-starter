from typing import Literal
from google.adk.agents import Agent
from google.adk.apps.app import App
from pydantic import BaseModel, Field


MODEL = "gemini-2.5-pro"

# 1. Define el esquema
class JudgeFeedback(BaseModel):
    """Retroalimentación estructurada del agente Juez."""
    status: Literal["pass", "fail"] = Field(
        description="Si la investigación es suficiente ('pass') o necesita más trabajo ('fail')."
    )
    feedback: str = Field(
        description="Retroalimentación detallada sobre lo que falta. Si es 'pass', una breve confirmación."
    )

# 2. Define el agente
judge = Agent(
    name="judge",
    model=MODEL,
    description="Evalúa los hallazgos de investigación por completitud y precisión.",
    instruction="""
    Eres un editor estricto.
    Evalúa los 'research_findings' contra la solicitud original del usuario.
    Si los hallazgos carecen de información clave, retorna status='fail'.
    Si son completos, retorna status='pass'.
    """,
    output_schema=JudgeFeedback,
    # No permitir delegación porque solo debe emitir el esquema
    disallow_transfer_to_parent=True,
    disallow_transfer_to_peers=True,
)

root_agent = judge