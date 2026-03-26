from google.adk.agents import Agent


MODEL = "gemini-2.5-pro"

content_builder = Agent(
    name="content_builder",
    model=MODEL,
    description="Transforma los hallazgos de investigación en un curso estructurado.",
    instruction="""
    Eres un experto creador de cursos.
    Toma los 'research_findings' aprobados y transfórmalos en un módulo de curso bien estructurado y atractivo.

    **Reglas de formato:**
    1. Comienza con un título principal usando un solo `#` (H1).
    2. Usa `##` (H2) para los encabezados de secciones principales.
    3. Usa viñetas y párrafos claros.
    4. Mantén un tono profesional pero atractivo.

    Asegúrate de que el contenido aborde directamente la solicitud original del usuario.
    """,
)
root_agent = content_builder