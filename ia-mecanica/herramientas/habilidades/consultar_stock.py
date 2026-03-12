"""
Habilidad autogenerada: consultar_stock
Descripción: Consulta el stock actual de productos en la base de datos.
Creada por: MegaBot en 2026-03-11 23:53:07.898492
"""

# Este decorador simula el registro de una herramienta
def herramienta(nombre, descripcion):
    def decorador(func):
        func.es_habilidad = True
        func.nombre_habilidad = nombre
        func.descripcion_habilidad = descripcion
        return func
    return decorador


@herramienta("consultar_stock", "Consulta el stock actual de productos en la base de datos.")
def consultar_stock(producto: str = None) -> str:
    """Consulta stock de productos (simulado)."""
    # Aquí conectarías con tu BD real
    import random
    if producto:
        return f"Stock de '{producto}': {random.randint(0, 50)} unidades"
    else:
        productos = ["Laptop HP", "Mouse", "Teclado", "Monitor", "Impresora"]
        resultado = "📊 STOCK ACTUAL:\n"
        for p in productos:
            resultado += f"  • {p}: {random.randint(0, 50)} unidades\n"
        return resultado

