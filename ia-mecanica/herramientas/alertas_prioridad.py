#!/usr/bin/env python3
"""
🚨 SISTEMA DE ALERTAS CON PRIORIDAD DINÁMICA
Asigna prioridad automática basada en múltiples factores
Sistema usado en operaciones críticas
"""

import json
from datetime import datetime, timedelta
import numpy as np

class SistemaAlertasPrioridad:
    def __init__(self):
        self.alertas_file = "alertas_detectadas.json"
        self.prioridades_file = "alertas_priorizadas.json"
        self.alertas = self.cargar_alertas()
        
    def cargar_alertas(self):
        try:
            with open(self.alertas_file, 'r') as f:
                return json.load(f)
        except:
            return []
    
    def guardar_prioridades(self, prioridades):
        with open(self.prioridades_file, 'w') as f:
            json.dump(prioridades, f, indent=2)
    
    def calcular_prioridad(self, alerta):
        """Calcula prioridad basada en múltiples factores"""
        puntuacion = 0
        factores = []
        
        # Factor 1: Nivel base
        if '🔴' in alerta['titulo']:
            puntuacion += 40
            factores.append("🔴 Nivel crítico (+40)")
        elif '⚠️' in alerta['titulo']:
            puntuacion += 20
            factores.append("⚠️ Nivel advertencia (+20)")
        
        # Factor 2: Antigüedad (más reciente = más prioridad)
        try:
            timestamp = datetime.fromisoformat(alerta['timestamp'])
            horas_antiguedad = (datetime.now() - timestamp).total_seconds() / 3600
            
            if horas_antiguedad < 1:
                puntuacion += 30
                factores.append(f"⏱️ Muy reciente (<1h) (+30)")
            elif horas_antiguedad < 6:
                puntuacion += 15
                factores.append(f"⏱️ Reciente (<6h) (+15)")
        except:
            pass
        
        # Factor 3: Frecuencia del mismo tipo
        mismo_tipo = [a for a in self.alertas[-20:] 
                     if a['titulo'] == alerta['titulo']]
        if len(mismo_tipo) > 3:
            puntuacion += min(len(mismo_tipo) * 2, 20)
            factores.append(f"🔄 Alta frecuencia ({len(mismo_tipo)} en últimas) (+{min(len(mismo_tipo)*2,20)})")
        
        # Factor 4: Contenido específico (palabras clave)
        mensaje = alerta['mensaje'].lower()
        if 'stock' in mensaje and '0' in mensaje:
            puntuacion += 25
            factores.append("📦 Stock agotado (+25)")
        elif 'pago' in mensaje and 'pendiente' in mensaje:
            puntuacion += 15
            factores.append("💰 Pagos pendientes (+15)")
        
        return {
            'puntuacion': min(puntuacion, 100),  # Máximo 100
            'factores': factores
        }
    
    def priorizar_alertas(self):
        """Prioriza todas las alertas activas"""
        alertas_activas = self.alertas[-20:]  # Últimas 20 alertas
        
        priorizadas = []
        for alerta in alertas_activas:
            calculo = self.calcular_prioridad(alerta)
            
            priorizadas.append({
                'timestamp': alerta['timestamp'],
                'titulo': alerta['titulo'],
                'mensaje': alerta['mensaje'],
                'prioridad': calculo['puntuacion'],
                'factores': calculo['factores'],
                'nivel_emergencia': '🔴 CRÍTICA' if calculo['puntuacion'] > 70 else
                                   '🟡 ALTA' if calculo['puntuacion'] > 40 else
                                   '🔵 NORMAL' if calculo['puntuacion'] > 20 else
                                   '⚪ BAJA'
            })
        
        # Ordenar por prioridad (mayor primero)
        priorizadas.sort(key=lambda x: x['prioridad'], reverse=True)
        
        self.guardar_prioridades(priorizadas)
        return priorizadas
    
    def mostrar_dashboard(self):
        """Muestra dashboard de alertas priorizadas"""
        priorizadas = self.priorizar_alertas()
        
        print("\n" + "="*80)
        print("🚨 DASHBOARD DE ALERTAS CON PRIORIDAD DINÁMICA")
        print("="*80)
        
        print(f"\n📊 Total alertas analizadas: {len(priorizadas)}")
        print("-"*80)
        
        for i, alerta in enumerate(priorizadas, 1):
            print(f"\n{i:2}. {alerta['nivel_emergencia']} - {alerta['titulo']}")
            print(f"    📍 {alerta['mensaje'][:100]}...")
            print(f"    🎯 Prioridad: {alerta['prioridad']:.0f}/100")
            print(f"    📋 Factores:")
            for factor in alerta['factores'][:3]:  # Top 3 factores
                print(f"       • {factor}")
        
        # Resumen estadístico
        criticas = sum(1 for a in priorizadas if a['nivel_emergencia'] == '🔴 CRÍTICA')
        altas = sum(1 for a in priorizadas if a['nivel_emergencia'] == '🟡 ALTA')
        normales = sum(1 for a in priorizadas if a['nivel_emergencia'] == '🔵 NORMAL')
        bajas = sum(1 for a in priorizadas if a['nivel_emergencia'] == '⚪ BAJA')
        
        print("\n" + "="*80)
        print("📈 RESUMEN DE EMERGENCIAS:")
        print(f"   🔴 Críticas: {criticas}")
        print(f"   🟡 Altas: {altas}")
        print(f"   🔵 Normales: {normales}")
        print(f"   ⚪ Bajas: {bajas}")
        print("="*80)

def main():
    sistema = SistemaAlertasPrioridad()
    
    print("🚨 SISTEMA DE ALERTAS INTELIGENTES")
    print("="*80)
    
    while True:
        print("\nOpciones:")
        print("1. Ver dashboard de prioridades")
        print("2. Simular alerta de prueba")
        print("3. Salir")
        
        opcion = input("\nSelecciona: ").strip()
        
        if opcion == '1':
            sistema.mostrar_dashboard()
        elif opcion == '2':
            # Simular alerta de prueba
            alerta_prueba = {
                'timestamp': datetime.now().isoformat(),
                'titulo': '🔴 FALLO CRÍTICO EN PAGOS',
                'mensaje': '3 pagos consecutivos fallidos en los últimos 2 minutos',
                'nivel': '🔴'
            }
            sistema.alertas.append(alerta_prueba)
            sistema.guardar_prioridades(sistema.priorizar_alertas())
            print("✅ Alerta de prueba agregada")
        elif opcion == '3':
            break

if __name__ == "__main__":
    main()
