# main_academico.py es la VISTA del negocio académico.
# Ejecutar con:  python main_academico.py
from menus import MenuCRUD, MenuPrincipal, reporte
from shared.herramientas import imprimir_titulo, imprimir_info, imprimir_error
from views_academico import (
    EstudianteController, DocenteController, MateriaController, MatriculaController
)


class MenuMaterias(MenuCRUD):
    """MenuCRUD + una opción extra para asignar un docente a una materia."""

    def opciones_extra(self):
        return {"7": ("Asignar docente", self.asignar_docente)}

    def asignar_docente(self):
        imprimir_titulo("ASIGNAR DOCENTE")
        materia_id = self.pedir_entero("Id de la materia: ")
        imprimir_info("Docentes disponibles:")
        for docente in self.controlador.docentes.leer():
            print(f"  {docente}")
        docente_id = self.pedir_entero("Id del docente: ")
        exito, mensaje = self.controlador.asignar_docente(materia_id, docente_id)
        self.mostrar_resultado(exito, mensaje)
        self.pausa()


class MenuMatriculas(MenuCRUD):
    """MenuCRUD + 'Agregar nota' y 'Ver boletín'. Sobrescribe crear() para
    mostrar primero los estudiantes y las materias disponibles."""

    def opciones_extra(self):
        return {
            "7": ("Agregar nota", self.agregar_nota),
            "8": ("Ver boletín de un estudiante", self.ver_boletin),
        }

    def crear(self):
        imprimir_titulo("CREAR MATRÍCULA")
        imprimir_info("Estudiantes:")
        for estudiante in self.controlador.estudiantes.leer():
            print(f"  {estudiante}")
        imprimir_info("Materias:")
        for materia in self.controlador.materias.leer():
            print(f"  {materia}")

        datos = {
            "estudiante_id": input("\nId del estudiante: "),
            "materia_id": input("Id de la materia: "),
            "periodo": input("Período (Enter = 2026-1): "),
        }
        exito, mensaje = self.controlador.crear(datos)
        self.mostrar_resultado(exito, mensaje)
        self.pausa()

    def agregar_nota(self):
        imprimir_titulo("AGREGAR NOTA")
        matricula_id = self.pedir_entero("Id de la matrícula: ")
        tipo = input("Tipo (deber / lección / examen): ")
        valor = input("Nota (0 a 20): ")
        peso = input("Peso (Enter = 1): ").strip() or 1
        exito, mensaje = self.controlador.agregar_nota(matricula_id, tipo, valor, peso)
        self.mostrar_resultado(exito, mensaje)
        self.pausa()

    def ver_boletin(self):
        imprimir_titulo("BOLETÍN")
        estudiante_id = self.pedir_entero("Id del estudiante: ")
        texto = self.controlador.boletin(estudiante_id)
        if texto is None:
            imprimir_error("No existe ese estudiante")
        else:
            print(texto)
        self.pausa()


class MenuReportes:
    """No hereda de MenuCRUD, pero tiene ejecutar(): MenuPrincipal lo trata igual."""

    def __init__(self, estudiantes, docentes, materias, matriculas):
        self.controladores = [estudiantes, docentes, materias, matriculas]
        self.matriculas = matriculas

    def ejecutar(self):
        while True:
            imprimir_titulo("REPORTES")
            print("  1. Listado de una entidad (reporte polimórfico)")
            print("  2. Estudiantes reprobados")
            print("  0. Volver\n")
            opcion = input("Opción: ").strip()
            if opcion == "1":
                for numero, controlador in enumerate(self.controladores, start=1):
                    print(f"    {numero}. {controlador.nombre.capitalize()}s")
                eleccion = input("Entidad: ").strip()
                if eleccion.isdigit() and 1 <= int(eleccion) <= len(self.controladores):
                    reporte(self.controladores[int(eleccion) - 1])
                else:
                    imprimir_error("Entidad no válida")
                input("\nPresione Enter para continuar...")
            elif opcion == "2":
                print(self.matriculas.reporte_reprobados())
                input("\nPresione Enter para continuar...")
            elif opcion == "0":
                break
            else:
                imprimir_error("Opción no válida")
                input("\nPresione Enter para continuar...")


def crear_aplicacion():
    # Un solo controlador de cada tipo; los que dependen de otros reciben los MISMOS
    estudiantes = EstudianteController()
    docentes = DocenteController()
    materias = MateriaController(docentes)
    matriculas = MatriculaController(estudiantes, materias)
    return MenuPrincipal("SISTEMA ACADÉMICO", [
        ("Estudiantes", MenuCRUD(estudiantes, "ESTUDIANTES")),
        ("Docentes", MenuCRUD(docentes, "DOCENTES")),
        ("Materias", MenuMaterias(materias, "MATERIAS")),
        ("Matrículas", MenuMatriculas(matriculas, "MATRÍCULAS")),
        ("Reportes", MenuReportes(estudiantes, docentes, materias, matriculas)),
    ])


if __name__ == "__main__":
    try:
        crear_aplicacion().ejecutar()
    except (KeyboardInterrupt, EOFError):
        print("\nPrograma terminado.")
