# agent/tools.py
# Define las herramientas (tools) que el agente puede invocar.
# Claude lee estas definiciones y decide cuál usar según la pregunta del usuario.

TOOLS = [
    {
        "name": "execute_bigquery_query",
        "description": (
            "Ejecuta una query SQL sobre el dataset staff_sizing en BigQuery "
            "y retorna los resultados como lista de diccionarios. "
            "Úsala cuando necesites datos reales de headcount, brechas, alertas o rotación."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "sql": {
                    "type": "string",
                    "description": (
                        "Query SQL válida para BigQuery Standard SQL. "
                        "Las tablas disponibles son: "
                        "mart_alerts_daily, mart_gap_analysis, mart_sizing_weekly, "
                        "mart_hiring_reco_2027, mart_attrition_history. "
                        "Proyecto: staff-sizing-portfolio, Dataset: staff_sizing."
                    )
                },
                "description": {
                    "type": "string",
                    "description": "Descripción breve de qué está consultando esta query (para logging)."
                }
            },
            "required": ["sql", "description"]
        }
    },
    {
        "name": "get_schema_info",
        "description": (
            "Retorna el esquema (columnas y tipos) de una tabla específica del dataset staff_sizing. "
            "Úsala primero si no estás seguro de qué columnas tiene una tabla antes de consultarla."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "table_name": {
                    "type": "string",
                    "description": "Nombre de la tabla sin proyecto ni dataset. Ej: mart_alerts_daily"
                }
            },
            "required": ["table_name"]
        }
    }
]