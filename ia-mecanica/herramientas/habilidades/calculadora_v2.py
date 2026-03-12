"""
Habilidad: calculadora_v2
Descripción: Calculadora básica
Creada por: SupremeBot
Fecha: 2026-03-12 00:32:36.028122
"""

def herramienta(nombre, descripcion):
    def decorador(func):
        func.es_habilidad = True
        func.nombre_habilidad = nombre
        func.descripcion_habilidad = descripcion
        return func
    return decorador


@herramienta("calculadora_v2", "Calculadora básica con operaciones aritméticas")
def calculadora_v2(operacion: str, a: float, b: float = 0) -> str:
    """Ejecuta operaciones aritméticas"""
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
    elif operacion == "raiz":
        return f"Resultado: {a ** 0.5}"
    else:
        return "Operación no soportada"

