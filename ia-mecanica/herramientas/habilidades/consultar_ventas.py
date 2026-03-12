"""
Habilidad autogenerada: consultar_ventas
Descripción: Consulta información de ventas recientes.
Creada por: MegaBot en 2026-03-11 23:54:25.485204
"""

# Este decorador simula el registro de una herramienta
def herramienta(nombre, descripcion):
    def decorador(func):
        func.es_habilidad = True
        func.nombre_habilidad = nombre
        func.descripcion_habilidad = descripcion
        return func
    return decorador


@herramienta("consultar_ventas", "Consulta información de ventas recientes.")
def consultar_ventas(ultimas: int = 5) -> str:
    """Muestra las últimas ventas (simulado)."""
    import random
    from datetime import datetime, timedelta
    
    resultado = f"🛒 ÚLTIMAS {ultimas} VENTAS:\n"
    for i in range(ultimas):
        fecha = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        monto = random.randint(10, 500)
        resultado += f"  • Venta #{1000+i}: {fecha} - ${monto}\n"
    return resultado

