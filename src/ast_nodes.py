"""
ast_nodes.py — Nodos del Árbol de Sintaxis Abstracta (AST)
Parser de Alertas Hidrológicas del Río Paraná
"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class NivelNode:
    valor: float
    unidad: str = 'm'

    def __repr__(self):
        return f'Nivel({self.valor} {self.unidad})'


@dataclass
class CaudalNode:
    valor: float
    unidad: str = 'm3s'

    def __repr__(self):
        return f'Caudal({self.valor} {self.unidad})'


@dataclass
class TendenciaNode:
    direccion: str   # SUBIENDO | BAJANDO | ESTABLE

    def __repr__(self):
        return f'Tendencia({self.direccion})'


@dataclass
class AlertaNode:
    nivel: str       # VERDE | AMARILLO | NARANJA | ROJO

    def __repr__(self):
        return f'Alerta({self.nivel})'


@dataclass
class EstacionNode:
    id_estacion: str
    nivel:       NivelNode
    caudal:      CaudalNode
    tendencia:   TendenciaNode
    alerta:      AlertaNode

    def __repr__(self):
        return (
            f'Estacion({self.id_estacion}, '
            f'{self.nivel}, {self.caudal}, '
            f'{self.tendencia}, {self.alerta})'
        )


@dataclass
class BoletinNode:
    fecha:       str
    hora:        str
    id_boletin:  str
    estaciones:  List[EstacionNode] = field(default_factory=list)

    def __repr__(self):
        ests = ', '.join(str(e) for e in self.estaciones)
        return (
            f'Boletin(id={self.id_boletin}, '
            f'fecha={self.fecha}, hora={self.hora}, '
            f'estaciones=[{ests}])'
        )

    def pretty(self, indent: int = 0) -> str:
        """Representación legible del AST completo."""
        pad  = '  ' * indent
        pad2 = '  ' * (indent + 1)
        pad3 = '  ' * (indent + 2)
        lines = [
            f'{pad}Boletin',
            f'{pad2}id       : {self.id_boletin}',
            f'{pad2}fecha    : {self.fecha}',
            f'{pad2}hora     : {self.hora}',
            f'{pad2}estaciones ({len(self.estaciones)}):',
        ]
        for est in self.estaciones:
            lines += [
                f'{pad3}Estacion : {est.id_estacion}',
                f'{pad3}  nivel    : {est.nivel.valor} {est.nivel.unidad}',
                f'{pad3}  caudal   : {est.caudal.valor} {est.caudal.unidad}',
                f'{pad3}  tendencia: {est.tendencia.direccion}',
                f'{pad3}  alerta   : {est.alerta.nivel}',
            ]
        return '\n'.join(lines)
