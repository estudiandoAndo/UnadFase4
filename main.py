# -*- coding: utf-8 -*-
"""Simulación de 18 operaciones de Software FJ (válidas e inválidas). El programa nunca se detiene."""
from gestor import GestorFJ  # Gestor central
from logger_fj import ARCHIVO_LOG, obtener_logger  # Logger y ruta del log

log = obtener_logger()  # Logger compartido


def titulo(numero, texto):  # Imprime el encabezado de cada operación
    print(f"\n[{numero:02d}] {texto}")  # Número y descripción


def main():  # Función principal
    log.info("===== INICIO DE LA SIMULACIÓN SOFTWARE FJ =====")  # Marca de inicio en el log
    fj = GestorFJ()  # Crea el sistema

    titulo(1, "Cliente válido (Ana)")  # Operación 1
    ana = fj.registrar_cliente("ana maría gómez", "1117500123", "ana@correo.com", "3101234567")  # Datos válidos
    titulo(2, "Cliente con correo inválido")  # Operación 2
    fj.registrar_cliente("Pedro Ruiz", "1117500456", "pedro-sin-arroba", "3109876543")  # Correo mal formado
    titulo(3, "Cliente válido (Carlos)")  # Operación 3
    carlos = fj.registrar_cliente("Carlos Pérez", "1117500789", "carlos@correo.com", "3205551234")  # Datos válidos
    titulo(4, "Cliente sin nombre (parámetro faltante)")  # Operación 4
    fj.registrar_cliente(None, "1117500999", "x@correo.com", "3101112233")  # Falta el nombre
    titulo(5, "Cliente con documento duplicado")  # Operación 5
    fj.registrar_cliente("Otra Persona", "1117500123", "otra@correo.com", "3001112233")  # Documento repetido

    titulo(6, "Servicio válido: sala de reuniones")  # Operación 6
    sala = fj.crear_servicio("sala", nombre="Sala Amazonas", tarifa_hora=50000, capacidad=10)  # Sala válida
    titulo(7, "Servicio válido: alquiler de equipo")  # Operación 7
    equipo = fj.crear_servicio("equipo", nombre="Video Beam", tarifa_hora=20000, seguro=15000)  # Equipo válido
    titulo(8, "Servicio válido: asesoría senior")  # Operación 8
    asesoria = fj.crear_servicio("asesoria", nombre="Asesoría en Python", tarifa_hora=80000, nivel="senior")  # Asesoría válida
    titulo(9, "Servicio inválido: tarifa negativa")  # Operación 9
    fj.crear_servicio("sala", nombre="Sala Rota", tarifa_hora=-100, capacidad=5)  # Tarifa negativa
    titulo(10, "Servicio inválido: tipo desconocido")  # Operación 10
    fj.crear_servicio("helicoptero", nombre="Heli", tarifa_hora=1000)  # Tipo que no existe

    titulo(11, "Reserva exitosa: sala 3h para Ana (6 asistentes)")  # Operación 11
    r1 = fj.crear_reserva(ana.id, sala.id, 3, asistentes=6)  # Reserva válida
    titulo(12, "Confirmar y procesar la reserva con 10% de descuento")  # Operación 12
    fj.ejecutar_sobre_reserva(r1.id, "confirmar")  # Confirma
    fj.ejecutar_sobre_reserva(r1.id, "procesar", impuesto=0.19, descuento=0.10)  # Procesa con descuento
    titulo(13, "Reserva fallida: demasiadas horas de sala")  # Operación 13
    fj.crear_reserva(ana.id, sala.id, 12)  # 12 horas excede el máximo de 8
    titulo(14, "Reserva fallida: cliente inexistente")  # Operación 14
    fj.crear_reserva(999, sala.id, 2)  # Cliente que no existe
    titulo(15, "Reserva fallida: servicio no disponible")  # Operación 15
    equipo.disponible = False  # Se marca el equipo como no disponible
    fj.crear_reserva(carlos.id, equipo.id, 5)  # Intento de reservarlo
    equipo.disponible = True  # Se vuelve a habilitar
    titulo(16, "Reserva de asesoría, cancelación y luego intento de procesarla")  # Operación 16
    r2 = fj.crear_reserva(carlos.id, asesoria.id, 2)  # Reserva válida
    fj.ejecutar_sobre_reserva(r2.id, "cancelar")  # Se cancela
    fj.ejecutar_sobre_reserva(r2.id, "procesar")  # Operación no permitida
    titulo(17, "Procesar una reserva sin confirmar")  # Operación 17
    r3 = fj.crear_reserva(carlos.id, equipo.id, 24)  # Reserva válida de equipo
    fj.ejecutar_sobre_reserva(r3.id, "procesar")  # Aún está pendiente: error
    titulo(18, "Cálculo inconsistente: descuento del 150%")  # Operación 18
    fj.ejecutar_sobre_reserva(r3.id, "confirmar")  # Se confirma correctamente
    fj.ejecutar_sobre_reserva(r3.id, "procesar", descuento=1.5)  # Descuento imposible

    print("\n=== RESUMEN FINAL ===")  # Encabezado del resumen
    fj.resumen()  # Totales del sistema
    print(f"\nEl sistema terminó sin caerse. Revisa el log en: {ARCHIVO_LOG}")  # Mensaje final
    log.info("===== FIN DE LA SIMULACIÓN =====")  # Marca de fin en el log


if __name__ == "__main__":  # Solo corre si se ejecuta este archivo directamente
    main()  # Llama a la función principal
