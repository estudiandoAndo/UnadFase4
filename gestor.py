# -*- coding: utf-8 -*-
"""Gestor central: maneja las listas internas y mantiene el sistema estable ante cualquier error."""
from inspect import signature
from cliente import Cliente  # Clase Cliente
from excepciones import ( ClienteInvalidoError, ErrorSoftwareFJ, OperacionNoPermitidaError, ReservaInvalidaError, ServicioInvalidoError,) # Errores propios
from logger_fj import obtener_logger 
from reserva import Reserva  # Clase Reserva
from servicios import AlquilerEquipo, AsesoriaEspecializada, ReservaSala  # Servicios concretos
 
log = obtener_logger()  
class GestorFJ:  # Clase que coordina todo el sistema
    """Administra clientes, servicios y reservas sin base de datos (solo listas en memoria)."""
 
    TIPOS_SERVICIO = {"sala": ReservaSala, "equipo": AlquilerEquipo, "asesoria": AsesoriaEspecializada}  # Fábrica de servicios
 
    def __init__(self):  # Constructor
        self._clientes = []  # Lista interna de clientes
        self._servicios = []  # Lista interna de servicios
        self._reservas = []  # Lista interna de reservas
 
    @staticmethod  # No necesita acceder a self
    def _reportar_error(contexto, error):  # Registra y muestra un error propio (evita repetir código)
        causa = error.__cause__ 
        log.error(f"{contexto}: {error}" + (f" | causa: {causa}" if causa else ""))  # Solo muestra la causa si existe
        print(f"   [ERROR] {error}" + (f" -> {causa}" if causa else ""))  # Informa en pantalla
 
    @staticmethod  
    def _reportar_inesperado(contexto, error):  # Último recurso: errores que no son de Software FJ
        log.error(f"{contexto}: error inesperado {type(error).__name__}: {error}", exc_info=True)  
        print(f"   [ERROR] Error inesperado ({type(error).__name__}): {error}")  # Informa y el sistema sigue
 
    def _buscar(self, lista, identificador, nombre_tipo, error=ReservaInvalidaError):  # Búsqueda genérica por id
        # Optimización por Yimer Varon: usa next para terminar la búsqueda al primer coincidencia.
        elemento = next((item for item in lista if item.id == identificador), None)
        if elemento is not None:
            return elemento
        raise error(f"{nombre_tipo} con id {identificador} no existe")  # Si no, error propio según el tipo
 
    def registrar_cliente(self, nombre=None, documento=None, correo=None, telefono=None):  # Alta de cliente
        try:  # Intenta crear el cliente
            if any(c.documento == str(documento).strip() for c in self._clientes):  
                raise ClienteInvalidoError(f"Ya existe un cliente con documento {documento}")  
            cliente = Cliente(nombre, documento, correo, telefono)  # Crea y valida
        except ErrorSoftwareFJ as error:  # Cualquier error propio...
            self._reportar_error("Registro de cliente fallido", error) 
            return None  
        except Exception as error:  # Cualquier otro fallo imprevisto
            self._reportar_inesperado("Registro de cliente fallido", error)  # Se registra con detalle
            return None  # El sistema sigue funcionando
        else:  # Si todo salió bien
            self._clientes.append(cliente)  # Agrega a la lista
            log.info(f"Cliente registrado: {cliente.describir()}")  # Registra el evento
            print(f"   [OK] {cliente.describir()}")  # Informa en pantalla
            return cliente  # Devuelve el cliente
        finally: 

            log.debug("Fin de operación: registrar_cliente") 
    def crear_servicio(self, tipo, **datos):  
        
        try:  # Intenta crear el servicio
            clase = self.TIPOS_SERVICIO.get(tipo)  # Busca la clase según el tipo
            if clase is None: 
                raise ServicioInvalidoError(f"Tipo de servicio desconocido: {tipo!r}") 
            servicio = clase(**datos)  # Instancia la clase con los datos recibidos
        except TypeError as error:  
            nuevo = ServicioInvalidoError("Parámetros incorrectos para crear el servicio")
            nuevo.__cause__ = error  # Encadena el error original para que se vea la causa
            self._reportar_error("Creación de servicio fallida", nuevo)  # Registra e informa
            return None  
        except ErrorSoftwareFJ as error:  # Cualquier error propio
            self._reportar_error("Creación de servicio fallida", error)  # Registra e informa
            return None  
        except Exception as error:  # Cualquier otro fallo imprevisto
            self._reportar_inesperado("Creación de servicio fallida", error)  

        else:  # Si todo salió bien
            self._servicios.append(servicio)  # Agrega a la lista
            log.info(f"Servicio creado: {servicio.describir()}")  # Registra
            print(f"   [OK] {servicio.describir()}") 
            
            return servicio  # Devuelve el servicio
        finally:  
            log.debug("Fin de operación: crear_servicio")  
 
    def crear_reserva(self, id_cliente, id_servicio, horas, **extra):  # Alta de reserva
        try:  # Intenta crear la reserva
            cliente = self._buscar(self._clientes, id_cliente, "Cliente", ClienteInvalidoError)  # Busca el cliente
            servicio = self._buscar(self._servicios, id_servicio, "Servicio", ServicioInvalidoError)  
            reserva = Reserva(cliente, servicio, horas, **extra)  # Crea la reserva
        except ErrorSoftwareFJ as error:  # Cualquier error propio
            self._reportar_error("Reserva fallida", error)  # Registra e informa
            return None  # Sigue funcionando
        except Exception as error:  # Cualquier otro fallo imprevisto (por ejemplo, un parámetro extra desconocido)
            self._reportar_inesperado("Reserva fallida", error)  # Registra con detalle
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
            acciones = {  "confirmar": reserva.confirmar,"cancelar": reserva.cancelar, "procesar": reserva.procesar, } # Acciones permitidas y el método que ejecuta cada una

            if not isinstance(accion, str) or accion not in acciones:  # Acción desconocida
                raise OperacionNoPermitidaError(f"Acción no permitida: {accion!r}")  
            metodo = acciones[accion]  # Método a ejecutar
            try:  # Verifica los parámetros antes de ejecutar
                signature(metodo).bind(**parametros) 
            except TypeError as error:  # Parámetros que el método no acepta
                raise OperacionNoPermitidaError(
                    f"Parámetros incorrectos para la acción {accion!r}") from error  # Conserva la causa original
            
            resultado = metodo(**parametros)  # Ejecuta la acción
        except ErrorSoftwareFJ as error:  # Cualquier error propio
            self._reportar_error(f"Acción '{accion}' fallida en reserva {id_reserva}", error)  # Registra e informa
            return None  # Sigue funcionando
        except Exception as error:  # Cualquier otro fallo imprevisto
            self._reportar_inesperado(f"Acción '{accion}' fallida en reserva {id_reserva}", error)  # Registra con detalle
            return None  
        else:  # Si todo salió bien
            print(f"   [OK] {reserva.describir()}")  # Informa el nuevo estado
            return resultado  
        finally: 
            log.debug(f"Fin de operación: {accion}")  
 
    def resumen(self):  # Muestra los totales finales
        # Optimización por Yimer Varon: calcula conteo e ingresos en una sola pasada.
        cantidad_procesadas = 0
        total = 0
        for reserva in self._reservas:
            if reserva.estado == Reserva.PROCESADA:
                cantidad_procesadas += 1
                total += reserva.costo_total
        print(f"   Clientes: {len(self._clientes)} | Servicios: {len(self._servicios)} | "  # Totales
              f"Reservas: {len(self._reservas)} (procesadas: {cantidad_procesadas}) | Ingresos: ${total:,.2f}")  # Ingresos
        log.info(f"Resumen final: {len(self._clientes)} clientes, {len(self._servicios)} servicios, {len(self._reservas)} reservas")
