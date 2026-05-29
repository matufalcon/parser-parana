"""
tokens.py - Definicion de tipos de token y dataclass Token
Parser de Alertas Hidrológicas del Río Paraná
"""

from dataclasses import dataclass

#--------------------------
# Tipos de token
#--------------------------

TOKENS_TYPES = [
    # Keywords estructurales
    ('BOLETIN_KW',   r'\bBOLETIN\b'),
    ('FIN_KW',       r'\bFIN\b'),
    ('ESTACION_KW',  r'\bESTACION\b'),

    # Keywords de campo
    ('NIVEL_KW',     r'\bNIVEL\b'),
    ('CAUDAL_KW',    r'\bCAUDAL\b'),
    ('TENDENCIA_KW', r'\bTENDENCIA\b'),
    ('ALERTA_KW',    r'\bALERTA\b'),

    # Keywords de valor 'Tendencia'
    ('SUBIENDO',     r'\bSUBIENDO\b'),
    ('BAJANDO',      r'\bBAJANDO\b'),
    ('ESTABLE',      r'\bESTABLE\b'),

    # Keywords de valor 'Alerta'
    ('VERDE',        r'\bVERDE\b'),
    ('AMARILLO',     r'\bAMARILLO\b'),
    ('NARANJA',      r'\bNARANJA\b'),
    ('ROJO',         r'\bROJO\b'),

    # Unidades (m3s antes que m para evitar match parcial)
    ('METROS3_KW',   r'\bm3s\b'),
    ('METROS_KW',    r'\bm\b'),

    # Literales
    ('FECHA',        r'\d{4}-\d{2}-\d{2}'),
    ('HORA',         r'\d{2}:\d{2}'),
    ('NUMBER',  r'\d+\.\d+'),      
    ('INTEGER', r'\d+'),     

    # Identificadores 
    ('ID_BOLETIN',   r'\bBOL-\d{3}\b'),
    ('ID_ESTACION',  r'\b[A-Za-z][A-Za-z0-9_-]*\b'),

    # Símbolos
    ('PUNTO_Y_COMA', r';'),

    # Control
    ('NEWLINE',      r'\n'),
    ('SKIP',         r'[ \t\r]+'),
    ('ERROR',        r'.'),
]

@dataclass
class Token:
    tipo:  str
    valor: str
    linea: int
    col:   int

    def __repr__(self):
        return (
            f"Token({self.tipo}, {self.valor!r}, "
            f"linea={self.linea}, col={self.col})"            
        )
