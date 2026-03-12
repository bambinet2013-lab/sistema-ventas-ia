"""
Habilidad: clima_avanzado
Descripción: Pronóstico del clima
Creada por: SupremeBot
Fecha: 2026-03-12 00:32:50.862286
"""

def herramienta(nombre, descripcion):
    def decorador(func):
        func.es_habilidad = True
        func.nombre_habilidad = nombre
        func.descripcion_habilidad = descripcion
        return func
    return decorador


@herramienta("clima_avanzado", "Pronóstico del clima para una ciudad")
def clima_avanzado(ciudad: str) -> str:
    """Simula pronóstico del clima"""
    import random
    condiciones = ["☀️ Soleado", "⛅ Parcialmente nublado", "🌧️ Lluvioso", "🌪️ Ventoso", "❄️ Nevado"]
    temp = random.randint(5, 35)
    humedad = random.randint(30, 95)
    viento = random.randint(0, 30)
    
    return (f"🌍 CLIMA EN {ciudad.upper()}\n"
            f"   Condición: {random.choice(condiciones)}\n"
            f"   Temperatura: {temp}°C\n"
            f"   Humedad: {humedad}%\n"
            f"   Viento: {viento} km/h")

