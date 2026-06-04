# main.py
# Punto de entrada del agente — interfaz conversacional en terminal.

import os
from dotenv import load_dotenv
from agent.agent import run_agent

load_dotenv()

def main():
    print("\n" + "="*60)
    print("  AGENTE DE DOTACIÓN LATAM — Staff Sizing 2027")
    print("  Conectado a BigQuery · staff-sizing-portfolio")
    print("="*60)
    print("Escribe tu pregunta en lenguaje natural.")
    print("Escribe 'salir' para terminar.\n")

    while True:
        try:
            question = input("HR > ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nHasta luego.")
            break

        if not question:
            continue
        if question.lower() in ("salir", "exit", "quit"):
            print("Hasta luego.")
            break

        respuesta = run_agent(question)
        print(f"\nAGENTE:\n{respuesta}\n")
        print("-" * 60)


if __name__ == "__main__":
    main()