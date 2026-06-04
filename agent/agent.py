# agent/agent.py
# Implementa el ciclo agentico: pregunta → plan → tool call → resultado → respuesta.
# El agente puede hacer múltiples llamadas a herramientas antes de responder.

import os
import anthropic
from agent.tools import TOOLS
from agent.executor import run_tool

# El system prompt define el rol y el contexto del agente.
# Es lo que convierte a Claude en un especialista en dotación LATAM.
SYSTEM_PROMPT = """Eres un agente analítico especializado en gestión de dotación para una aerolínea LATAM.

Tienes acceso a un dataset en BigQuery llamado staff_sizing con las siguientes tablas:
- mart_alerts_daily: alertas diarias de brecha de dotación por base y rol
- mart_gap_analysis: análisis mensual de gaps (real vs requerido) por base y rol  
- mart_sizing_weekly: dotación real vs requerida con estado (CRITICO/BAJO/OK) por semana
- mart_hiring_reco_2027: recomendación de contratación por base y rol con prioridad
- mart_attrition_history: historial de rotación por segmento, base y rol

Cuando el usuario te hace una pregunta:
1. Si necesitas datos, usa execute_bigquery_query para consultarlos directamente
2. Si no estás seguro de las columnas de una tabla, usa get_schema_info primero
3. Genera SQL preciso y eficiente — siempre incluye LIMIT para evitar queries enormes
4. Lee los resultados y redacta una respuesta ejecutiva en español
5. Incluye siempre: qué encontraste, qué significa para el negocio y qué acción se recomienda

Responde siempre en español. Sé directo y accionable — el usuario es de RR.HH., no sabe SQL."""


def run_agent(user_question: str) -> str:
    """
    Ejecuta el ciclo agentico completo para una pregunta del usuario.
    
    Ciclo:
    1. Envía la pregunta a Claude con las herramientas disponibles
    2. Si Claude quiere llamar una herramienta, la ejecutamos y devolvemos el resultado
    3. Repetimos hasta que Claude entregue una respuesta final (stop_reason = 'end_turn')
    """
    client_ai = anthropic.Anthropic()  # lee ANTHROPIC_API_KEY del entorno

    messages = [{"role": "user", "content": user_question}]

    print(f"\n{'='*60}")
    print(f"PREGUNTA: {user_question}")
    print(f"{'='*60}")

    iteration = 0
    max_iterations = 5  # límite de seguridad para evitar loops infinitos

    while iteration < max_iterations:
        iteration += 1
        print(f"\n[Iteración {iteration}] Consultando a Claude...")

        response = client_ai.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=2048,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages
        )

        print(f"[Stop reason] {response.stop_reason}")

        # Si Claude terminó de razonar → retornamos su respuesta de texto
        if response.stop_reason == "end_turn":
            final_text = ""
            for block in response.content:
                if hasattr(block, "text"):
                    final_text += block.text
            return final_text

        # Si Claude quiere llamar herramientas → las ejecutamos
        if response.stop_reason == "tool_use":
            # Agregamos la respuesta de Claude al historial
            messages.append({"role": "assistant", "content": response.content})

            # Procesamos cada herramienta que Claude quiere usar
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    print(f"\n[Tool call] {block.name}")
                    result = run_tool(block.name, block.input)

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result
                    })

            # Devolvemos los resultados a Claude para que continúe razonando
            messages.append({"role": "user", "content": tool_results})

        else:
            # Stop reason inesperado
            break

    return "El agente alcanzó el límite de iteraciones sin completar la tarea."