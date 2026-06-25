"""
visualizer.py - Visualizacion del AST como HTML interactivo
Parser de Alertas Hidrológicas del Río Paraná
"""

from ast_nodes import BoletinNode

PALETA_ESTACIONES = [
    {"bg": "#0d1a1a", "color": "#80deea", "border": "#00838f"},  # cian 
    {"bg": "#1a0d2e", "color": "#ce93d8", "border": "#7b5cff"},  # violeta
    {"bg": "#1a1000", "color": "#ffcc80", "border": "#e65100"},  # ambar
    {"bg": "#0d1a2e", "color": "#90caf9", "border": "#1565c0"},  # azul
]


def _nodo(label: str, clase: str, hijos: list = [], estilo: str = "") -> dict:
    return {"label": label, "clase": clase, "hijos": hijos, "estilo": estilo}

def _ast_a_dict(ast: BoletinNode) -> dict:
    estaciones = []

    for i, estacion in enumerate(ast.estaciones):
        p = PALETA_ESTACIONES[i % len(PALETA_ESTACIONES)]
        estilo = f'background:{p["bg"]};color:{p["color"]};border-color:{p["border"]}'

        estaciones.append(_nodo(
            f"ESTACION\\n{estacion.id_estacion}",
            "estacion",
            hijos=[
                _nodo(f"NIVEL\\n{estacion.nivel.valor} {estacion.nivel.unidad}", "medicion"),
                _nodo(f"CAUDAL\\n{estacion.caudal.valor} {estacion.caudal.unidad}", "medicion"),
                _nodo(f"TENDENCIA\\n{estacion.tendencia.direccion}", "tendencia"),
                _nodo(f"ALERTA\\n{estacion.alerta.nivel}", f"alerta-{estacion.alerta.nivel.lower()}"),
            ],
            estilo=estilo,
        ))

    return _nodo(
        f"BoletinNode\\n{ast.id_boletin}",
        "boletin",
        hijos=[
            _nodo(f"FECHA\\n{ast.fecha}", "medicion"),
            _nodo(f"HORA\\n{ast.hora}", "medicion"),
            _nodo("Lista de \\nestaciones", "medicion", hijos=estaciones),
        ]
    )


def _nodo_a_html(nodo: dict) -> str:
    hijos_html = ""

    if nodo["hijos"]:
        items = "".join(f"<li>{_nodo_a_html(h)}</li>" for h in nodo["hijos"])
        hijos_html = f"<ul>{items}</ul>"

    label = nodo["label"].replace("\\n", "<br>")
    estilo = f' style="{nodo["estilo"]}"' if nodo.get("estilo") else ""

    if nodo["clase"] == "estacion" and nodo["hijos"]:
        return f'<details><summary class="node {nodo["clase"]}"{estilo}>{label}</summary>{hijos_html}</details>'

    return f'<div class="node {nodo["clase"]}"{estilo}> {label} </div> {hijos_html}'


def generar_html(ast: BoletinNode, titulo: str = "AST — Boletín Hidrológico") -> str:
    arbol_html = _nodo_a_html(_ast_a_dict(ast))

    return f"""
    <!DOCTYPE html>
        <html lang="es">

        <head>
            <meta charset="UTF-8">
            <link rel="stylesheet" href="../assets/styles.css">
            <title>{titulo}</title>
        </head>
        <body>
            <h1>{titulo}</h1>
            <div class="tree"><ul><li>{arbol_html}</li></ul></div>
        </body>
    </html>"""


def visualizar(ast: BoletinNode, ruta_salida: str = "ast_output.html") -> None:
    html = generar_html(ast, f"AST — {ast.id_boletin} ({ast.fecha})")
    with open(ruta_salida, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"\n  ✓ AST visualizado → {ruta_salida}\n")