import os

VERDE = "\033[92m"
ROJO = "\033[91m"
AZUL = "\033[94m"
AMARILLO = "\033[93m"
RESET = "\033[0m"


def limpiar_pantalla():
    os.system("cls" if os.name == "nt" else "clear")


def imprimir_color(texto, color):
    print(f"{color}{texto}{RESET}")


def imprimir_titulo(texto):
    print()
    imprimir_color("=" * 46, AZUL)
    imprimir_color(f"  {texto}", AZUL)
    imprimir_color("=" * 46, AZUL)


def imprimir_exito(texto):
    imprimir_color(f"✔ {texto}", VERDE)


def imprimir_error(texto):
    imprimir_color(f"✘ {texto}", ROJO)


def imprimir_info(texto):
    imprimir_color(f"ℹ {texto}", AMARILLO)


def confirmar(pregunta):
    respuesta = input(f"{pregunta} (s/n): ").strip().lower()
    return respuesta in ("s", "si", "sí")