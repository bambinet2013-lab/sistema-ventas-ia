#!/usr/bin/env python3
# test_normalizacion.py

import logging
from capa_negocio.ia_productos_service import IAProductosService

# Configurar logging para ver mensajes
logging.basicConfig(level=logging.INFO)

def probar_normalizacion():
    """
    Prueba la función de normalización de textos
    """
    print("\n🧪 PRUEBA DE NORMALIZACIÓN DE TEXTOS")
    print("="*60)
    
    ia = IAProductosService()
    
    casos = [
        ("CAFÉ YOCOIMA", "CAFE YOCOIMA"),
        ("ACEITE DE OLIVA", "ACEITE DE OLIVA"),
        ("PIÑA COLADA", "PINA COLADA"),
        ("JABÓN LÍQUIDO", "JABON LIQUIDO"),
        ("MOTOR PIÑÓN", "MOTOR PINON"),
        ("CAFÉ CON LECHE", "CAFE CON LECHE"),
        ("ÉXITO", "EXITO"),
        ("ACCIDENTE", "ACCIDENTE"),  # Sin tildes
        ("CANCIÓN", "CANCION"),
        ("CORAZÓN", "CORAZON"),
        ("AVIÓN", "AVION"),
        ("FERRETERÍA", "FERRETERIA"),
        ("ALMACÉN", "ALMACEN"),
        ("COMPRACIÓN", "COMPRACION"),
        ("TELÉFONO", "TELEFONO"),
        ("PÁGINA", "PAGINA"),
        ("ÚTILES", "UTILES"),
        ("DRÁCULA", "DRACULA"),
    ]
    
    print("\n📋 CASOS DE PRUEBA:")
    print("-"*60)
    
    exitosos = 0
    fallidos = 0
    
    for i, (original, esperado) in enumerate(casos, 1):
        normalizado = ia.normalizar_texto(original)
        es_correcto = (normalizado == esperado)
        
        if es_correcto:
            exitosos += 1
            marca = "✅"
        else:
            fallidos += 1
            marca = "❌"
        
        print(f"{marca} Caso {i:2d}:")
        print(f"   Original:   '{original}'")
        print(f"   Normalizado: '{normalizado}'")
        print(f"   Esperado:    '{esperado}'")
        print(f"   Resultado:   {'CORRECTO' if es_correcto else 'INCORRECTO'}")
        print()
    
    print("="*60)
    print(f"📊 RESULTADOS: {exitosos} exitosos, {fallidos} fallidos")
    print(f"🎯 Precisión: {exitosos/len(casos)*100:.1f}%")
    print("="*60)
    
    # Probar análisis completo con algunos productos
    print("\n🛒 PRUEBA DE ANÁLISIS COMPLETO")
    print("="*60)
    
    productos_prueba = [
        "CAFÉ YOCOIMA",
        "JABÓN LÍQUIDO",
        "ACEITE DE OLIVA",
        "PIÑA COLADA",
        "PASTILLAS DE FRENO",
        "MOTOR PIÑÓN"
    ]
    
    for producto in productos_prueba:
        print(f"\n📦 Producto: '{producto}'")
        resultado = ia.analizar_producto(producto)
        
        if resultado:
            print(f"   ✅ Detectado:")
            print(f"      - Método: {resultado.get('metodo', 'desconocido')}")
            print(f"      - Categoría: {resultado.get('idcategoria', 'N/A')}")
            print(f"      - Impuesto: {resultado.get('id_impuesto', 'N/A')}")
            print(f"      - Confianza: {resultado.get('confianza', 0):.0%}")
            if 'palabra' in resultado:
                print(f"      - Palabra: '{resultado['palabra']}'")
        else:
            print(f"   ❌ No detectado")
    
    print("\n" + "="*60)
    print("🏁 PRUEBA COMPLETADA")

def verificar_metodos_aprendizaje():
    """
    Verifica que los métodos de aprendizaje estén disponibles
    """
    print("\n🔍 VERIFICANDO MÉTODOS DE APRENDIZAJE")
    print("="*60)
    
    ia = IAProductosService()
    
    # Verificar si tiene repo_aprendizaje
    if hasattr(ia, 'repo_aprendizaje') and ia.repo_aprendizaje:
        print("✅ repo_aprendizaje disponible")
        
        # Verificar método buscar_similares
        if hasattr(ia.repo_aprendizaje, 'buscar_similares'):
            print("✅ método buscar_similares disponible")
        else:
            print("❌ método buscar_similares NO disponible")
        
        # Verificar método buscar_por_palabra
        if hasattr(ia.repo_aprendizaje, 'buscar_por_palabra'):
            print("✅ método buscar_por_palabra disponible")
        else:
            print("❌ método buscar_por_palabra NO disponible")
    else:
        print("⚠️ repo_aprendizaje NO disponible (esto puede ser normal en pruebas)")

if __name__ == "__main__":
    print("🚀 INICIANDO PRUEBAS DE NORMALIZACIÓN")
    print("="*60)
    
    # Verificar métodos primero
    verificar_metodos_aprendizaje()
    
    # Probar normalización
    probar_normalizacion()
