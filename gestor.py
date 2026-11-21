# -*- coding: utf-8 -*-
"""Gestor central: maneja las listas internas y mantiene el sistema estable ante cualquier error."""
from cliente import Cliente  # Clase Cliente
from excepciones import (  # Errores propios
    ClienteInvalidoError,
    ErrorSoftwareFJ,
    ReservaInvalidaError,
    ServicioInvalidoError,
)
from logger_fj import obtener_logger  # Logger de eventos
from reserva import Reserva  # Clase Reserva
from servicios import AlquilerEquipo, AsesoriaEspecializada, ReservaSala  # Servicios concretos

log = obtener_logger()  # Logger compartido


class GestorFJ:  # Clase que coordina todo el sistema
    """Administra clientes, servicios y reservas sin base de datos (solo listas en memoria)."""

    TIPOS_SERVICIO = {"sala": ReservaSala, "equipo": AlquilerEquipo, "asesoria": AsesoriaEspecializada}  # Fábrica de servicios

    def __init__(self):  # Constructor
        self._clientes = []  # Lista interna de clientes
        self._servicios = []  # Lista interna de servicios
        self._reservas = []  # Lista interna de reservas

    def _buscar(self, lista, identificador, nombre_tipo):  # Búsqueda genérica por id
        for elemento in lista:  # Recorre la lista
            if elemento.id == identificador:  # Si coincide el id...
                return elemento  # ...lo devuelve
        raise ReservaInvalidaError(f"{nombre_tipo} con id {identificador} no existe")  # Si no, error propio

    def registrar_cliente(self, nombre=None, documento=None, correo=None, telefono=None):  # Alta de cliente
        try:  # Intenta crear el cliente
            if any(c.documento == str(documento).strip() for c in self._clientes):  # Documento duplicado
                raise ClienteInvalidoError(f"Ya existe un cliente con documento {documento}")  # Error propio
            cliente = Cliente(nombre, documento, correo, telefono)  # Crea y valida
        except ErrorSoftwareFJ as error:  # Cualquier error propio...
            log.error(f"Registro de cliente fallido: {error} | causa: {error.__cause__}")  # ...se registra
            print(f"   [ERROR] {error}" + (f" -> {error.__cause__}" if error.__cause__ else ""))  # ...y se informa
            return None  # El sistema sigue funcionando
        else:  # Si todo salió bien
            self._clientes.append(cliente)  # Agrega a la lista
            log.info(f"Cliente registrado: {cliente.describir()}")  # Registra el evento
            print(f"   [OK] {cliente.describir()}")  # Informa en pantalla
            return cliente  # Devuelve el cliente
        finally:  # Siempre se ejecuta
            log.debug("Fin de operación: registrar_cliente")  # Traza

    def crear_servicio(self, tipo, **datos):  # Alta de servicio
        try:  # Intenta crear el servicio
            clase = self.TIPOS_SERVICIO.get(tipo)  # Busca la clase según el tipo
            if clase is None:  # Tipo desconocido
                raise ServicioInvalidoError(f"Tipo de servicio desconocido: {tipo!r}")  # Error propio
            servicio = clase(**datos)  # Instancia la clase con los datos recibidos
        except TypeError as error:  # Parámetros mal nombrados o sobrantes
            nuevo = ServicioInvalidoError("Parámetros incorrectos para crear el servicio")  # Error propio
            log.error(f"Creación de servicio fallida: {nuevo} | causa: {error}")  # Registra
            print(f"   [ERROR] {nuevo} -> {error}")  # Informa
            return None  # Sigue funcionando
        except ErrorSoftwareFJ as error:  # Cualquier error propio
            log.error(f"Creación de servicio fallida: {error}")  # Registra
            print(f"   [ERROR] {error}")  # Informa
            return None  # Sigue funcionando
        else:  # Si todo salió bien
            self._servicios.append(servicio)  # Agrega a la lista
            log.info(f"Servicio creado: {servicio.describir()}")  # Registra
            print(f"   [OK] {servicio.describir()}")  # Informa
            return servicio  # Devuelve el servicio
        finally:  # Siempre se ejecuta
            log.debug("Fin de operación: crear_servicio")  # Traza

    def crear_reserva(self, id_cliente, id_servicio, horas, **extra):  # Alta de reserva
        try:  # Intenta crear la reserva
            cliente = self._buscar(self._clientes, id_cliente, "Cliente")  # Busca el cliente
            servicio = self._buscar(self._servicios, id_servicio, "Servicio")  # Busca el servicio
            reserva = Reserva(cliente, servicio, horas, **extra)  # Crea la reserva
        except ErrorSoftwareFJ as error:  # Cualquier error propio
            log.error(f"Reserva fallida: {error} | causa: {error.__cause__}")  # Registra
            print(f"   [ERROR] {error}" + (f" -> {error.__cause__}" if error.__cause__ else ""))  # Informa
            return None  # Sigue funcionando
        else:  # Si todo salió bien
            self._reservas.append(reserva)  # Agrega a la lista
            log.info(f"Reserva creada: {reserva.describir()}")  # Registra
            print(f"   [OK] {reserva.describir()}")  # Informa
            return reserva  # Devuelve la reserva
        finally:  # Siempre se ejecuta
            log.debug("Fin de operación: crear_reserva")  # Traza

    def ejecutar_sobre_reserva(self, id_reserva, accion, **parametros):  # Confirmar, cancelar o procesar
        try:  # Intenta la acción
            reserva = self._buscar(self._reservas, id_reserva, "Reserva")  # Busca la reserva
            resultado = getattr(reserva, accion)(**parametros)  # Llama al método por nombre
        except ErrorSoftwareFJ as error:  # Cualquier error propio
            log.error(f"Acción '{accion}' fallida en reserva {id_reserva}: {error} | causa: {error.__cause__}")  # Registra
            print(f"   [ERROR] {error}" + (f" -> {error.__cause__}" if error.__cause__ else ""))  # Informa
            return None  # Sigue funcionando
        else:  # Si todo salió bien
            print(f"   [OK] {reserva.describir()}")  # Informa el nuevo estado
            return resultado  # Devuelve el resultado de la acción
        finally:  # Siempre se ejecuta
            log.debug(f"Fin de operación: {accion}")  # Traza

    def resumen(self):  # Muestra los totales finales
        procesadas = [r for r in self._reservas if r.estado == Reserva.PROCESADA]  # Reservas exitosas
        total = sum(r.costo_total for r in procesadas)  # Suma de ingresos
        print(f"   Clientes: {len(self._clientes)} | Servicios: {len(self._servicios)} | "  # Totales
              f"Reservas: {len(self._reservas)} (procesadas: {len(procesadas)}) | Ingresos: ${total:,.2f}")  # Ingresos
        log.info(f"Resumen final: {len(self._clientes)} clientes, {len(self._servicios)} servicios, {len(self._reservas)} reservas")  # Log
