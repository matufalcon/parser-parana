"""
lexer.py - Analizador léxico (tokenizador)
Parser de Alertas Hidrológicas del Río Paraná
"""

import re
from typing import List
from tokens import TOKENS_TYPES, Token

MASTER_PATTERN = re.compile(
    '|'.join(f'(?P<{name}>{pattern})' for name, pattern in TOKEN_TYPES)
)

class LexerError(Exception):
    pass

def tokenizar(texto: str) -> List[Token]:
    """
    Convierte una cadena de texto en una lista de Token.
    Lanza LexerError ante cualquier carácter no reconocido.
    """
    tokens = []
    linea  = 1
    inicio_linea = 0

    for m in MASTER_PATTERN.finditer(texto):
        tipo  = m.lastgroup
        valor = m.group()
        col   = m.start() - inicio_linea + 1

        if tipo == 'NEWLINE':
            linea += 1
            inicio_linea = m.end()
            continue
        if tipo == 'SKIP':
            continue
        if tipo == 'ERROR':
            raise LexerError(
                f"Carácter inesperado '{valor}' en línea {linea}, columna {col}"
            )

        tokens.append(Token(tipo, valor, linea, col))

    return tokens