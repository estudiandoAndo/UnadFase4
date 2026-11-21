# -*- coding: utf-8 -*-
"""Configuración del archivo de logs donde se registran errores y eventos."""
import logging  # Módulo estándar de Python para registrar mensajes
import os  # Para construir rutas y crear la carpeta de logs

RUTA_LOGS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")  # Carpeta logs junto al código
ARCHIVO_LOG = os.path.join(RUTA_LOGS, "software_fj.log")  # Ruta completa del archivo de log


def obtener_logger(nombre="software_fj"):  # Devuelve un logger ya configurado
    """Crea (una sola vez) y devuelve el logger que escribe en logs/software_fj.log."""
    os.makedirs(RUTA_LOGS, exist_ok=True)  # Crea la carpeta de logs si no existe
    logger = logging.getLogger(nombre)  # Obtiene el logger por nombre
    if logger.handlers:  # Si ya fue configurado antes...
        return logger  # ...lo reutiliza para no duplicar mensajes
    logger.setLevel(logging.DEBUG)  # Registra todos los niveles (DEBUG, INFO, WARNING, ERROR)
    manejador = logging.FileHandler(ARCHIVO_LOG, encoding="utf-8")  # Escribe en archivo con tildes correctas
    formato = logging.Formatter("%(asctime)s | %(levelname)-8s | %(message)s")  # Fecha | nivel | mensaje
    manejador.setFormatter(formato)  # Aplica el formato al manejador
    logger.addHandler(manejador)  # Conecta el manejador al logger
    logger.propagate = False  # Evita que los mensajes salgan duplicados por la consola
    return logger  # Devuelve el logger listo para usar
