"""LA VISTA: menús de consola reutilizables (lo único que usa input/print).

No valida ni guarda nada: le pide todo al controlador y solo muestra lo que
este responde. Un MISMO menú (MenuCRUD) sirve para cualquier controlador
porque todos heredan de CrudBase y tienen los mismos métodos: eso es
polimorfismo. Los menús con opciones extra heredan de MenuCRUD y solo
sobrescriben lo que cambia.
"""
from shared.herramientas import (
    imprimir_titulo, imprimir_exito, imprimir_error, imprimir_info, confirmar
)


class MenuCRUD:

    def __init__(self, controlador, titulo=None):
        self.controlador = controlador
        self.titulo = titulo or controlador.nombre.upper() + "S"     # ESTUDIANTES, MATERIAS...

    # ---------- ayudas ----------
    def pausa(self):
        input("\nPresione Enter para continuar...")

    def pedir_entero(self, texto):
        # Devuelve el número, o None si el usuario no escribió un número
        try:
            return int(input(texto))
        except ValueError:
            return None

    def mostrar_resultado(self, exito, mensaje):
        # Los controladores devuelven (exito, mensaje)
        if exito:
            imprimir_exito(mensaje)
        else:
            imprimir_error(mensaje)

    @staticmethod
    def etiqueta_campo(campo):
        return campo.replace("_", " ").capitalize()       # "docente_id" -> "Docente id"

    # ---------- gancho: los menús hijos agregan opciones aquí ----------
    def opciones_extra(self):
        """Devuelve {"7": ("Texto de la opción", metodo)}."""
        return {}

    # ---------- el menú ----------
    def ejecutar(self):
        nombre = self.controlador.nombre
        while True:
            extras = self.opciones_extra()
            imprimir_titulo(self.titulo)
            print(f"  1. Crear {nombre}")
            print("  2. Ver todos")
            print("  3. Buscar")
            print("  4. Ver por id")
            print("  5. Actualizar")
            print("  6. Eliminar")
            for clave, (texto, _) in extras.items():
                print(f"  {clave}. {texto}")
            print("  0. Volver\n")
            opcion = input("Opción: ").strip()

            if opcion == "0":
                break
            acciones = {
                "1": self.crear, "2": self.ver_todos, "3": self.buscar,
                "4": self.ver_por_id, "5": self.actualizar, "6": self.eliminar,
            }
            for clave, (_, metodo) in extras.items():
                acciones[clave] = metodo
            accion = acciones.get(opcion)
            if accion is None:
                imprimir_error("Opción no válida")
                self.pausa()
            else:
                accion()

    # ---------- operaciones del CRUD ----------
    def crear(self):
        imprimir_titulo(f"CREAR {self.controlador.nombre.upper()}")
        datos = {}
        for campo in self.controlador.campos:          # un dato por cada campo del modelo
            datos[campo] = input(f"{self.etiqueta_campo(campo)}: ")
        exito, mensaje = self.controlador.crear(datos)
        self.mostrar_resultado(exito, mensaje)
        self.pausa()

    def ver_todos(self):
        imprimir_titulo(self.titulo)
        lista = self.controlador.leer()
        if len(lista) == 0:
            imprimir_info("No hay registros todavía.")
        else:
            for objeto in lista:
                print(f"  {objeto}")                   # polimorfismo: __str__ -> etiqueta()
            imprimir_info(f"Total: {len(lista)}")
        self.pausa()

    def buscar(self):
        imprimir_titulo(f"BUSCAR {self.controlador.nombre.upper()}")
        texto = input("Buscar: ")
        encontrados = self.controlador.buscar(texto)
        if len(encontrados) == 0:
            imprimir_info(f"Sin coincidencias para '{texto}'.")
        else:
            for objeto in encontrados:
                print(f"  {objeto}")
        self.pausa()

    def ver_por_id(self):
        imprimir_titulo(f"VER {self.controlador.nombre.upper()}")
        id_registro = self.pedir_entero("Id: ")
        objeto = self.controlador.obtener(id_registro)
        if objeto is None:
            imprimir_error("No encontrado")
        else:
            for clave, valor in objeto.a_diccionario().items():
                print(f"  {clave.capitalize()}: {valor}")
        self.pausa()

    def actualizar(self):
        imprimir_titulo(f"ACTUALIZAR {self.controlador.nombre.upper()}")
        id_registro = self.pedir_entero("Id: ")
        objeto = self.controlador.obtener(id_registro)
        if objeto is None:
            imprimir_error("No encontrado")
            self.pausa()
            return

        imprimir_info(f"Editando: {objeto.etiqueta()}")
        print("Deje en blanco lo que no quiera cambiar.\n")
        cambios = {}
        for campo in self.controlador.campos:
            actual = getattr(objeto, campo)            # igual que objeto.nombre, objeto.email...
            nuevo = input(f"{self.etiqueta_campo(campo)} [{actual}]: ").strip()
            if nuevo != "":
                cambios[campo] = nuevo

        exito, mensaje = self.controlador.actualizar(id_registro, cambios)
        self.mostrar_resultado(exito, mensaje)
        self.pausa()

    def eliminar(self):
        imprimir_titulo(f"ELIMINAR {self.controlador.nombre.upper()}")
        id_registro = self.pedir_entero("Id: ")
        objeto = self.controlador.obtener(id_registro)
        if objeto is None:
            imprimir_error("No encontrado")
            self.pausa()
            return

        imprimir_info(f"Se eliminará: {objeto.etiqueta()}")
        if confirmar("¿Confirma?"):
            exito, mensaje = self.controlador.eliminar(id_registro)
            self.mostrar_resultado(exito, mensaje)
        else:
            imprimir_info("Operación cancelada")
        self.pausa()


class MenuPrincipal:
    """Menú de nivel superior: recibe una lista de (texto, objeto con ejecutar())."""

    def __init__(self, titulo, opciones):
        self.titulo = titulo
        self.opciones = opciones

    def ejecutar(self):
        while True:
            imprimir_titulo(self.titulo)
            for numero, (texto, _) in enumerate(self.opciones, start=1):
                print(f"  {numero}. {texto}")
            print("  0. Salir\n")
            opcion = input("Opción: ").strip()

            if opcion == "0":
                imprimir_info("¡Hasta luego! 👋")
                break
            if opcion.isdigit() and 1 <= int(opcion) <= len(self.opciones):
                self.opciones[int(opcion) - 1][1].ejecutar()      # polimorfismo
            else:
                imprimir_error("Opción no válida")
                input("\nPresione Enter para continuar...")


def reporte(controlador):
    """Reporte polimórfico: sin un solo 'if', sirve para CUALQUIER controlador."""
    imprimir_titulo(f"REPORTE DE {controlador.nombre.upper()}S")
    registros = controlador.listar()
    for objeto in registros:
        print(f"  {objeto.etiqueta()}")          # cada modelo arma su propia etiqueta
    imprimir_info(f"Total: {len(registros)}")
