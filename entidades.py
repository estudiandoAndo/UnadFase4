# -*- coding: utf-8 -*-
"""Clase abstracta que representa las entidades generales del sistema."""
from abc import ABC, abstractmethod  # Herramientas para clases abstractas
from datetime import datetime  # Para guardar la fecha de creación
import itertools  # Para generar identificadores consecutivos


class EntidadBase(ABC):  # Clase abstracta: no se puede instanciar directamente
    """Entidad general (Cliente, Servicio, Reserva): tiene id, fecha y una descripción."""

    _contador = itertools.count(1)  # Contador compartido que genera ids 1, 2, 3...

    def __init__(self):  # Constructor común a todas las entidades
        self._id = None  # El id se asigna al primer uso, así los objetos fallidos no gastan ids
        self._fecha_creacion = datetime.now()  # Guarda el momento de creación

    @property  # Expone el id como atributo de solo lectura (encapsulación)
    def id(self):  # Getter del id
        if self._id is None:  # Si aún no tiene id...
            self._id = next(type(self)._contador)  # ...toma el siguiente del contador de su tipo
        return self._id  # Devuelve el id privado

    @property  # Expone la fecha como atributo de solo lectura
    def fecha_creacion(self):  # Getter de la fecha
        return self._fecha_creacion  # Devuelve la fecha privada

    @abstractmethod  # Obliga a las subclases a implementar este método
    def describir(self):  # Cada entidad se describe a sí misma (polimorfismo)
        """Devuelve un texto que describe la entidad."""

    def __str__(self):  # Al imprimir una entidad se usa su descripción
        return self.describir()  # Delegamos en el método polimórfico
