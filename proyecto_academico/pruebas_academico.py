"""Pruebas del negocio académico. Ejecutar con:  python pruebas_academico.py

Usa la carpeta data_prueba_academico/ para no tocar los datos reales.
Cada prueba imprime OK o FALLA; al final se muestra el resumen.
"""
import os
import shutil

from models_academico import Matricula
from views import CrudBase
from views_academico import (
    EstudianteController, DocenteController, MateriaController, MatriculaController
)
from menus import reporte

CARPETA = "data_prueba_academico"
total = 0
fallas = 0


def verificar(descripcion, condicion, detalle=""):
    global total, fallas
    total += 1
    if condicion:
        print(f"  OK     {descripcion}")
    else:
        fallas += 1
        print(f"  FALLA  {descripcion}   {detalle}")


def seccion(titulo):
    print()
    print("=" * 66)
    print(titulo)
    print("=" * 66)


def nuevos_controladores():
    """Crea los controladores leyendo los JSON de la carpeta de prueba."""
    docentes = DocenteController(f"{CARPETA}/docentes.json")
    estudiantes = EstudianteController(f"{CARPETA}/estudiantes.json")
    materias = MateriaController(docentes, f"{CARPETA}/materias.json")
    matriculas = MatriculaController(estudiantes, materias, f"{CARPETA}/matriculas.json")
    return docentes, estudiantes, materias, matriculas


if os.path.exists(CARPETA):
    shutil.rmtree(CARPETA)             # empezar siempre desde cero
docentes, estudiantes, materias, matriculas = nuevos_controladores()

# ---------------------------------------------------------------------
seccion("1. ABSTRACCIÓN: CrudBase es abstracta")
try:
    CrudBase()
    verificar("CrudBase no se puede instanciar", False)
except TypeError as error:
    verificar("CrudBase no se puede instanciar", True)
    print("         ->", error)


class SinValidar(CrudBase):          # hija que se olvida del método abstracto
    MODELO = Matricula


try:
    SinValidar()
    verificar("Una hija sin validar() tampoco se puede instanciar", False)
except TypeError:
    verificar("Una hija sin validar() tampoco se puede instanciar", True)

# ---------------------------------------------------------------------
seccion("2. DOCENTES (email único)")
ok, msg = docentes.crear({"nombre": "laura", "apellido": "mora", "email": "laura@unemi.edu.ec",
                          "titulo": "Ing.", "especialidad": "programación"})
verificar("Crear docente Laura", ok, msg); print("         ->", msg)
ok, msg = docentes.crear({"nombre": "carlos", "apellido": "vera", "email": "carlos@unemi.edu.ec",
                          "titulo": "Mgs.", "especialidad": "bases de datos"})
verificar("Crear docente Carlos", ok, msg)
ok, msg = docentes.crear({"nombre": "otra", "apellido": "persona", "email": "LAURA@unemi.edu.ec"})
verificar("Rechaza email de docente repetido", not ok and "ya está registrado" in msg, msg)
print("         ->", msg)
ok, msg = docentes.crear({"nombre": "", "apellido": "", "email": ""})
verificar("Rechaza docente sin datos obligatorios", not ok and "Faltan" in msg, msg)
ok, msg = docentes.crear({"nombre": "x", "apellido": "y", "email": "correo-malo"})
verificar("Rechaza email inválido (lo valida el modelo)", not ok and "inválido" in msg, msg)
ok, msg = docentes.actualizar(2, {"email": "laura@unemi.edu.ec"})
verificar("Al actualizar tampoco permite email repetido", not ok, msg)

# ---------------------------------------------------------------------
seccion("3. ESTUDIANTES (carnet único)")
ok, msg = estudiantes.crear({"nombre": "ana", "apellido": "pérez", "email": "ana@mail.com",
                             "carnet": "est-001"})
verificar("Crear estudiante Ana (carnet pasa a mayúsculas)", ok and "EST-001" in msg, msg)
print("         ->", msg)
ok, msg = estudiantes.crear({"nombre": "luis", "apellido": "gómez", "email": "luis@mail.com",
                             "carnet": "EST-002"})
verificar("Crear estudiante Luis", ok, msg)
ok, msg = estudiantes.crear({"nombre": "mia", "apellido": "ruiz", "email": "mia@mail.com",
                             "carnet": "est-001"})
verificar("Rechaza carnet repetido (sin importar mayúsculas)", not ok and "carnet" in msg, msg)
print("         ->", msg)
ok, msg = estudiantes.crear({"nombre": "mia", "apellido": "ruiz", "email": "mia@mail.com"})
verificar("Rechaza estudiante sin carnet", not ok and "Faltan" in msg, msg)
ok, msg = estudiantes.crear({"nombre": "mia", "apellido": "ruiz", "email": "mia@mail.com",
                             "carnet": "12"})
