"""
parser.py - Analizador sintáctico descendente recursivo LL(1)
Parser de Alertas Hidrológicas del Río Paraná

Grámatica implementada:
    <boletin>          → BOLETIN_KW <encabezado> <lista_estaciones> FIN_KW
    <encabezado>       → FECHA HORA ID_BOLETIN
    <lista_estaciones> → <estacion> <resto_estaciones>
    <resto_estaciones> → PUNTO_Y_COMA <estacion> <resto_estaciones> | λ
    <estacion>         → ESTACION_KW ID_ESTACION <mediciones> <alerta>
    <mediciones>       → <nivel> <caudal> <tendencia>
    <numero>           → INTEGER | NUMBER
    <nivel>            → NIVEL_KW <numero> METROS_KW
    <caudal>           → CAUDAL_KW <numero> METROS3_KW
    <tendencia>        → TENDENCIA_KW <dir_tendencia>
    <dir_tendencia>    → SUBIENDO | BAJANDO | ESTABLE
    <alerta>           → ALERTA_KW <nivel_alerta>
    <nivel_alerta>     → VERDE | AMARILLO | NARANJA | ROJO
"""

from typing import List, Optional
from tokens import Token
from ast_nodes import (
    BoletinNode, EstacionNode,
    NivelNode, CaudalNode, TendenciaNode, AlertaNode
)

class ParseError(Exception):
    pass

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens  = tokens
        self.pos     = 0
        self.estaciones = set()
    
    #--------------------------
    #  Utilidades internas
    #--------------------------
    def _actual(self) -> Optional[Token]:
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def _consumir(self, tipo_esperado: str) -> Token:
        tok = self._actual()

        if tok is None:
            raise ParseError(
                f"Se esperaba '{tipo_esperado}' pero se llegó al final del archivo"
            )

        if tok.tipo != tipo_esperado:
            raise ParseError(
                f"Línea {tok.linea}, col {tok.col}: "
                f"se esperaba '{tipo_esperado}' pero se encontró "
                f"'{tok.tipo}' ({tok.valor!r})"
            )

        self.pos += 1
        return tok
    
    def _tipo_actual(self) -> Optional[str]:
        tok = self._actual()
        return tok.tipo if tok else None

    #------------------------------------------
    #  Producciones de la gramatica
    #------------------------------------------
    def parsear(self) -> BoletinNode:
        """Punto de entrada — produce el nodo raíz del AST."""
        nodo = self._boletin()
        
        if self._actual() is not None:
            tok = self._actual()
            raise ParseError(
                f"Línea {tok.linea}, col {tok.col}: "
                f"tokens inesperados después de FIN"
            )
        return nodo

    def _boletin(self) -> BoletinNode:
        """<boletin> → BOLETIN_KW <encabezado> <lista_estaciones> FIN_KW"""
        self._consumir('BOLETIN_KW')
        
        fecha, hora, id_boletin = self._encabezado()
        estaciones = self._lista_estaciones()
        
        self._consumir('FIN_KW')

        return BoletinNode(
            fecha=fecha,
            hora=hora,
            id_boletin=id_boletin,
            estaciones=estaciones
        )

    def _encabezado(self):
        """<encabezado> → FECHA HORA ID_BOLETIN"""
        fecha      = self._consumir('FECHA').valor
        hora       = self._consumir('HORA').valor
        id_boletin = self._consumir('ID_BOLETIN').valor
        
        return fecha, hora, id_boletin

    def _lista_estaciones(self) -> list:
        """<lista_estaciones> → <estacion> <resto_estaciones>"""
        estaciones = [self._estacion()]
        estaciones.extend(self._resto_estaciones())
        
        return estaciones

    def _resto_estaciones(self) -> list:
        """<resto_estaciones> → PUNTO_Y_COMA <estacion> <resto_estaciones> | λ"""
        if self._tipo_actual() == 'PUNTO_Y_COMA':
            self._consumir('PUNTO_Y_COMA')
            
            estacion = self._estacion()
            
            return [estacion] + self._resto_estaciones()
        
        return []   # produccion vacia (λ)
    
    def _estacion(self) -> EstacionNode:
        """<estacion> → ESTACION_KW ID_ESTACION <mediciones> <alerta>"""
        self._consumir('ESTACION_KW')
        
        tok = self._consumir('ID_ESTACION')
        id_est = tok.valor

        if id_est in self.estaciones:
            raise ParseError(
                f"Línea {tok.linea}, col {tok.col}: "
                f"la estación '{id_est}' ya fue declarada"
        )

        self.estaciones.add(id_est)
        nivel, caudal, tendencia = self._mediciones()
        alerta = self._alerta()
        
        return EstacionNode(
            id_estacion=id_est,
            nivel=nivel,
            caudal=caudal,
            tendencia=tendencia,
            alerta=alerta
        )

    def _mediciones(self):
        """<mediciones> → <nivel> <caudal> <tendencia>"""
        nivel    = self._nivel()
        caudal   = self._caudal()
        tendencia = self._tendencia()
        
        return nivel, caudal, tendencia

    def _numero(self) -> float:
        """
        <numero> → INTEGER | NUMBER
        """
        tipo = self._tipo_actual()

        if tipo in ('INTEGER', 'NUMBER'):
            return float(self._consumir(tipo).valor)

        tok = self._actual()

        raise ParseError(
            f"Línea {tok.linea}, col {tok.col}: "
            f"número inválido '{tok.valor}'"
        )

    def _nivel(self) -> NivelNode:
        """<nivel> → NIVEL_KW <numero> METROS_KW"""
        self._consumir('NIVEL_KW')
        valor = self._numero()

        self._consumir('METROS_KW')
        return NivelNode(valor=valor)

    def _caudal(self) -> CaudalNode:
        """<caudal> → CAUDAL_KW <numero> METROS3_KW"""
        self._consumir('CAUDAL_KW')
        valor = self._numero()
        
        self._consumir('METROS3_KW')
        return CaudalNode(valor=valor)

    def _tendencia(self) -> TendenciaNode:
        """<tendencia> → TENDENCIA_KW <dir_tendencia>"""
        self._consumir('TENDENCIA_KW')
        
        direccion = self._dir_tendencia()
        return TendenciaNode(direccion=direccion)

    def _dir_tendencia(self) -> str:
        """<dir_tendencia> → SUBIENDO | BAJANDO | ESTABLE"""
        tipo = self._tipo_actual()
        
        if tipo in ('SUBIENDO', 'BAJANDO', 'ESTABLE'):
            return self._consumir(tipo).valor
        
        tok = self._actual()
        
        raise ParseError(
            f"Línea {tok.linea}, col {tok.col}: "
            f"tendencia inválida '{tok.valor}'. "
            f"Se esperaba SUBIENDO, BAJANDO o ESTABLE"
        )

    def _alerta(self) -> AlertaNode:
        """<alerta> → ALERTA_KW <nivel_alerta>"""
        self._consumir('ALERTA_KW')
        
        nivel = self._nivel_alerta()
        
        return AlertaNode(nivel=nivel)

    def _nivel_alerta(self) -> str:
        """<nivel_alerta> → VERDE | AMARILLO | NARANJA | ROJO"""
        tipo = self._tipo_actual()
        
        if tipo in ('VERDE', 'AMARILLO', 'NARANJA', 'ROJO'):
            return self._consumir(tipo).valor
        
        tok = self._actual()
        
        raise ParseError(
            f"Línea {tok.linea}, col {tok.col}: "
            f"nivel de alerta inválido '{tok.valor}'. "
            f"Se esperaba VERDE, AMARILLO, NARANJA o ROJO"
        )
