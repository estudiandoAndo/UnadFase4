# Software FJ – Fase 4 (Programación 213023, UNAD)

Sistema integral orientado a objetos en Python para gestionar **clientes, servicios y reservas**, sin base de datos.
Solo usa objetos, listas internas y un archivo de logs (`logs/software_fj.log`).

## Ejecutar
```bash
python main.py
```
Requiere Python 3.8 o superior. No necesita librerías externas.

## Estructura
| Archivo | Contenido |
|---|---|
| `entidades.py` | Clase abstracta `EntidadBase` (id, fecha, `describir()`) |
| `cliente.py` | `Cliente`: encapsulación (atributos privados) y validaciones con setters |
| `servicios.py` | `Servicio` (abstracta) + `ReservaSala`, `AlquilerEquipo`, `AsesoriaEspecializada` |
| `reserva.py` | `Reserva`: estados, confirmar, cancelar y procesar |
| `gestor.py` | `GestorFJ`: listas internas y control de errores para que el sistema no se caiga |
| `excepciones.py` | Excepciones personalizadas (base `ErrorSoftwareFJ`) |
| `logger_fj.py` | Configuración del archivo de logs |
| `main.py` | Simulación de 18 operaciones (válidas e inválidas) |

## Conceptos aplicados
- **Abstracción:** `EntidadBase` y `Servicio` (métodos abstractos).
- **Herencia y polimorfismo:** tres servicios sobrescriben `calcular_costo_base`, `validar_parametros` y `describir`.
- **Encapsulación:** datos del cliente privados con `@property` y validación.
- **Sobrecarga (simulada):** `calcular_costo(horas)`, `calcular_costo(horas, impuesto)`, `calcular_costo(horas, impuesto, descuento)` mediante parámetros opcionales.
- **Excepciones:** personalizadas, `try/except`, `try/except/else`, `try/except/finally` y encadenamiento con `raise ... from ...`.

## Reparto sugerido del equipo (5 integrantes)
1. `excepciones.py` + `logger_fj.py`
2. `entidades.py` + `cliente.py`
3. `servicios.py`
4. `reserva.py`
5. `gestor.py` + `main.py` + README

> Cada integrante debe hacer sus propios commits en el repositorio.