verificar("Rechaza carnet demasiado corto (lo valida el modelo)", not ok, msg)
ok, msg = estudiantes.actualizar(2, {"nombre": "luis alberto"})
verificar("Actualizar nombre de Luis", ok and estudiantes.obtener(2).nombre == "Luis Alberto", msg)
verificar("buscar('EST-00') encuentra 2 estudiantes", len(estudiantes.buscar("EST-00")) == 2)

# ---------------------------------------------------------------------
seccion("4. MATERIAS (código único, créditos 0-10, docente existente)")
ok, msg = materias.crear({"nombre": "programación orientada a objetos", "codigo": "poo101",
                          "creditos": "4", "docente_id": "1"})
verificar("Crear materia POO con docente 1", ok, msg); print("         ->", msg)
ok, msg = materias.crear({"nombre": "bases de datos", "codigo": "bd201", "creditos": "5"})
verificar("Crear materia BD sin docente", ok and materias.obtener(2).docente_id is None, msg)
ok, msg = materias.crear({"nombre": "otra", "codigo": "POO101", "creditos": "3"})
verificar("Rechaza código de materia repetido", not ok and "código" in msg, msg)
print("         ->", msg)
ok, msg = materias.crear({"nombre": "física", "codigo": "fis101", "creditos": "11"})
verificar("Rechaza créditos mayores a 10", not ok and "entre 0 y 10" in msg, msg)
print("         ->", msg)
ok, msg = materias.crear({"nombre": "física", "codigo": "fis101", "creditos": "-1"})
verificar("Rechaza créditos negativos", not ok, msg)
ok, msg = materias.crear({"nombre": "física", "codigo": "fis101", "creditos": "3", "docente_id": "99"})
verificar("Rechaza docente que no existe al crear", not ok and "No existe un docente" in msg, msg)
print("         ->", msg)
ok, msg = materias.asignar_docente(2, 2)
verificar("asignar_docente(2, 2) funciona", ok and materias.obtener(2).docente_id == 2, msg)
ok, msg = materias.asignar_docente(2, 99)
verificar("asignar_docente rechaza docente inexistente", not ok, msg); print("         ->", msg)
ok, msg = materias.asignar_docente(99, 1)
verificar("asignar_docente rechaza materia inexistente", not ok, msg)
verificar("materias_de_docente(1) devuelve 1 materia", len(materias.materias_de_docente(1)) == 1)

# ---------------------------------------------------------------------
seccion("5. MATRÍCULAS (estudiante y materia existentes, sin duplicados)")
ok, msg = matriculas.crear({"estudiante_id": "1", "materia_id": "1", "periodo": "2026-1"})
verificar("Matricular a Ana en POO", ok, msg); print("         ->", msg)
ok, msg = matriculas.crear({"estudiante_id": "2", "materia_id": "1", "periodo": "2026-1"})
verificar("Matricular a Luis en POO", ok, msg)
ok, msg = matriculas.crear({"estudiante_id": "1", "materia_id": "2", "periodo": ""})
verificar("Período vacío usa 2026-1 por defecto", ok and matriculas.obtener(3).periodo == "2026-1", msg)
ok, msg = matriculas.crear({"estudiante_id": "1", "materia_id": "1", "periodo": "2026-1"})
verificar("Rechaza matrícula duplicada (mismo estudiante, materia y período)", not ok, msg)
print("         ->", msg)
ok, msg = matriculas.crear({"estudiante_id": "1", "materia_id": "1", "periodo": "2026-2"})
verificar("Permite la misma materia en otro período", ok, msg)
ok, msg = matriculas.crear({"estudiante_id": "99", "materia_id": "1"})
verificar("Rechaza estudiante que no existe", not ok and "estudiante" in msg, msg)
ok, msg = matriculas.crear({"estudiante_id": "1", "materia_id": "99"})
verificar("Rechaza materia que no existe", not ok and "materia" in msg, msg)
ok, msg = matriculas.crear({"estudiante_id": "abc", "materia_id": "1"})
verificar("Rechaza ids que no son números", not ok, msg)

