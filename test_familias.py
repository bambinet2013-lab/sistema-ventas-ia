#!/usr/bin/env python3
# test_familias.py

import logging
from capa_datos.aprendizaje_repo import AprendizajeRepositorio
from capa_datos.familia_repo import FamiliaRepositorio
from capa_negocio.ia_productos_service import IAProductosService

logging.basicConfig(level=logging.INFO)

def probar_familias():
    print("🧪 PRUEBA DE FAMILIAS DE PALABRAS")
    print("="*60)
    
    # Inicializar repositorios
    repo_aprendizaje = AprendizajeRepositorio()
    repo_familia = FamiliaRepositorio(repo_aprendizaje.conn)
    
    # Crear algunas familias de prueba
    print("\n📝 Creando familias de prueba...")
    
    # Familia LÁCTEOS
    id_lacteos = repo_familia.crear_familia("LACTEOS", "Productos lácteos")
    
    # Familia PASTILLAS FRENO
    id_pastillas = repo_familia.crear_familia("PASTILLAS_FRENO", "Sistemas de freno")
    
    # Registrar palabras y asignarlas a familias
    print("\n📝 Registrando palabras de prueba...")
    
    # Palabras de lácteos
    palabras_lacteos = ["LECHE", "QUESO", "YOGURT", "MANTEQUILLA"]
    for palabra in palabras_lacteos:
        repo_aprendizaje.registrar_uso(palabra, 4, 1)
        # Obtener ID de la palabra
        cursor = repo_aprendizaje.conn.cursor()
        cursor.execute("SELECT idpalabra FROM aprendizaje_palabras WHERE palabra = ?", (palabra,))
        idpalabra = cursor.fetchone()[0]
        repo_familia.asignar_palabra_a_familia(idpalabra, id_lacteos)
        print(f"   ✅ '{palabra}' → Familia LACTEOS")
    
    # Palabras de frenos
    palabras_frenos = ["PASTILLA", "FRENO", "BALATA", "ZAPATA"]
    for palabra in palabras_frenos:
        repo_aprendizaje.registrar_uso(palabra, 103, 2)
        cursor = repo_aprendizaje.conn.cursor()
        cursor.execute("SELECT idpalabra FROM aprendizaje_palabras WHERE palabra = ?", (palabra,))
        idpalabra = cursor.fetchone()[0]
        repo_familia.asignar_palabra_a_familia(idpalabra, id_pastillas)
        print(f"   ✅ '{palabra}' → Familia PASTILLAS_FRENO")
    
    # Probar IA con familias
    print("\n🤖 Probando IA con detección por familias:")
    print("-" * 40)
    
    ia = IAProductosService(repo_aprendizaje=repo_aprendizaje)
    ia.repo_familia = repo_familia  # Asignar repositorio de familias
    
    casos = [
        "LECHE COMPLETA",
        "YOGURT FRESA",
        "PASTILLAS DE FRENO",
        "BALATAS DELANTERAS",
        "QUESO BLANCO"
    ]
    
    for caso in casos:
        print(f"\n🔍 Analizando: '{caso}'")
        resultado = ia.analizar_producto(caso)
        if resultado:
            print(f"   ✅ Detectado por: {resultado.get('metodo', 'desconocido')}")
            if 'familia' in resultado:
                print(f"   👪 Familia: {resultado['familia']}")
            print(f"   📊 Categoría: {resultado['idcategoria']}, Impuesto: {resultado['id_impuesto']}")
        else:
            print("   ❌ No detectado")
    
    # Mostrar familias
    print("\n📊 FAMILIAS REGISTRADAS:")
    print("-" * 40)
    familias = repo_familia.obtener_todas_familias()
    for f in familias:
        print(f"   👪 {f['nombre_familia']}: {f['total_palabras']} palabras, {f['usos_totales'] or 0} usos")

if __name__ == "__main__":
    probar_familias()
