import json
import os


class GestorJSON:
    """Lee y guarda una lista de diccionarios en un archivo JSON."""

    def __init__(self, ruta):
        self._ruta = ruta

    def leer(self):
        if not os.path.exists(self._ruta):
            return []
        try:
            with open(self._ruta, "r", encoding="utf-8") as archivo:
                return json.load(archivo)
        except (json.JSONDecodeError, OSError):
            return []

    def guardar(self, registros):
        try:
            carpeta = os.path.dirname(self._ruta)
            if carpeta:
                os.makedirs(carpeta, exist_ok=True)
            with open(self._ruta, "w", encoding="utf-8") as archivo:
                json.dump(registros, archivo, ensure_ascii=False, indent=2)
            return True
        except OSError:
            return False