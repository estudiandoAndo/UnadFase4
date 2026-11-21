# -*- coding: utf-8 -*-
"""Clase Cliente con validaciones robustas y encapsulación de datos personales."""
import itertools  # Para los contadores de id
import re  # Expresiones regulares para validar formatos

from entidades import EntidadBase  # Clase abstracta padre
from excepciones import ClienteInvalidoError, ParametroFaltanteError  # Errores propios

PATRON_NOMBRE = re.compile(r"^[A-Za-zÁÉÍÓÚáéíóúÑñÜü ]{3,60}$")  # Solo letras y espacios, 3 a 60 caracteres
PATRON_CORREO = re.compile(r"^[\w.+-]+@[\w-]+(\.[\w-]+)+$")  # Formato básico usuario@dominio.ext
PATRON_DOCUMENTO = re.compile(r"^\d{6,12}$")  # Documento: solo dígitos, de 6 a 12
PATRON_TELEFONO = re.compile(r"^3\d{9}$")  # Celular colombiano: 10 dígitos que empiezan por 3


def _requerido(valor, campo):  # Función auxiliar: verifica que el dato exista
    if valor is None or str(valor).strip() == "":  # Si es None o texto vacío...
        raise ParametroFaltanteError(f"Falta el parámetro obligatorio: {campo}")  # ...lanza error propio
    return str(valor).strip()  # Devuelve el valor limpio (sin espacios sobrantes)


class Cliente(EntidadBase):  # Cliente hereda de la entidad abstracta
    """Cliente de Software FJ con datos personales privados y validados."""

    _contador = itertools.count(1)  # Contador propio: ids 1, 2, 3... por tipo de entidad

    def __init__(self, nombre=None, documento=None, correo=None, telefono=None):  # Constructor
        super().__init__()  # Inicializa id y fecha en la clase padre
        try:  # Intenta asignar cada dato usando los setters validados
            self.nombre = nombre  # Valida y guarda el nombre
            self.documento = documento  # Valida y guarda el documento
            self.correo = correo  # Valida y guarda el correo
            self.telefono = telefono  # Valida y guarda el teléfono
        except ClienteInvalidoError as error:  # Si algún dato es inválido...
            raise ClienteInvalidoError("No se pudo crear el cliente") from error  # ...encadena la excepción original

    @property  # Getter del nombre
    def nombre(self):
        return self.__nombre  # Atributo privado (name mangling)

    @nombre.setter  # Setter con validación
    def nombre(self, valor):
        valor = _requerido(valor, "nombre")  # Debe existir
        if not PATRON_NOMBRE.match(valor):  # Debe cumplir el patrón
            raise ClienteInvalidoError(f"Nombre inválido: '{valor}'")  # Error si no cumple
        self.__nombre = valor.title()  # Guarda con formato Nombre Apellido

    @property  # Getter del documento
    def documento(self):
        return self.__documento  # Devuelve el documento privado

    @documento.setter  # Setter con validación
    def documento(self, valor):
        valor = _requerido(valor, "documento")  # Debe existir
        if not PATRON_DOCUMENTO.match(valor):  # Debe ser numérico de 6 a 12 dígitos
            raise ClienteInvalidoError(f"Documento inválido: '{valor}'")  # Error si no cumple
        self.__documento = valor  # Guarda el documento

    @property  # Getter del correo
    def correo(self):
        return self.__correo  # Devuelve el correo privado

    @correo.setter  # Setter con validación
    def correo(self, valor):
        valor = _requerido(valor, "correo")  # Debe existir
        if not PATRON_CORREO.match(valor):  # Debe tener formato de correo
            raise ClienteInvalidoError(f"Correo inválido: '{valor}'")  # Error si no cumple
        self.__correo = valor.lower()  # Guarda en minúsculas

    @property  # Getter del teléfono
    def telefono(self):
        return self.__telefono  # Devuelve el teléfono privado

    @telefono.setter  # Setter con validación
    def telefono(self, valor):
        valor = _requerido(valor, "teléfono")  # Debe existir
        if not PATRON_TELEFONO.match(valor):  # Debe ser celular de 10 dígitos
            raise ClienteInvalidoError(f"Teléfono inválido: '{valor}'")  # Error si no cumple
        self.__telefono = valor  # Guarda el teléfono

    def describir(self):  # Implementación del método abstracto
        return f"Cliente #{self.id}: {self.nombre} | Doc: {self.documento} | {self.correo}"  # Texto descriptivo
