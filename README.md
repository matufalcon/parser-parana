# Parser de Alertas Hidrológicas del Río Paraná

Analizador léxico-sintáctico para un lenguaje formal de boletines hidrológicos del río Paraná.  
Trabajo Integrador — Teoría de la Computación  
Licenciatura en Sistemas de Información — UNNE

---

## Descripción

Este proyecto implementa un compilador front-end completo para un lenguaje formal que permite expresar boletines estructurados de crecida/bajante del río Paraná. El sistema incluye:

- **Analizador léxico** (`lexer.py`): tokeniza el texto de entrada usando expresiones regulares
- **Analizador sintáctico** (`parser.py`): parser descendente recursivo LL(1)
- **AST** (`ast_nodes.py`): árbol de sintaxis abstracta con representación legible
- **Visualizador** (`visualizer.py`): genera un árbol HTML interactivo del AST

---

## Requisitos

- Python 3.8 o superior
- Sin dependencias externas (solo biblioteca estándar)

Verificar versión instalada:
```bash
python --version
```

---

## Estructura del proyecto

```
parser-parana/
├── main.py                  # Punto de entrada
├── README.md
├── .gitignore
├── LICENSE
├── assets/
│   └── styles.css           # Estilos del visualizador HTML
├── src/
│   ├── tokens.py            # Tipos de token y dataclass Token
│   ├── lexer.py             # Analizador léxico
│   ├── parser.py            # Analizador sintáctico LL(1)
│   ├── ast_nodes.py         # Nodos del AST
│   └── visualizer.py        # Generador de árbol HTML
└── examples/
    ├── valido_01.bol        # Boletín simple — 1 estación
    ├── valido_02.bol        # Boletín múltiple — 4 estaciones con ';' separador
    ├── valido_03.bol        # Tres tendencias distintas (BAJANDO/ESTABLE/SUBIENDO)
    ├── valido_04.bol        # 4 estaciones, alertas AMARILLO→VERDE→NARANJA→ROJO
    ├── valido_05.bol        # 5 estaciones, mix completo de tendencias y alertas
    ├── valido_06.bol        # 6 estaciones, alerta ROJO en Parana, mayoría estables
    ├── valido_07.bol        # Nivel entero — sin decimales (INTEGER)
    ├── valido_08.bol        # 8 estaciones, boletín más completo
    ├── invalido_01.bol      # Error: unidad de medida incorrecta ('@metros')
    ├── invalido_02.bol      # Error: tendencia inválida ('CRECIENDO')
    ├── invalido_03.bol      # Error: identificador mal formado ('BOL-12')
    └── invalido_04.bol      # Error: campo TENDENCIA ausente
```

---

## Ejecución

### Modo demo — ejecuta los 12 casos de prueba (8 válidos + 4 inválidos)

```bash
python main.py --demo
```

### Analizar un archivo específico

```bash
python main.py examples/valido_01.bol
python main.py examples/invalido_02.bol
```

### Analizar y generar visualización HTML del AST

```bash
python main.py examples/valido_01.bol --visualizar
```

Genera un archivo `valido_01_ast.html` con el árbol interactivo. Abrirlo en cualquier navegador.

---

## Sintaxis del lenguaje

Un boletín válido tiene la siguiente estructura:

```
BOLETIN <fecha> <hora> <id>
  ESTACION <nombre>
    NIVEL <numero> m
    CAUDAL <numero> m3s
    TENDENCIA SUBIENDO | BAJANDO | ESTABLE
    ALERTA VERDE | AMARILLO | NARANJA | ROJO
  [; ESTACION ...]
FIN
```

> Las estaciones múltiples se separan con `;`

### Ejemplo válido — boletín simple

```
BOLETIN 2026-05-23 08:30 BOL-001
  ESTACION Corrientes
    NIVEL 6.45 m
    CAUDAL 18500 m3s
    TENDENCIA SUBIENDO
    ALERTA NARANJA
FIN
```

### Ejemplo válido — boletín multi-estación

```
BOLETIN 2026-05-23 08:30 BOL-002
  ESTACION Posadas
    NIVEL 6.45 m
    CAUDAL 18500 m3s
    TENDENCIA SUBIENDO
    ALERTA NARANJA
;
  ESTACION Corrientes
    NIVEL 4.12 m
    CAUDAL 9800 m3s
    TENDENCIA ESTABLE
    ALERTA VERDE
FIN
```

### Formatos de tokens

| Campo | Formato | Ejemplo |
|---|---|---|
| Fecha | `AAAA-MM-DD` | `2026-05-23` |
| Hora | `HH:MM` | `08:30` |
| ID boletín | `BOL-NNN` | `BOL-001` |
| Nombre estación | letras, dígitos, guion bajo | `BellaVista` |
| Número decimal | dígitos con punto | `6.45` |
| Número entero | dígitos sin punto | `18500` |
| Unidad nivel | literal `m` | `m` |
| Unidad caudal | literal `m3s` | `m3s` |

---

## Gramática (BNF)

```
<boletin>          → BOLETIN_KW <encabezado> <lista_estaciones> FIN_KW
<encabezado>       → FECHA HORA ID_BOLETIN
<lista_estaciones> → <estacion> <resto_estaciones>
<resto_estaciones> → PUNTO_Y_COMA <estacion> <resto_estaciones> | ε
<estacion>         → ESTACION_KW ID_ESTACION <mediciones> <alerta>
<mediciones>       → <nivel> <caudal> <tendencia>
<nivel>            → NIVEL_KW <numero> METROS_KW
<caudal>           → CAUDAL_KW <numero> METROS3_KW
<numero>           → NUMBER | INTEGER
<tendencia>        → TENDENCIA_KW <dir_tendencia>
<dir_tendencia>    → SUBIENDO | BAJANDO | ESTABLE
<alerta>           → ALERTA_KW <nivel_alerta>
<nivel_alerta>     → VERDE | AMARILLO | NARANJA | ROJO
```

La gramática es **libre de contexto, no ambigua y LL(1)**. No existen conflictos FIRST/FIRST ni FIRST/FOLLOW.

---

## Ejemplos de errores detectados

**Unidad de medida incorrecta:**
```
NIVEL 5.40 @metros
→ ERROR LÉXICO: Carácter inesperado '@' en línea 3, columna 16
```

**Tendencia inválida:**
```
TENDENCIA CRECIENDO
→ ERROR SINTÁCTICO: tendencia inválida 'CRECIENDO'.
  Se esperaba SUBIENDO, BAJANDO o ESTABLE
```

**Identificador mal formado:**
```
BOLETIN 2026-05-23 08:30 BOL-12
→ ERROR LÉXICO: se esperaba 'ID_BOLETIN' pero se encontró 'ID_ESTACION' ('BOL-12')
```

**Campo TENDENCIA ausente:**
```
→ ERROR SINTÁCTICO: se esperaba 'TENDENCIA_KW' pero se encontró 'ALERTA_KW'
```

---

## Autores

Trabajo Integrador — Teoría de la Computación  
Licenciatura en Sistemas de Información — UNNE  
2026
