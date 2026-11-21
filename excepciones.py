# -*- coding: utf-8 -*-
"""Excepciones personalizadas del sistema Software FJ."""


class ErrorSoftwareFJ(Exception):  # Excepción base: todas las demás heredan de ella
    """Error general del sistema; permite capturar cualquier error propio con un solo except."""


class ClienteInvalidoError(ErrorSoftwareFJ):  # Se lanza cuando los datos de un cliente no son válidos
    """Datos del cliente inválidos (nombre, documento, correo, teléfono o duplicado)."""


class ParametroFaltanteError(ErrorSoftwareFJ):  # Se lanza cuando falta un dato obligatorio
    """Falta un parámetro obligatorio (None o texto vacío)."""


class ServicioInvalidoError(ErrorSoftwareFJ):  # Se lanza cuando un servicio se crea o se usa mal
    """Parámetros del servicio inválidos (tarifa, horas, capacidad, tipo desconocido...)."""


class ServicioNoDisponibleError(ErrorSoftwareFJ):  # Se lanza si el servicio está marcado como no disponible
    """El servicio solicitado no está disponible para reservar."""


class ReservaInvalidaError(ErrorSoftwareFJ):  # Se lanza cuando una reserva no se puede crear o procesar
    """Intento de reserva incorrecto o fallo durante su procesamiento."""


class OperacionNoPermitidaError(ErrorSoftwareFJ):  # Se lanza ante cambios de estado que no están permitidos
    """Operación no permitida para el estado actual (ej. procesar una reserva cancelada)."""


class CalculoInconsistenteError(ErrorSoftwareFJ):  # Se lanza si un cálculo de costo da un resultado absurdo
    """Cálculo inconsistente (descuento fuera de rango, costo negativo, impuesto inválido)."""
