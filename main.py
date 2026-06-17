"""
main.py — Punto de entrada del analizador
Parser de Alertas Hidrológicas del Río Paraná

Uso:
    python main.py <archivo.bol>
    python main.py --demo
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from lexer  import tokenizar, LexerError
from parser import Parser, ParseError
from visualizer import visualizar


def analizar(texto: str, nombre: str = "entrada", visualizar_ast: bool = False) -> bool:
    """
    Ejecuta el pipeline completo: lexer → parser → AST.
    Retorna True si el análisis fue exitoso, False si hubo error.
    """
    print(f"\n{'─'*55}")
    print(f"  Analizando: {nombre}")
    print(f"{'─'*55}")

    # ── Fase 1: Análisis léxico ──────────────────────────────
    try:
        tokens = tokenizar(texto)
    except LexerError as e:
        print(f"  ✗ ERROR LÉXICO: {e}")
        return False

    print(f"  ✓ Léxico OK — {len(tokens)} tokens reconocidos")

    # ── Fase 2: Análisis sintáctico + construcción del AST ───
    try:
        parser = Parser(tokens)
        ast    = parser.parsear()
    except ParseError as e:
        print(f"  ✗ ERROR SINTÁCTICO: {e}")
        return False

    print(f"  ✓ Sintáctico OK — AST construido")
    print()
    print(ast.pretty(indent=1))

    if visualizar_ast:
        salida = os.path.splitext(nombre)[0] + "_ast.html"
        visualizar(ast, salida)
    return True


DEMO_CASOS = {
    # ── Válidos ──────────────────────────────────────────────
    "valido_01_simple": """BOLETIN 2026-05-23 08:30 BOL-001
  ESTACION Corrientes
    NIVEL 6.45 m
    CAUDAL 18500 m3s
    TENDENCIA SUBIENDO
    ALERTA NARANJA
FIN""",

    "valido_02_multi": """BOLETIN 2026-05-23 08:30 BOL-002
  ESTACION Corrientes
    NIVEL 6.45 m
    CAUDAL 18500 m3s
    TENDENCIA SUBIENDO
    ALERTA NARANJA
  ;
  ESTACION Itati
    NIVEL 4.12 m
    CAUDAL 9800 m3s
    TENDENCIA ESTABLE
    ALERTA VERDE
FIN""",

    "valido_03_bajante": """BOLETIN 2026-03-10 14:00 BOL-003
  ESTACION Resistencia
    NIVEL 3.20 m
    CAUDAL 7500 m3s
    TENDENCIA BAJANDO
    ALERTA VERDE
FIN""",

    "valido_04_rojo": """BOLETIN 2026-06-01 06:00 BOL-004
  ESTACION Corrientes
    NIVEL 9.80 m
    CAUDAL 32000 m3s
    TENDENCIA SUBIENDO
    ALERTA ROJO
FIN""",

    "valido_05_tres_estaciones": """BOLETIN 2026-05-23 12:00 BOL-005
  ESTACION Corrientes
    NIVEL 6.45 m
    CAUDAL 18500 m3s
    TENDENCIA SUBIENDO
    ALERTA NARANJA
  ;
  ESTACION Itati
    NIVEL 4.12 m
    CAUDAL 9800 m3s
    TENDENCIA ESTABLE
    ALERTA VERDE
  ;
  ESTACION Empedrado
    NIVEL 5.70 m
    CAUDAL 14200 m3s
    TENDENCIA SUBIENDO
    ALERTA AMARILLO
FIN""",

    "valido_06_amarillo": """BOLETIN 2026-04-15 09:00 BOL-006
  ESTACION Goya
    NIVEL 5.10 m
    CAUDAL 12000 m3s
    TENDENCIA SUBIENDO
    ALERTA AMARILLO
FIN""",

    "valido_07_nivel_entero": """BOLETIN 2026-02-20 18:30 BOL-007
  ESTACION Itati
    NIVEL 4 m
    CAUDAL 9500 m3s
    TENDENCIA BAJANDO
    ALERTA VERDE
FIN""",

    "valido_08_estable_naranja": """BOLETIN 2026-05-10 07:45 BOL-008
  ESTACION Corrientes
    NIVEL 7.30 m
    CAUDAL 21000 m3s
    TENDENCIA ESTABLE
    ALERTA NARANJA
FIN""",

    # ── Inválidos ─────────────────────────────────────────────
    "invalido_01_sin_fin": """BOLETIN 2026-05-23 08:30 BOL-009
  ESTACION Corrientes
    NIVEL 6.45 m
    CAUDAL 18500 m3s
    TENDENCIA SUBIENDO
    ALERTA NARANJA""",

    "invalido_02_alerta_erronea": """BOLETIN 2026-05-23 08:30 BOL-010
  ESTACION Corrientes
    NIVEL 6.45 m
    CAUDAL 18500 m3s
    TENDENCIA SUBIENDO
    ALERTA AZUL
FIN""",

    "invalido_03_caracter_ilegal": """BOLETIN 2026-05-23 08:30 BOL-011
  ESTACION Corrientes
    NIVEL 6.45 m
    CAUDAL 18500 m3s
    TENDENCIA SUBIENDO
    ALERTA @NARANJA
FIN""",
}


def main():
    if len(sys.argv) == 2 and sys.argv[1] == '--demo':
        exitosos  = 0
        fallidos  = 0
        for nombre, texto in DEMO_CASOS.items():
            ok = analizar(texto, nombre)
            if ok:
                exitosos += 1
            else:
                fallidos += 1
        print(f"\n{'═'*55}")
        print(f"  Resumen: {exitosos} exitosos / {fallidos} con errores")
        print(f"{'═'*55}\n")
        return

    if len(sys.argv) >= 2 and sys.argv[1] != '--demo':
        ruta = sys.argv[1]
        viz  = '--visualizar' in sys.argv
        try:
            with open(ruta, encoding='utf-8') as f:
                texto = f.read()
            analizar(texto, ruta, visualizar_ast=viz)
        except FileNotFoundError:
            print(f"Error: no se encontró el archivo '{ruta}'")
        return

    print("Uso:")
    print("  python main.py <archivo.bol>   — analiza un archivo")
    print("  python main.py --demo          — ejecuta todos los casos de prueba")
    print("  python main.py <archivo.bol> --visualizar — analiza y genera HTML del AST")


if __name__ == '__main__':
    main()
