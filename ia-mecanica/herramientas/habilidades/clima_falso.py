"""
Habilidad autogenerada: clima_falso
Descripción: Devuelve un informe meteorológico simulado para una ciudad.
Creada por: MegaBot en 2026-03-11 23:52:25.382522
"""

# Este decorador simula el registro de una herramienta
def herramienta(nombre, descripcion):
    def decorador(func):
        func.es_habilidad = True
        func.nombre_habilidad = nombre
        func.descripcion_habilidad = descripcion
        return func
    return decorador


@herramienta("clima_falso", "Devuelve un informe meteorológico simulado para una ciudad.")
def clima_falso(ciudad: str) -> str:
    """Simula una consulta meteorológica."""
    import random
    condiciones = ["☀️ soleado", "⛅ nublado", "🌧️ lluvioso", "🌪️ ventoso", "❄️ nevado"]
    temperatura = random.randint(5, 35)
    humedad = random.randint(30, 90)
    condicion = random.choice(condiciones)
    return f"Clima en {ciudad}: {condicion}, {temperatura}°C, humedad {humedad}%"

