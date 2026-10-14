"""CONTROLADORES del negocio académico.

El CRUD ya está escrito UNA vez en CrudBase (views.py). Aquí cada controlador
solo aporta su configuración (MODELO, ARCHIVO, NOMBRE, CAMPOS_BUSCABLES) y
sus reglas de negocio en validar(). Los métodos propios (asignar_docente,
agregar_nota, boletin, ...) son lo único realmente nuevo.
"""
from models_academico import Estudiante, Docente, Materia, Matricula
from views import CrudBase


# =====================================================================
# ESTUDIANTES: carnet único
# =====================================================================
class EstudianteController(CrudBase):
    MODELO = Estudiante
    ARCHIVO = "data/estudiantes.json"
    NOMBRE = "estudiante"
    CAMPOS_BUSCABLES = ("nombre", "apellido", "email", "carnet")

    def validar(self, datos, id_actual=None):
        if id_actual is None:
            faltantes = self.faltantes(datos)
            if faltantes:
                return f"Faltan campos obligatorios: {', '.join(faltantes)}"
        if "carnet" in datos and str(datos["carnet"]).strip():
            carnet = str(datos["carnet"]).strip().upper()
            usados = {r["carnet"].upper() for r in self.registros()
                      if r["id"] != id_actual}
            if carnet in usados:
                return f"El carnet {carnet} ya está registrado"
        return None


# =====================================================================
# DOCENTES: email único
# =====================================================================
class DocenteController(CrudBase):
    MODELO = Docente
    ARCHIVO = "data/docentes.json"
    NOMBRE = "docente"
    CAMPOS_BUSCABLES = ("nombre", "apellido", "email", "especialidad")

    def validar(self, datos, id_actual=None):
        if id_actual is None:
            faltantes = self.faltantes(datos)
            if faltantes:
                return f"Faltan campos obligatorios: {', '.join(faltantes)}"
        if "email" in datos and str(datos["email"]).strip():
            email = str(datos["email"]).strip().lower()
            usados = {r["email"] for r in self.registros() if r["id"] != id_actual}
            if email in usados:
                return f"El email {email} ya está registrado"
        return None


# =====================================================================
# MATERIAS: código único, créditos de 0 a 10 (los valida el modelo)
# y el docente asignado tiene que existir (AGREGACIÓN por docente_id)
# =====================================================================
class MateriaController(CrudBase):
    MODELO = Materia
    ARCHIVO = "data/materias.json"
    NOMBRE = "materia"
    GENERO = "a"
    CAMPOS_BUSCABLES = ("nombre", "codigo")

    def __init__(self, docentes=None, archivo=None):
        super().__init__(archivo)
        # La materia USA al controlador de docentes: se le pasa el MISMO que usa el menú
        self.docentes = docentes if docentes is not None else DocenteController()

    def validar(self, datos, id_actual=None):
        if id_actual is None:
            faltantes = self.faltantes(datos)
            if faltantes:
                return f"Faltan campos obligatorios: {', '.join(faltantes)}"

        if "codigo" in datos and str(datos["codigo"]).strip():
            codigo = str(datos["codigo"]).strip().upper()
            for otra in self._lista:
                if otra.codigo == codigo and otra.id != id_actual:
                    return f"El código {codigo} ya está registrado"

        docente_id = datos.get("docente_id")
        if docente_id not in (None, "", "0"):          # vacío = materia sin docente
            try:
                docente_id = int(docente_id)
            except (TypeError, ValueError):
                return f"docente_id inválido: '{docente_id}'"
            if not self.docentes.existe(docente_id):
                return f"No existe un docente con id {docente_id}"
        return None

    # --- métodos propios de materias ---
    def asignar_docente(self, materia_id, docente_id):
        if not self.existe(materia_id):
            return False, f"No existe materia con id {materia_id}"
        if not self.docentes.existe(docente_id):
            return False, f"No existe docente con id {docente_id}"
        return self.actualizar(materia_id, {"docente_id": docente_id})

    def materias_de_docente(self, docente_id):
        return [m for m in self.listar() if m.docente_id == docente_id]


