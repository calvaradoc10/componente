"""Lectura y escritura de archivos JSON.

Es la única parte del sistema que sabe CÓMO se guardan los datos.
Los controladores solo le piden leer() o guardar(datos); si mañana los
datos se guardaran en otra parte, solo cambiaría este archivo.
"""
import json
import os


class GestorJSON:

    def __init__(self, archivo):
        self.archivo = archivo

    def leer(self):
        """Devuelve la lista guardada en el archivo.
        Si el archivo todavía no existe, devuelve una lista vacía."""
        if not os.path.exists(self.archivo):
            return []

        with open(self.archivo, "r", encoding="utf-8") as f:
            contenido = f.read().strip()

        if contenido == "":
            return []

        try:
            datos = json.loads(contenido)
        except json.JSONDecodeError as error:
            # No devolvemos [] en silencio: el siguiente guardar() borraría
            # los datos que el usuario podría arreglar a mano.
            raise ValueError(f"El archivo {self.archivo} no tiene un JSON válido: {error}")

        if not isinstance(datos, list):
            raise ValueError(f"El archivo {self.archivo} debe contener una lista de registros")
        return datos

    def guardar(self, datos):
        """Escribe la lista completa en el archivo (crea la carpeta si no existe)."""
        carpeta = os.path.dirname(self.archivo)
        if carpeta:
            os.makedirs(carpeta, exist_ok=True)

        with open(self.archivo, "w", encoding="utf-8") as f:
            json.dump(datos, f, indent=2, ensure_ascii=False)
