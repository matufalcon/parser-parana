# Parser de Alertas Hidrológicas del Río Paraná

Analizador léxico-sintáctico para un lenguaje formal de boletines hidrológicos del río Paraná.  
Trabajo Integrador — Teoría de la Computación  
Licenciatura en Sistemas de Información — UNNE

---

## Descripción

Este proyecto implementa un compilador front-end completo para un lenguaje formal que permite expresar boletines estructurados de crecida/bajante del río Paraná. El sistema incluye:

- **Analizador léxico** (`lexer.py`): tokeniza el texto de entrada
- **Analizador sintáctico** (`parser.py`): parser descendente recursivo LL(1)