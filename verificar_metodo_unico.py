#!/usr/bin/env python3
# verificar_metodo_unico.py

import inspect
from capa_negocio.ia_productos_service import IAProductosService

def verificar_metodo_analizar():
    """
    Verifica únicamente el método analizar_producto
    """
    print("🔍 VERIFICANDO MÉTODO: analizar_producto")
    print("=" * 60)
    
    # Obtener el código fuente del método
    fuente = inspect.getsource(IAProductosService.analizar_producto)
    
    # Mostrar el método completo
    print("\n📄 CÓDIGO COMPLETO DEL MÉTODO:")
    print("-" * 60)
    print(fuente)
    
    print("\n" + "=" * 60)
    
    # Verificaciones específicas
    print("\n📋 VERIFICACIONES CLAVE:")
    print("-" * 60)
    
    verificaciones = {
        "Firma correcta": "def analizar_producto(self, nombre: str, codigo_barras: str = None)",
        "Tiene docstring": '"""' in fuente,
        "Normaliza texto": "self.normalizar_texto(nombre)" in fuente,
        "Bloque código barras": "# ===== NUEVO: Detección por código de barras" in fuente,
        "Inicializa pista_impuesto": "pista_impuesto = None" in fuente,
        "Llama detectar_por_codigo_barras": "self.detectar_por_codigo_barras" in fuente,
        "Verifica categoría": "if resultado_codigo.get('idcategoria')" in fuente,
        "Captura pista impuesto": "pista_impuesto = resultado_codigo.get('id_impuesto')" in fuente,
        "Bloque marcas": "# ===== DETECCIÓN POR MARCA" in fuente,
        "Bloque motos": "# 1. Intentar detectar si es producto de motos" in fuente,
        "Bloque aprendizaje": "# 2. Intentar con aprendizaje" in fuente,
        "Búsqueda por similitud": "resultados_similares = self.repo_aprendizaje.buscar_similares" in fuente,
        "Bloque familias": "# ===== NUEVO: Detección por familia" in fuente,
        "Pista impuesto final": "if pista_impuesto:" in fuente,
        "Return pista impuesto": "'metodo': 'codigo_barras_solo_impuesto'" in fuente,
        "Return final": "return None" in fuente
    }
    
    for descripcion, presente in verificaciones.items():
        if presente:
            print(f"   ✅ {descripcion}")
        else:
            print(f"   ❌ {descripcion} - NO ENCONTRADO")
    
    print("\n" + "=" * 60)
    
    # Verificar líneas específicas
    lineas = fuente.split('\n')
    print("\n📊 ANÁLISIS DE LÍNEAS CRÍTICAS:")
    print("-" * 60)
    
    lineas_criticas = [
        ("Línea 1 (firma)", "def analizar_producto"),
        ("Línea código barras", "# ===== NUEVO: Detección por código de barras"),
        ("Línea pista_impuesto", "pista_impuesto = None"),
        ("Línea resultado_codigo", "resultado_codigo = self.detectar_por_codigo_barras"),
        ("Línea categoría específica", "if resultado_codigo.get('idcategoria'):"),
        ("Línea return categoría", "return resultado_codigo"),
        ("Línea captura pista", "pista_impuesto = resultado_codigo.get('id_impuesto')"),
        ("Línea marcas", "# ===== DETECCIÓN POR MARCA"),
        ("Línea motos", "# 1. Intentar detectar si es producto de motos"),
        ("Línea aprendizaje", "# 2. Intentar con aprendizaje"),
        ("Línea familias", "# ===== NUEVO: Detección por familia"),
        ("Línea pista final", "if pista_impuesto:"),
        ("Línea return pista", "'metodo': 'codigo_barras_solo_impuesto'"),
        ("Línea final", "return None")
    ]
    
    for i, (descripcion, texto) in enumerate(lineas_criticas, 1):
        encontrado = any(texto in linea for linea in lineas)
        if encontrado:
            print(f"   ✅ {descripcion}: ENCONTRADA")
        else:
            print(f"   ❌ {descripcion}: NO ENCONTRADA")
    
    print("\n" + "=" * 60)
    print("🏁 VERIFICACIÓN COMPLETADA")

if __name__ == "__main__":
    verificar_metodo_analizar()
