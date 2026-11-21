# -*- coding: utf-8 -*-
"""Clase Reserva: integra cliente, servicio, duración y estado."""
import itertools  # Para los contadores de id
from cliente import Cliente  # Para verificar el tipo del cliente
from entidades import EntidadBase  # Entidad general
from excepciones import (  # Errores propios usados aquí
    CalculoInconsistenteError,
    OperacionNoPermitidaError,
    ReservaInvalidaError,
    ServicioInvalidoError,
    ServicioNoDisponibleError,
)
from logger_fj import obtener_logger  # Logger de eventos
from servicios import Servicio  # Para verificar el tipo del servicio

log = obtener_logger()  # Logger compartido del sistema


class Reserva(EntidadBase):  # Reserva hereda de la entidad abstracta
    """Reserva con estados: PENDIENTE -> CONFIRMADA -> PROCESADA (o CANCELADA / FALLIDA)."""

    _contador = itertools.count(1)  # Contador propio: ids 1, 2, 3... por tipo de entidad
    PENDIENTE, CONFIRMADA, CANCELADA, PROCESADA, FALLIDA = "PENDIENTE", "CONFIRMADA", "CANCELADA", "PROCESADA", "FALLIDA"  # Estados

    def __init__(self, cliente, servicio, horas, **extra):  # Constructor de la reserva
        super().__init__()  # Inicializa id y fecha
        if not isinstance(cliente, Cliente):  # El cliente debe ser un Cliente real
            raise ReservaInvalidaError("La reserva requiere un cliente válido")  # Error si no lo es
        if not isinstance(servicio, Servicio):  # El servicio debe ser un Servicio real
            raise ReservaInvalidaError("La reserva requiere un servicio válido")  # Error si no lo es
        if not servicio.disponible:  # No se reserva un servicio no disponible
            raise ServicioNoDisponibleError(f"El servicio '{servicio.nombre}' no está disponible")  # Error propio
        try:  # Valida horas y parámetros extra con la lógica del servicio
            servicio.validar_parametros(horas, **extra)  # Método polimórfico
        except ServicioInvalidoError as error:  # Si el servicio rechaza los parámetros...
            raise ReservaInvalidaError("Intento de reserva incorrecto") from error  # ...encadena el error original
        self._cliente = cliente  # Guarda el cliente
        self._servicio = servicio  # Guarda el servicio
        self._horas = horas  # Guarda la duración
        self._extra = extra  # Guarda parámetros opcionales (ej. asistentes)
        self._estado = Reserva.PENDIENTE  # Toda reserva nace pendiente
        self._costo_total = None  # Se calcula al procesar

    @property  # Getter del estado
    def estado(self):
        return self._estado  # Devuelve el estado actual

    @property  # Getter del costo
    def costo_total(self):
        return self._costo_total  # Devuelve el costo (None si no se ha procesado)

    @property  # Getter del cliente
    def cliente(self):
        return self._cliente  # Devuelve el cliente

    @property  # Getter del servicio
    def servicio(self):
        return self._servicio  # Devuelve el servicio

    def confirmar(self):  # Confirma la reserva
        if self._estado != Reserva.PENDIENTE:  # Solo se confirma lo pendiente
            raise OperacionNoPermitidaError(f"No se puede confirmar una reserva {self._estado}")  # Error propio
        self._estado = Reserva.CONFIRMADA  # Cambia el estado
        log.info(f"Reserva #{self.id} CONFIRMADA")  # Registra el evento

    def cancelar(self):  # Cancela la reserva
        if self._estado in (Reserva.CANCELADA, Reserva.PROCESADA):  # No se cancela lo ya cancelado o procesado
            raise OperacionNoPermitidaError(f"No se puede cancelar una reserva {self._estado}")  # Error propio
        self._estado = Reserva.CANCELADA  # Cambia el estado
        log.info(f"Reserva #{self.id} CANCELADA")  # Registra el evento

    def procesar(self, impuesto=None, descuento=None):  # Procesa y calcula el costo
        try:  # Bloque principal con try/except/else/finally
            if self._estado != Reserva.CONFIRMADA:  # Solo se procesa lo confirmado
                raise OperacionNoPermitidaError(f"Solo se procesan reservas CONFIRMADAS (actual: {self._estado})")  # Error
            costo = self._servicio.calcular_costo(self._horas, impuesto, descuento, **self._extra)  # Calcula el costo
        except OperacionNoPermitidaError:  # Si la operación no está permitida...
            raise  # ...se relanza tal cual para que el gestor la registre
        except (CalculoInconsistenteError, ServicioInvalidoError) as error:  # Si el cálculo falla...
            self._estado = Reserva.FALLIDA  # ...la reserva queda FALLIDA
            raise ReservaInvalidaError(f"Falló el procesamiento de la reserva #{self.id}") from error  # Encadena el error
        else:  # Solo se ejecuta si NO hubo excepciones
            self._costo_total = costo  # Guarda el costo calculado
            self._estado = Reserva.PROCESADA  # Marca como procesada
            log.info(f"Reserva #{self.id} PROCESADA. Total: ${costo:,.2f}")  # Registra el éxito
            return costo  # Devuelve el costo
        finally:  # Se ejecuta SIEMPRE, haya o no error
            log.debug(f"Fin del procesamiento de la reserva #{self.id} (estado: {self._estado})")  # Traza final

    def describir(self):  # Implementación del método abstracto
        costo = f"${self._costo_total:,.2f}" if self._costo_total is not None else "sin calcular"  # Texto del costo
        return (f"Reserva #{self.id} | {self._cliente.nombre} -> {self._servicio.nombre} | "  # Cliente y servicio
                f"{self._horas}h | {self._estado} | {costo}")  # Duración, estado y costo
