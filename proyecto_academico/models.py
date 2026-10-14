"""Modelos base del sistema: ModeloBase y Persona.
Los modelos del negocio académico están en models_academico.py y heredan de estos."""
from abc import ABC, abstractmethod


# =====================================================================
# ABSTRACCIÓN: clase abstracta raíz de todos los modelos
# =====================================================================
class ModeloBase(ABC):
    """Contrato mínimo que todo modelo del sistema debe cumplir."""

    CAMPOS = ()          # atributos de clase que cada hijo redefine
    OBLIGATORIOS = ()

    def __init__(self, id_registro):
        self.__id = int(id_registro)

    @property
    def id(self):
        # Solo lectura: el id lo asigna el Controlador y nadie más lo cambia
        return self.__id

    @staticmethod
    def limpiar(texto):
        return str(texto).strip()

    # ---- MÉTODOS ABSTRACTOS: obligan a los hijos a implementarlos ----
    @abstractmethod
    def a_diccionario(self):
        """Objeto -> diccionario, para poder guardarlo en JSON."""

    @abstractmethod
    def etiqueta(self):
        """Una línea que describe al objeto. Cada modelo la arma a su manera."""

    # ---- MÉTODO CONCRETO: se hereda tal cual ----
    @classmethod
    def desde_diccionario(cls, datos):
        valores = {campo: datos.get(campo, "") for campo in cls.CAMPOS}
        return cls(datos["id"], **valores)

    def __str__(self):
        # POLIMORFISMO: el mismo print() muestra distinto según la clase
        return f"[{self.id}] {self.etiqueta()}"


# =====================================================================
# HERENCIA: Persona es la base de Estudiante y Docente
# =====================================================================
class Persona(ModeloBase):
    """Abstracta: agrupa lo que toda persona del sistema tiene."""

    CAMPOS = ("nombre", "apellido", "email")
    OBLIGATORIOS = ("nombre", "apellido", "email")

    def __init__(self, id_registro, nombre, apellido, email):
        super().__init__(id_registro)     # llama al __init__ del padre
        self.nombre = nombre
        self.apellido = apellido
        self.email = email

    @staticmethod
    def es_email_valido(texto):
        texto = str(texto).strip()
        if texto.count("@") != 1:
            return False
        usuario, dominio = texto.split("@")
        return len(usuario) > 0 and "." in dominio and not dominio.endswith(".")

    @property
    def nombre(self):
        return self.__nombre

    @nombre.setter
    def nombre(self, valor):
        valor = Persona.limpiar(valor)
        if not valor:
            raise ValueError("El nombre es obligatorio")
        self.__nombre = valor.title()

    @property
    def apellido(self):
        return self.__apellido

    @apellido.setter
    def apellido(self, valor):
        valor = Persona.limpiar(valor)
        if not valor:
            raise ValueError("El apellido es obligatorio")
        self.__apellido = valor.title()

    @property
    def email(self):
        return self.__email

    @email.setter
    def email(self, valor):
        valor = Persona.limpiar(valor)
        if not Persona.es_email_valido(valor):
            raise ValueError(f"Email inválido: '{valor}'")
        self.__email = valor.lower()

    @property
    def nombre_completo(self):
        return f"{self.__nombre} {self.__apellido}"

    def a_diccionario(self):
        return {
            "id": self.id,
            "nombre": self.__nombre,
            "apellido": self.__apellido,
            "email": self.__email,
        }
