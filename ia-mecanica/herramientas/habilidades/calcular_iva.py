"""
Habilidad: calcular_iva
Descripción: Calcula el precio final con IVA incluido
Creada por: SupremeBot
Fecha: 2026-03-12 00:31:40.978867
"""

def herramienta(nombre, descripcion):
    def decorador(func):
        func.es_habilidad = True
        func.nombre_habilidad = nombre
        func.descripcion_habilidad = descripcion
        return func
    return decorador


@herramienta("calcular_iva", "Calcula el precio final con IVA incluido (16%)")
def calcular_iva(precio_sin_iva: float) -> str:
    """Calcula el IVA y el precio final"""
    iva = precio_sin_iva * 0.16
    total = precio_sin_iva + iva
    return (f"📊 CÁLCULO DE IVA:\n"
            f"   Precio sin IVA: ${precio_sin_iva:.2f}\n"
            f"   IVA (16%): ${iva:.2f}\n"
            f"   TOTAL con IVA: ${total:.2f}")

