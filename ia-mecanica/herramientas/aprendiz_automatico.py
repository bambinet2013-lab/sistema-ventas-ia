#!/usr/bin/env python3
"""
Sistema de Auto-aprendizaje para el Mecánico de Ventas
Aprende de cada error y cómo solucionarlo
"""

import json
import os
from datetime import datetime
import subprocess

# Archivos de conocimiento
ALERTAS_FILE = "alertas_detectadas.json"
CONOCIMIENTO_FILE = "conocimiento_aprendido.json"
SOLUCIONES_FILE = "soluciones_aplicadas.json"

class AprendizAutomatico:
    def __init__(self):
        self.conocimiento = self.cargar_conocimiento()
        self.alertas = self.cargar_alertas()
        self.soluciones = self.cargar_soluciones()
    
    def cargar_conocimiento(self):
        """Carga la base de conocimiento aprendido"""
        try:
            with open(CONOCIMIENTO_FILE, 'r') as f:
                return json.load(f)
        except:
            return {
                "patrones": [],
                "soluciones_exitosas": {},
                "estadisticas": {
                    "total_alertas": 0,
                    "alertas_resueltas": 0,
                    "tasa_exito": 0
                }
            }
    
    def guardar_conocimiento(self):
        with open(CONOCIMIENTO_FILE, 'w') as f:
            json.dump(self.conocimiento, f, indent=2)
    
    def cargar_alertas(self):
        try:
            with open(ALERTAS_FILE, 'r') as f:
                return json.load(f)
        except:
            return []
    
    def cargar_soluciones(self):
        """Carga las soluciones aplicadas (diccionario)"""
        try:
            with open(SOLUCIONES_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}  # ¡Importante: es un diccionario, no lista!
    
    def guardar_soluciones(self):
        with open(SOLUCIONES_FILE, 'w') as f:
            json.dump(self.soluciones, f, indent=2)
    
    def analizar_patrones(self):
        """Analiza alertas repetitivas para encontrar patrones"""
        conteo = {}
        for alerta in self.alertas[-50:]:  # Últimas 50 alertas
            # Limpiar título de emojis
            titulo = alerta['titulo']
            for emoji in ['🔴', '⚠️', '✅', '🔵']:
                titulo = titulo.replace(emoji, '')
            titulo = titulo.strip()
            
            if titulo not in conteo:
                conteo[titulo] = {
                    "cantidad": 0,
                    "ultima_vez": alerta['timestamp'],
                    "nivel": alerta['nivel'],
                    "mensajes": []
                }
            conteo[titulo]["cantidad"] += 1
            conteo[titulo]["ultima_vez"] = alerta['timestamp']
            conteo[titulo]["mensajes"].append(alerta['mensaje'])
        
        # Identificar patrones problemáticos
        for error, datos in conteo.items():
            if datos["cantidad"] >= 2:  # A partir de 2 repeticiones ya es patrón
                self.aprender_patron(error, datos)
    
    def aprender_patron(self, error, datos):
        """Aprende un patrón de error y sugiere solución"""
        patron = {
            "error": error,
            "frecuencia": datos["cantidad"],
            "ultima_vez": datos["ultima_vez"],
            "nivel": datos["nivel"],
            "ejemplos": datos["mensajes"][-3:],  # Últimos 3 ejemplos
            "soluciones_posibles": self.buscar_soluciones(error),
            "aprendido": datetime.now().isoformat()
        }
        
        # Verificar si ya conocemos este patrón
        conocido = False
        for p in self.conocimiento["patrones"]:
            if p["error"] == error:
                p["frecuencia"] = datos["cantidad"]
                p["ultima_vez"] = datos["ultima_vez"]
                p["ejemplos"] = datos["mensajes"][-3:]
                conocido = True
                break
        
        if not conocido:
            self.conocimiento["patrones"].append(patron)
        
        self.guardar_conocimiento()
    
    def buscar_soluciones(self, error):
        """Busca soluciones previas para este error"""
        return self.soluciones.get(error, [])
    
    def sugerir_solucion(self, alerta):
        """Sugiere una solución basada en aprendizaje previo"""
        # Limpiar título de emojis
        titulo = alerta['titulo']
        for emoji in ['🔴', '⚠️', '✅', '🔵']:
            titulo = titulo.replace(emoji, '')
        titulo = titulo.strip()
        
        # Buscar en conocimiento
        for patron in self.conocimiento["patrones"]:
            if patron["error"] == titulo:
                if patron.get("soluciones_posibles"):
                    return {
                        "sugerencia": f"🤖 He visto este error {patron['frecuencia']} veces antes",
                        "soluciones": patron["soluciones_posibles"],
                        "confianza": min(patron['frecuencia'] * 10, 90)
                    }
        
        # Sugerencias por defecto según el tipo
        if "SIN VENTAS" in titulo:
            return {
                "sugerencia": "⚠️ Posibles causas:",
                "soluciones": [
                    "1. Verificar conexión a base de datos",
                    "2. Revisar si los cajeros están trabajando",
                    "3. Comprobar horario de operación",
                    "4. Verificar logs del sistema"
                ],
                "confianza": 70
            }
        elif "STOCK CRÍTICO" in titulo:
            return {
                "sugerencia": "📦 Productos con stock bajo:",
                "soluciones": [
                    "1. Revisar alerta específica para ver productos",
                    "2. Generar orden de compra",
                    "3. Verificar si hay más productos próximos a agotarse",
                    "4. Revisar tendencia de ventas de estos productos"
                ],
                "confianza": 85
            }
        
        return None
    
    def reportar_solucion(self, error, solucion_aplicada, exitosa=True):
        """Registra una solución que funcionó"""
        # Limpiar error de emojis
        for emoji in ['🔴', '⚠️', '✅', '🔵']:
            error = error.replace(emoji, '')
        error = error.strip()
        
        if error not in self.soluciones:
            self.soluciones[error] = []
        
        self.soluciones[error].append({
            "solucion": solucion_aplicada,
            "fecha": datetime.now().isoformat(),
            "exitosa": exitosa
        })
        
        self.guardar_soluciones()
        
        # Actualizar conocimiento
        for patron in self.conocimiento["patrones"]:
            if patron["error"] == error:
                patron["soluciones_posibles"] = self.soluciones[error]
                break
        
        self.guardar_conocimiento()
        print(f"✅ Solución aprendida para: {error}")

