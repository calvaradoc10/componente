"""BASE de todos los controladores del sistema (el CRUD escrito una sola vez).

CrudBase es una clase ABSTRACTA: tiene escrito UNA SOLA VEZ todo el CRUD
(crear, leer, buscar, actualizar, eliminar y guardar en JSON). Cada
controlador hijo solo aporta:
  - su configuración: MODELO, ARCHIVO, NOMBRE, CAMPOS_BUSCABLES
  - sus reglas propias, en validar() (método abstracto, obligatorio)
  - los métodos que solo él necesita (asignar_docente, agregar_nota, boletin, ...)

Todos los métodos que modifican datos devuelven una tupla (exito, mensaje):
la vista (main.py) solo muestra el mensaje, nunca valida ni guarda.
"""
from abc import ABC, abstractmethod

from shared.json_manager import GestorJSON


# =====================================================================
# CLASE BASE ABSTRACTA: el CRUD escrito una sola vez
# =====================================================================
class CrudBase(ABC):
    MODELO = None              # clase del modelo que maneja (Estudiante, Materia...)
    ARCHIVO = ""               # archivo JSON donde guarda sus registros
    NOMBRE = "registro"        # nombre en singular, para mensajes y títulos
    GENERO = "o"               # "o" o "a": para escribir "creado" / "creada"
    CAMPOS_BUSCABLES = ()      # atributos del modelo donde busca buscar()

    def __init__(self, archivo=None):
        self.gestor = GestorJSON(archivo or self.ARCHIVO)
        # Se lee el JSON y cada diccionario se convierte en un objeto
        self._lista = [self.MODELO.desde_diccionario(d) for d in self.gestor.leer()]

    # ---------- datos que usa el menú para armar títulos y formularios ----------
    @property
    def nombre(self):
        return self.NOMBRE

    @property
    def campos(self):
        return self.MODELO.CAMPOS

    # ---------- el contrato: lo único que cada hijo DEBE escribir ----------
    @abstractmethod
    def validar(self, datos, id_actual=None):
        """Devuelve un texto con el error si los datos no sirven, o None si están bien.
        id_actual es None al crear, y el id del registro al actualizar."""

    # ---------- gancho opcional: los hijos pueden sobrescribirlo ----------
    def preparar(self, datos):
        """Último ajuste a los datos antes de construir el objeto."""
        return datos

    # ---------- guardar / leer ----------
    def guardar(self):
        self.gestor.guardar([objeto.a_diccionario() for objeto in self._lista])

    def leer(self):
        return self._lista

    listar = leer              # otro nombre para lo mismo

    def registros(self):
        """Los registros como diccionarios (útil para validar sin tocar los objetos)."""
        return [objeto.a_diccionario() for objeto in self._lista]

    def obtener(self, id_registro):
        for objeto in self._lista:
            if objeto.id == id_registro:
                return objeto
        return None

    def existe(self, id_registro):
        return self.obtener(id_registro) is not None

    def siguiente(self):
        mayor = 0
        for objeto in self._lista:
            if objeto.id > mayor:
                mayor = objeto.id
        return mayor + 1

    def buscar(self, texto):
        texto = str(texto).strip().lower()
        encontrados = []
        if texto == "":
            return encontrados
        for objeto in self._lista:
            for campo in self.CAMPOS_BUSCABLES:
                if texto in str(getattr(objeto, campo)).lower():
                    encontrados.append(objeto)
                    break
        return encontrados

    def faltantes(self, datos):
        """Campos obligatorios del modelo que vienen vacíos."""
        return [c for c in self.MODELO.OBLIGATORIOS if not str(datos.get(c, "")).strip()]

    # ---------- MÉTODO PLANTILLA: los pasos fijos de crear() ----------
    def crear(self, datos):
        error = self.validar(datos)                     # 1. reglas del hijo
        if error:
            return False, error
        datos = self.preparar(datos)                    # 2. ajuste opcional
        try:                                            # 3. el modelo se valida solo
            valores = {c: datos.get(c, "") for c in self.MODELO.CAMPOS}
            objeto = self.MODELO(self.siguiente(), **valores)
        except ValueError as error:
            return False, str(error)
        self._lista.append(objeto)                      # 4. agregar y guardar
        self.guardar()
        return True, f"{self.NOMBRE.capitalize()} cread{self.GENERO}: {objeto.etiqueta()}"

    def actualizar(self, id_registro, cambios):
        if not cambios:
            return False, "No se indicó ningún cambio"
        actual = self.obtener(id_registro)
        if actual is None:
            return False, f"No existe {self.NOMBRE} con id {id_registro}"
        error = self.validar(cambios, id_actual=id_registro)
        if error:
            return False, error
        # Se arma un objeto NUEVO con los cambios. Si algo falla, el viejo queda igual.
        try:
            nuevo = self.MODELO.desde_diccionario({**actual.a_diccionario(), **cambios})
        except ValueError as error:
            return False, str(error)
        self._lista[self._lista.index(actual)] = nuevo
        self.guardar()
        return True, f"{self.NOMBRE.capitalize()} {id_registro} actualizad{self.GENERO}"

    def eliminar(self, id_registro):
        objeto = self.obtener(id_registro)
        if objeto is None:
            return False, f"No existe {self.NOMBRE} con id {id_registro}"
        self._lista.remove(objeto)
        self.guardar()
        return True, f"{self.NOMBRE.capitalize()} {id_registro} eliminad{self.GENERO}"
