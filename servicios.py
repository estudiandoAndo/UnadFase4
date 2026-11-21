# -*- coding: utf-8 -*-
"""Clase abstracta Servicio y tres servicios especializados (polimorfismo)."""
import itertools  # Para los contadores de id
from abc import ABC, abstractmethod  # Para definir la clase abstracta

from entidades import EntidadBase  # Entidad general
from excepciones import (  # Errores propios usados en este módulo
    CalculoInconsistenteError,
    ParametroFaltanteError,
    ServicioInvalidoError,
)


class Servicio(EntidadBase, ABC):  # Clase abstracta Servicio
    """Servicio genérico de Software FJ. Las subclases definen costo, descripción y validación."""

    _contador = itertools.count(1)  # Contador propio: ids 1, 2, 3... por tipo de entidad
    IVA_POR_DEFECTO = 0.19  # Impuesto aplicado cuando no se indica otro

    def __init__(self, nombre=None, tarifa_hora=None):  # Constructor común
        super().__init__()  # Inicializa id y fecha
        if nombre is None or str(nombre).strip() == "":  # Nombre obligatorio
            raise ParametroFaltanteError("Falta el nombre del servicio")  # Error si falta
        if isinstance(tarifa_hora, bool) or not isinstance(tarifa_hora, (int, float)) or tarifa_hora <= 0:  # Tarifa válida
            raise ServicioInvalidoError(f"Tarifa por hora inválida: {tarifa_hora!r}")  # Error si no es positiva
        self._nombre = str(nombre).strip()  # Nombre protegido
        self._tarifa_hora = float(tarifa_hora)  # Tarifa protegida
        self._disponible = True  # Todo servicio nace disponible

    @property  # Getter del nombre
    def nombre(self):
        return self._nombre  # Devuelve el nombre

    @property  # Getter de la tarifa
    def tarifa_hora(self):
        return self._tarifa_hora  # Devuelve la tarifa

    @property  # Getter de disponibilidad
    def disponible(self):
        return self._disponible  # Devuelve si está disponible

    @disponible.setter  # Setter de disponibilidad
    def disponible(self, valor):
        if not isinstance(valor, bool):  # Solo acepta True o False
            raise ServicioInvalidoError("La disponibilidad debe ser True o False")  # Error si no es booleano
        self._disponible = valor  # Guarda el nuevo estado

    @abstractmethod  # Cada servicio calcula su costo base distinto
    def calcular_costo_base(self, horas):
        """Costo sin impuestos ni descuentos."""

    @abstractmethod  # Cada servicio valida sus propios parámetros
    def validar_parametros(self, horas, **extra):
        """Lanza ServicioInvalidoError si los parámetros no son válidos."""

    @abstractmethod  # Cada servicio se describe a su manera
    def describir(self):
        """Descripción del servicio."""

    def calcular_costo(self, horas, impuesto=None, descuento=None, **extra):  # Sobrecarga simulada con opcionales
        """Variantes: calcular_costo(h) | calcular_costo(h, impuesto) | calcular_costo(h, impuesto, descuento)."""
        self.validar_parametros(horas, **extra)  # Primero valida (método polimórfico)
        tasa = self.IVA_POR_DEFECTO if impuesto is None else impuesto  # Usa IVA por defecto si no se indica
        dto = 0.0 if descuento is None else descuento  # Sin descuento por defecto
        if not isinstance(tasa, (int, float)) or not 0 <= tasa <= 1:  # El impuesto debe estar entre 0 y 1
            raise CalculoInconsistenteError(f"Impuesto fuera de rango: {tasa!r}")  # Error de cálculo
        if not isinstance(dto, (int, float)) or not 0 <= dto <= 1:  # El descuento debe estar entre 0 y 1
            raise CalculoInconsistenteError(f"Descuento fuera de rango: {dto!r}")  # Error de cálculo
        base = self.calcular_costo_base(horas)  # Costo base según el tipo de servicio
        total = base * (1 - dto) * (1 + tasa)  # Aplica descuento y luego impuesto
        if total <= 0:  # Un costo no positivo es inconsistente
            raise CalculoInconsistenteError(f"Costo calculado inconsistente: {total}")  # Error de cálculo
        return round(total, 2)  # Devuelve el total redondeado