def main():
    aprendiz = AprendizAutomatico()
    
    print("🧠 APRENDIZ AUTOMÁTICO INICIADO")
    print("="*50)
    
    # Analizar patrones
    aprendiz.analizar_patrones()
    
    # Mostrar conocimiento actual
    print(f"\n📊 ESTADÍSTICAS DE APRENDIZAJE:")
    print(f"   Patrones detectados: {len(aprendiz.conocimiento['patrones'])}")
    print(f"   Soluciones aprendidas: {len(aprendiz.soluciones)}")
    
    # Mostrar patrones detectados
    if aprendiz.conocimiento['patrones']:
        print(f"\n🔍 PATRONES DETECTADOS:")
        for patron in aprendiz.conocimiento['patrones']:
            print(f"   • {patron['error']} - {patron['frecuencia']} veces")
    
    # Analizar última alerta
    if aprendiz.alertas:
        ultima = aprendiz.alertas[-1]
        print(f"\n🔍 ANALIZANDO ÚLTIMA ALERTA:")
        print(f"   {ultima['titulo']}")
        print(f"   {ultima['mensaje']}")
        
        sugerencia = aprendiz.sugerir_solucion(ultima)
        if sugerencia:
            print(f"\n💡 {sugerencia['sugerencia']} (confianza: {sugerencia['confianza']}%)")
            for sol in sugerencia['soluciones']:
                print(f"   • {sol}")
    else:
        print("\n📭 No hay alertas para analizar")
    
    print("\n✅ Análisis completado")
    print(f"Conocimiento guardado en: {CONOCIMIENTO_FILE}")

if __name__ == "__main__":
    main()
