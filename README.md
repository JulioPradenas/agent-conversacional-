# 🤖 Agente Conversacional — Staff Sizing LATAM
### Portfolio Data Analyst · Claude API · BigQuery · Tool Use · Python

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Anthropic](https://img.shields.io/badge/Claude-API-purple)
![BigQuery](https://img.shields.io/badge/BigQuery-GCP-orange)
![Status](https://img.shields.io/badge/Status-Production--Ready-green)

---

## ¿Qué es este proyecto?

Un agente conversacional que permite a equipos de RR.HH. consultar el sistema
de dotación LATAM en **lenguaje natural**, sin necesidad de saber SQL ni abrir
un dashboard.

En lugar de buscar manualmente en Looker Studio, el usuario escribe:

> _"¿Qué bases tienen riesgo crítico de dotación este mes?"_

Y el agente:
1. Genera la query SQL correcta
2. La ejecuta sobre BigQuery (`staff_sizing` dataset)
3. Lee los resultados
4. Redacta un resumen ejecutivo con acciones recomendadas

---

## Arquitectura del agente
Usuario (lenguaje natural)
↓
Claude API (claude-sonnet-4-5)

System prompt especializado
Tool definitions
↓
┌────────────────────────────┐
│   Ciclo agentico (loop)    │
│                            │
│  Claude decide tool_use    │
│         ↓                  │
│  executor.py ejecuta tool  │
│         ↓                  │
│  resultado → Claude        │
│         ↓                  │
│  stop_reason = end_turn    │
└────────────────────────────┘
↓
Respuesta ejecutiva en español


---

## Herramientas del agente (Tool Use)

| Herramienta | Descripción |
|---|---|
| `execute_bigquery_query` | Genera y ejecuta SQL sobre los marts de staff_sizing |
| `get_schema_info` | Consulta el esquema de una tabla antes de generar la query |

El agente puede encadenar múltiples tool calls en una sola pregunta — por ejemplo,
primero inspecciona el esquema y luego ejecuta la query con las columnas correctas.

---

## Dataset — Staff Sizing (BigQuery)

Este agente consume los marts del proyecto
[Staff Sizing & Headcount Planning 2027](https://github.com/JulioPradenas/staff-sizing-portfolio):

| Tabla | Contenido |
|---|---|
| `mart_alerts_daily` | Alertas de brecha por base y rol |
| `mart_gap_analysis` | Gap mensual real vs requerido |
| `mart_sizing_weekly` | Dotación semanal con estado CRITICO/BAJO/OK |
| `mart_hiring_reco_2027` | Recomendación de contratación por prioridad |
| `mart_attrition_history` | Historial de rotación por segmento |

---

## Estructura del proyecto
agent-conversacional/
├── agent/
│   ├── agent.py       # Ciclo agentico principal (loop tool use)
│   ├── tools.py       # Definición de herramientas para Claude
│   └── executor.py    # Ejecución real de tools (BigQuery client)
├── main.py            # Interfaz CLI conversacional
├── requirements.txt
└── .env               # ANTHROPIC_API_KEY (no incluido en repo)

---

## Cómo ejecutarlo

```bash
# 1. Clonar y activar entorno
git clone https://github.com/JulioPradenas/agent-conversacional-.git
cd agent-conversacional-
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2. Configurar credenciales
echo "ANTHROPIC_API_KEY=tu_key_aqui" > .env
gcloud auth application-default login \
  --scopes=https://www.googleapis.com/auth/cloud-platform

# 3. Ejecutar
python main.py
```

### Ejemplo de sesión
HR > ¿Qué bases tienen riesgo crítico de dotación este mes?
[Iteración 1] Consultando a Claude...
[Stop reason] tool_use
[Tool call] execute_bigquery_query
[BQ] Bases con estado CRÍTICO en junio 2027
[SQL] SELECT base_code, gap_vs_minimum, pct_weeks_critical ...
[OK] 3 filas retornadas
[Iteración 2] Consultando a Claude...
[Stop reason] end_turn
AGENTE:
Encontré 3 bases en estado CRÍTICO este mes:

Santiago (SCL): déficit de 38 FTE — 72% de semanas críticas
Roles urgentes: Piloto Comandante, Copiloto, Técnico Mantenimiento
Buenos Aires (EZE): déficit de 16 FTE — 61% de semanas críticas
Roles urgentes: Tripulante de Cabina, Copiloto
Caracas (CCS): déficit de 7 FTE — 55% de semanas críticas
Roles urgentes: Piloto Comandante

Recomendación: iniciar convocatoria inmediata para Pilotos Comandante
y Copilotos en SCL y EZE antes del 15 de junio.

---

## Habilidades demostradas

| Habilidad | Detalle |
|---|---|
| **LLM Orchestration** | Ciclo agentico con tool use real (Claude API) |
| **Function Calling** | Definición de tools con JSON Schema |
| **BigQuery** | Queries generadas dinámicamente por el LLM |
| **Python** | Arquitectura modular (agent / tools / executor) |
| **Prompt Engineering** | System prompt especializado por dominio |
| **GCP** | Autenticación ADC, BigQuery client |

---

## Conexión con el portfolio

Este proyecto consume los datos construidos en
**[Staff Sizing & Headcount Planning 2027](https://github.com/JulioPradenas/staff-sizing-portfolio)**,
demostrando cómo una capa de IA conversacional puede hacer accesibles los datos
de un sistema analítico complejo a usuarios no técnicos.