class ReservaSala(Servicio):  # Servicio 1: reserva de salas
    """Reserva de salas de reuniones por horas."""

    def __init__(self, nombre=None, tarifa_hora=None, capacidad=None):  # Constructor con capacidad
        super().__init__(nombre, tarifa_hora)  # Valida nombre y tarifa en la clase padre
        if isinstance(capacidad, bool) or not isinstance(capacidad, int) or capacidad <= 0:  # Capacidad entera positiva
            raise ServicioInvalidoError(f"Capacidad inválida: {capacidad!r}")  # Error si no cumple
        self._capacidad = capacidad  # Guarda la capacidad

    def calcular_costo_base(self, horas):  # Sobrescribe el método abstracto
        return self._tarifa_hora * horas  # Tarifa por número de horas

    def validar_parametros(self, horas, **extra):  # Sobrescribe la validación
        if isinstance(horas, bool) or not isinstance(horas, (int, float)) or not 1 <= horas <= 8:  # Entre 1 y 8 horas
            raise ServicioInvalidoError(f"Horas de sala inválidas (1-8): {horas!r}")  # Error de horas
        asistentes = extra.get("asistentes")  # Parámetro opcional: número de asistentes
        if asistentes is not None and (not isinstance(asistentes, int) or not 1 <= asistentes <= self._capacidad):  # Debe caber
            raise ServicioInvalidoError(f"Asistentes ({asistentes}) exceden la capacidad ({self._capacidad})")  # Error

    def describir(self):  # Sobrescribe la descripción
        return f"Sala '{self.nombre}' | capacidad {self._capacidad} | ${self.tarifa_hora:,.0f}/hora"  # Texto


class AlquilerEquipo(Servicio):  # Servicio 2: alquiler de equipos
    """Alquiler de equipos con un cargo fijo de seguro."""

    def __init__(self, nombre=None, tarifa_hora=None, seguro=0):  # Constructor con seguro
        super().__init__(nombre, tarifa_hora)  # Valida nombre y tarifa
        if isinstance(seguro, bool) or not isinstance(seguro, (int, float)) or seguro < 0:  # Seguro no negativo
            raise ServicioInvalidoError(f"Seguro inválido: {seguro!r}")  # Error si es inválido
        self._seguro = float(seguro)  # Guarda el seguro

    def calcular_costo_base(self, horas):  # Sobrescribe el costo
        return self._tarifa_hora * horas + self._seguro  # Horas por tarifa más seguro fijo

    def validar_parametros(self, horas, **extra):  # Sobrescribe la validación
        if isinstance(horas, bool) or not isinstance(horas, (int, float)) or not 1 <= horas <= 72:  # Entre 1 y 72 horas
            raise ServicioInvalidoError(f"Horas de alquiler inválidas (1-72): {horas!r}")  # Error de horas

    def describir(self):  # Sobrescribe la descripción
        return f"Equipo '{self.nombre}' | ${self.tarifa_hora:,.0f}/hora + seguro ${self._seguro:,.0f}"  # Texto


class AsesoriaEspecializada(Servicio):  # Servicio 3: asesorías
    """Asesoría especializada; el nivel del consultor cambia el precio."""

    NIVELES = {"junior": 1.0, "senior": 1.5}  # Multiplicador de tarifa según nivel

    def __init__(self, nombre=None, tarifa_hora=None, nivel="junior"):  # Constructor con nivel
        super().__init__(nombre, tarifa_hora)  # Valida nombre y tarifa
        if nivel not in self.NIVELES:  # El nivel debe existir en el diccionario
            raise ServicioInvalidoError(f"Nivel de asesor inválido: {nivel!r}")  # Error si no existe
        self._nivel = nivel  # Guarda el nivel

    def calcular_costo_base(self, horas):  # Sobrescribe el costo
        return self._tarifa_hora * self.NIVELES[self._nivel] * horas  # Tarifa por nivel y horas

    def validar_parametros(self, horas, **extra):  # Sobrescribe la validación
        if isinstance(horas, bool) or not isinstance(horas, (int, float)) or not 1 <= horas <= 6:  # Entre 1 y 6 horas
            raise ServicioInvalidoError(f"Horas de asesoría inválidas (1-6): {horas!r}")  # Error de horas

    def describir(self):  # Sobrescribe la descripción
        return f"Asesoría '{self.nombre}' | nivel {self._nivel} | ${self.tarifa_hora:,.0f}/hora base"  # Texto
