"""Herramientas de consola: colores, títulos y confirmación.

No tienen nada que ver con el negocio (las notas o las matrículas): solo ayudan a que
el menú se vea ordenado. Los colores usan códigos ANSI.
"""
import os

# En Windows, esta llamada vacía activa los colores ANSI en la consola.
os.system("")

VERDE = "\033[92m"
ROJO = "\033[91m"
AZUL = "\033[94m"
AMARILLO = "\033[93m"
NEGRITA = "\033[1m"
RESET = "\033[0m"


def imprimir_titulo(texto):
    print()
    print(f"{NEGRITA}{AZUL}{'=' * 50}{RESET}")
    print(f"{NEGRITA}{AZUL}  {texto}{RESET}")
    print(f"{NEGRITA}{AZUL}{'=' * 50}{RESET}")


def imprimir_exito(texto):
    print(f"{VERDE}✔ {texto}{RESET}")


def imprimir_error(texto):
    print(f"{ROJO}✘ {texto}{RESET}")


def imprimir_info(texto):
    print(f"{AMARILLO}ℹ {texto}{RESET}")


def confirmar(pregunta):
    """Pregunta s/n y devuelve True solo si el usuario responde 's' o 'si'."""
    respuesta = input(f"{pregunta} (s/n): ").strip().lower()
    return respuesta in ("s", "si", "sí")
