"""
Habilidad autogenerada: calculadora_basica
Descripción: Realiza operaciones aritméticas básicas (suma, resta, multiplicación, división).
Creada por: MegaBot en 2026-03-11 23:51:27.869480
"""

# Este decorador simula el registro de una herramienta
def herramienta(nombre, descripcion):
    def decorador(func):
        func.es_habilidad = True
        func.nombre_habilidad = nombre
        func.descripcion_habilidad = descripcion
        return func
    return decorador


@herramienta("calculadora_basica", "Realiza operaciones aritméticas básicas (suma, resta, multiplicación, división).")
def calculadora_basica(operacion: str, a: float, b: float) -> str:
    """Ejecuta una operación aritmética."""
    if operacion == "suma":
        return f"Resultado: {a + b}"
    elif operacion == "resta":
        return f"Resultado: {a - b}"
    elif operacion == "multiplica":
        return f"Resultado: {a * b}"
    elif operacion == "divide":
        if b == 0:
            return "Error: División por cero"
        return f"Resultado: {a / b}"
    else:
        return "Operación no soportada. Prueba con: suma, resta, multiplica, divide"

