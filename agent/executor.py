# agent/executor.py
# Ejecuta las herramientas cuando Claude las solicita.
# Claude decide QUÉ herramienta llamar; este módulo la EJECUTA.

import json
from google.cloud import bigquery

PROJECT = "staff-sizing-portfolio"
DATASET = "staff_sizing"

client = bigquery.Client(project=PROJECT)


def execute_bigquery_query(sql: str, description: str) -> str:
    """
    Ejecuta una query SQL en BigQuery y retorna los resultados como JSON string.
    Limitamos a 50 filas para no saturar el contexto de Claude.
    """
    print(f"\n  [BQ] {description}")
    print(f"  [SQL] {sql[:120]}{'...' if len(sql) > 120 else ''}")

    try:
        query_job = client.query(sql)
        results = query_job.result()

        rows = []
        for i, row in enumerate(results):
            if i >= 50:  # límite de seguridad
                break
            rows.append(dict(row))

        print(f"  [OK] {len(rows)} filas retornadas")
        return json.dumps(rows, default=str, ensure_ascii=False)

    except Exception as e:
        error_msg = f"Error ejecutando query: {str(e)}"
        print(f"  [ERROR] {error_msg}")
        return json.dumps({"error": error_msg})


def get_schema_info(table_name: str) -> str:
    """
    Retorna el esquema de una tabla como JSON.
    Útil para que Claude sepa qué columnas puede usar antes de generar SQL.
    """
    print(f"\n  [SCHEMA] Consultando esquema de {table_name}")

    try:
        table_ref = f"{PROJECT}.{DATASET}.{table_name}"
        table = client.get_table(table_ref)

        schema = [
            {"column": field.name, "type": field.field_type, "description": field.description or ""}
            for field in table.schema
        ]

        print(f"  [OK] {len(schema)} columnas")
        return json.dumps(schema, ensure_ascii=False)

    except Exception as e:
        return json.dumps({"error": f"Tabla no encontrada: {str(e)}"})


def run_tool(tool_name: str, tool_input: dict) -> str:
    """
    Router: recibe el nombre de la herramienta que Claude quiere usar
    y la ejecuta con los parámetros que Claude eligió.
    """
    if tool_name == "execute_bigquery_query":
        return execute_bigquery_query(**tool_input)
    elif tool_name == "get_schema_info":
        return get_schema_info(**tool_input)
    else:
        return json.dumps({"error": f"Herramienta desconocida: {tool_name}"})