# =====================================================================
# MATRÍCULAS: une estudiante y materia, y guarda las notas
# =====================================================================
class MatriculaController(CrudBase):
    MODELO = Matricula
    ARCHIVO = "data/matriculas.json"
    NOMBRE = "matrícula"
    GENERO = "a"
    CAMPOS_BUSCABLES = ("periodo",)

    def __init__(self, estudiantes=None, materias=None, archivo=None):
        super().__init__(archivo)
        self.estudiantes = estudiantes if estudiantes is not None else EstudianteController()
        self.materias = materias if materias is not None else MateriaController()

    def validar(self, datos, id_actual=None):
        actual = self.obtener(id_actual) if id_actual is not None else None
        if actual is None:
            faltantes = self.faltantes(datos)
            if faltantes:
                return f"Faltan campos obligatorios: {', '.join(faltantes)}"

        # Al actualizar solo llegan los campos que cambian: el resto sale de la matrícula actual
        try:
            estudiante_id = int(datos.get("estudiante_id", actual.estudiante_id if actual else ""))
            materia_id = int(datos.get("materia_id", actual.materia_id if actual else ""))
        except (TypeError, ValueError):
            return "El estudiante y la materia se indican con su número de id"

        if not self.estudiantes.existe(estudiante_id):                     # regla 1
            return f"No existe un estudiante con id {estudiante_id}"
        if not self.materias.existe(materia_id):                           # regla 2
            return f"No existe una materia con id {materia_id}"

        # Regla 3: el modelo normaliza el período (vacío -> "2026-1"); se lo pedimos a él
        periodo = Matricula(0, estudiante_id, materia_id,
                            datos.get("periodo", actual.periodo if actual else "")).periodo
        for otra in self._lista:
            if (otra.id != id_actual and otra.estudiante_id == estudiante_id
                    and otra.materia_id == materia_id and otra.periodo == periodo):
                return (f"El estudiante {estudiante_id} ya está matriculado en la "
                        f"materia {materia_id} en el período {periodo}")
        return None

    # --- métodos propios de matrículas ---
    def agregar_nota(self, matricula_id, tipo, valor, peso=1):
        """Patrón: obtener el objeto, usar su método,
        atrapar el ValueError y volver a guardar el archivo."""
        matricula = self.obtener(matricula_id)
        if matricula is None:
            return False, f"No existe matrícula con id {matricula_id}"
        try:
            nota = matricula.agregar_nota(tipo, valor, peso)
        except ValueError as error:
            return False, str(error)
        self.guardar()          # sin esto la nota solo viviría en RAM y se perdería al cerrar
        return True, (f"Nota registrada ({nota}). "
                      f"Promedio: {matricula.promedio} · {matricula.estado}")

    def boletin(self, estudiante_id):
        estudiante = self.estudiantes.obtener(estudiante_id)
        if estudiante is None:
            return None

        matriculas = [m for m in self._lista if m.estudiante_id == estudiante_id]
        texto = "BOLETÍN DE NOTAS\n"
        texto += f"Estudiante: {estudiante.nombre_completo} (carnet {estudiante.carnet})\n"
        texto += "-" * 46 + "\n"
        if not matriculas:
            texto += "  No tiene matrículas registradas\n"
        promedios = []
        for m in matriculas:
            materia = self.materias.obtener(m.materia_id)
            nombre_materia = "materia eliminada" if materia is None else f"{materia.nombre} ({materia.codigo})"
            texto += f"{nombre_materia} · período {m.periodo}\n"
            if not m.notas:
                texto += "    sin notas todavía\n"
            for nota in m.notas:
                texto += f"    - {nota.tipo}: {nota.valor} (peso {nota.peso:g})\n"
            if m.notas:
                texto += f"    Promedio: {m.promedio} · {m.estado}\n"
                promedios.append(m.promedio)
        texto += "-" * 46 + "\n"
        if promedios:
            general = round(sum(promedios) / len(promedios), 2)
            texto += f"  PROMEDIO GENERAL: {general}  ({len(promedios)} materia(s) con notas)"
        else:
            texto += "  PROMEDIO GENERAL: sin notas registradas"
        return texto

    def reprobados(self):
        """Matrículas cuyo promedio está por debajo de la nota de aprobación."""
        return [m for m in self._lista if m.estado == "Reprobado"]

    def reporte_reprobados(self):
        texto = "ESTUDIANTES REPROBADOS\n" + "-" * 46 + "\n"
        reprobados = self.reprobados()
        if not reprobados:
            return texto + "  No hay estudiantes reprobados"
        for m in reprobados:
            estudiante = self.estudiantes.obtener(m.estudiante_id)
            materia = self.materias.obtener(m.materia_id)
            nombre_e = "estudiante eliminado" if estudiante is None else estudiante.nombre_completo
            nombre_m = "materia eliminada" if materia is None else materia.nombre
            texto += f"  {nombre_e} · {nombre_m} · promedio {m.promedio}\n"
        return texto + f"  Total: {len(reprobados)}"