# ---------------------------------------------------------------------
seccion("6. NOTAS (0-20, tipo permitido, promedio ponderado)")
ok, msg = matriculas.agregar_nota(1, "deber", 18, 1)
verificar("Agregar deber 18 (peso 1)", ok, msg)
ok, msg = matriculas.agregar_nota(1, "examen", 15, 2)
verificar("Agregar examen 15 (peso 2)", ok, msg); print("         ->", msg)
promedio = matriculas.obtener(1).promedio
verificar("Promedio ponderado = (18*1 + 15*2) / 3 = 16", promedio == 16.0, f"salió {promedio}")
verificar("Estado de la matrícula 1 = Aprobado", matriculas.obtener(1).estado == "Aprobado")
ok, msg = matriculas.agregar_nota(1, "deber", 25)
verificar("Rechaza nota mayor a 20", not ok and "entre 0 y 20" in msg, msg); print("         ->", msg)
ok, msg = matriculas.agregar_nota(1, "deber", -1)
verificar("Rechaza nota negativa", not ok, msg)
ok, msg = matriculas.agregar_nota(1, "trabajo", 10)
verificar("Rechaza tipo de nota no permitido", not ok and "Tipo inválido" in msg, msg)
print("         ->", msg)
ok, msg = matriculas.agregar_nota(1, "deber", "diez")
verificar("Rechaza nota que no es número", not ok, msg)
ok, msg = matriculas.agregar_nota(99, "deber", 10)
verificar("Rechaza matrícula inexistente", not ok, msg)
verificar("Las notas inválidas no quedaron guardadas", len(matriculas.obtener(1).notas) == 2)
matriculas.agregar_nota(2, "deber", 8, 1)
matriculas.agregar_nota(2, "examen", 10, 2)               # (8 + 20) / 3 = 9.33
verificar("Promedio de Luis = 9.33 -> Reprobado",
          matriculas.obtener(2).promedio == 9.33 and matriculas.obtener(2).estado == "Reprobado")
verificar("Matrícula sin notas = 'Sin notas'", matriculas.obtener(3).estado == "Sin notas")

# ---------------------------------------------------------------------
seccion("7. ENCAPSULAMIENTO")
try:
    matriculas.obtener(1).notas.append("basura")
    verificar("matricula.notas devuelve copia de solo lectura (tupla)", False)
except AttributeError:
    verificar("matricula.notas devuelve copia de solo lectura (tupla)", True)
try:
    matriculas.obtener(1).promedio = 20
    verificar("El promedio es calculado: no se puede asignar a mano", False)
except AttributeError:
    verificar("El promedio es calculado: no se puede asignar a mano", True)
try:
    estudiantes.obtener(1).id = 50
    verificar("El id no se puede cambiar desde afuera", False)
except AttributeError:
    verificar("El id no se puede cambiar desde afuera", True)

# ---------------------------------------------------------------------
seccion("8. REPORTES")
print(matriculas.boletin(1)); print()
verificar("boletin(1) incluye el promedio general 16.0", "PROMEDIO GENERAL: 16.0" in matriculas.boletin(1))
verificar("boletin de estudiante inexistente devuelve None", matriculas.boletin(99) is None)
print(matriculas.reporte_reprobados())
verificar("Hay 1 matrícula reprobada", len(matriculas.reprobados()) == 1)
print()
print("Reporte polimórfico: la MISMA función con los 4 controladores")
for controlador in (estudiantes, docentes, materias, matriculas):
    reporte(controlador)

# ---------------------------------------------------------------------
seccion("9. PERSISTENCIA EN JSON (volver a leer los archivos desde cero)")
docentes2, estudiantes2, materias2, matriculas2 = nuevos_controladores()
verificar("Se recuperan 2 docentes", len(docentes2.leer()) == 2)
verificar("Se recuperan 2 estudiantes", len(estudiantes2.leer()) == 2)
verificar("Se recuperan 2 materias", len(materias2.leer()) == 2)
verificar("Se recuperan 4 matrículas", len(matriculas2.leer()) == 4)
verificar("Las notas (composición) siguen dentro de la matrícula 1",
          len(matriculas2.obtener(1).notas) == 2 and matriculas2.obtener(1).promedio == 16.0)
verificar("La docente de la materia 2 se recuperó (agregación por id)",
          materias2.obtener(2).docente_id == 2)
verificar("Los ids siguen la secuencia (siguiente = 5)", matriculas2.siguiente() == 5)

# ---------------------------------------------------------------------
seccion("10. ELIMINAR")
ok, msg = matriculas2.eliminar(4)
verificar("Eliminar matrícula 4", ok, msg); print("         ->", msg)
ok, msg = matriculas2.eliminar(4)
verificar("Eliminar de nuevo da error", not ok, msg)
verificar("Al eliminar la matrícula se van sus notas (composición)",
          matriculas2.obtener(1) is not None and len(matriculas2.leer()) == 3)
ok, msg = estudiantes2.eliminar(2)
verificar("Eliminar estudiante 2", ok, msg)
verificar("El boletín no se rompe si falta un estudiante", matriculas2.boletin(2) is None)
verificar("El reporte de reprobados no se rompe con estudiante eliminado",
          "estudiante eliminado" in matriculas2.reporte_reprobados())

print()
print("=" * 66)
print(f"RESULTADO: {total - fallas} de {total} pruebas OK" + ("" if fallas == 0 else f"  ({fallas} FALLAS)"))
print("=" * 66)
raise SystemExit(1 if fallas else 0)
