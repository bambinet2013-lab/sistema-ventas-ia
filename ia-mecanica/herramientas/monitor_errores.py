#!/usr/bin/env python3
"""
Sistema de Monitoreo Automático de Errores
Detecta fallos en el sistema de ventas y te alerta
"""

import time
import requests
import json
from datetime import datetime, timedelta
import os
import subprocess

# Configuración
API_BD = "http://localhost:5000/consultar"
CHECK_INTERVAL = 60  # segundos (1 minuto)
LOG_FILE = "/home/junior/Escritorio/sistema-ventas-python/sistema_ventas.log"
ALERTAS_FILE = "alertas_detectadas.json"

# Cargar alertas previas para no repetir
def cargar_alertas():
    try:
        with open(ALERTAS_FILE, 'r') as f:
            return json.load(f)
    except:
        return []

def guardar_alertas(alertas):
    with open(ALERTAS_FILE, 'w') as f:
        json.dump(alertas, f, indent=2)

def enviar_alerta(titulo, mensaje, nivel="⚠️"):
    """Envía alerta a la interfaz web y terminal"""
    alerta = {
        "timestamp": datetime.now().isoformat(),
        "titulo": titulo,
        "mensaje": mensaje,
        "nivel": nivel
    }
    
    # Guardar en archivo
    alertas = cargar_alertas()
    alertas.append(alerta)
    guardar_alertas(alertas[-50:])  # Guardar últimas 50
    
    # Mostrar en terminal con colores
    colores = {
        "🔴": "\033[91m",
        "⚠️": "\033[93m",
        "✅": "\033[92m",
        "🔵": "\033[94m"
    }
    color = colores.get(nivel, "\033[0m")
    print(f"{color}{nivel} {titulo}\033[0m")
    print(f"   {mensaje}\n")

def consultar_bd(query):
    """Ejecuta consulta en la BD"""
    try:
        response = requests.post(
            API_BD,
            json={"consulta": query},
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        return response.json()
    except Exception as e:
        print(f"Error consultando BD: {e}")
        return None

def obtener_valor_int(resultado, campo, default=0):
    """Extrae un valor entero de un resultado de BD de forma segura"""
    try:
        if resultado and resultado.get('success') and resultado['resultados']:
            valor = resultado['resultados'][0].get(campo, default)
            if valor is None:
                return default
            return int(valor)
    except (ValueError, TypeError, KeyError, IndexError):
        pass
    return default

def analizar_ventas_recientes():
    """Detecta anomalías en ventas de los últimos 5 minutos"""
    try:
        hace_5min = (datetime.now() - timedelta(minutes=5)).strftime('%Y-%m-%d %H:%M:%S')
        
        query = f"""
        SELECT COUNT(*) as ventas_recientes 
        FROM venta 
        WHERE fecha_hora >= '{hace_5min}'
        """
        resultado = consultar_bd(query)
        ventas = obtener_valor_int(resultado, 'ventas_recientes', 0)
        
        if ventas == 0:
            enviar_alerta(
                "🔴 SIN VENTAS EN 5 MINUTOS",
                "No se han registrado ventas en los últimos 5 minutos. Verificar sistema.",
                "🔴"
            )
    except Exception as e:
        print(f"Error en análisis de ventas: {e}")

def analizar_pagos_fallidos():
    """Detecta pagos que quedaron incompletos"""
    try:
        query = """
        SELECT COUNT(*) as pagos_pendientes
        FROM venta_pago_detalle
        WHERE estado_pago = 'PENDIENTE'
        """
        resultado = consultar_bd(query)
        pendientes = obtener_valor_int(resultado, 'pagos_pendientes', 0)
        
        if pendientes > 0:
            enviar_alerta(
                f"⚠️ {pendientes} PAGOS PENDIENTES",
                f"Hay {pendientes} pagos sin confirmar. Revisar Pago Móvil/Transferencias.",
                "⚠️"
            )
    except Exception as e:
        print(f"Error en análisis de pagos: {e}")

def analizar_logs():
    """Lee el archivo de logs en busca de errores recientes"""
    try:
        with open(LOG_FILE, 'r') as f:
            lineas = f.readlines()[-100:]  # Últimas 100 líneas
        
        errores = []
        for linea in lineas:
            if "ERROR" in linea or "❌" in linea or "Exception" in linea:
                errores.append(linea.strip())
        
        if errores:
            enviar_alerta(
                f"🔴 {len(errores)} ERRORES EN LOGS",
                f"Último error: {errores[-1][:200]}",
                "🔴"
            )
    except Exception as e:
        print(f"Error leyendo logs: {e}")

def analizar_stock_critico():
    """Detecta productos con stock peligrosamente bajo"""
    try:
        query = """
        SELECT a.nombre, SUM(k.cantidad) as stock
        FROM articulo a
        JOIN kardex k ON a.idarticulo = k.idarticulo
        GROUP BY a.nombre
        HAVING SUM(k.cantidad) < 3
        """
        resultado = consultar_bd(query)
        
        if resultado and resultado.get('success') and resultado['resultados']:
            productos = resultado['resultados']
            num_productos = len(productos)
            
            if num_productos > 0:
                nombres = [p['nombre'][:20] for p in productos[:3]]
                enviar_alerta(
                    f"⚠️ {num_productos} PRODUCTOS CON STOCK CRÍTICO",
                    f"Productos con stock < 3: {', '.join(nombres)}...",
                    "⚠️"
                )
    except Exception as e:
        print(f"Error en análisis de stock: {e}")

def mostrar_dashboard():
    """Muestra resumen en terminal"""
    os.system('clear' if os.name == 'posix' else 'cls')
    print("="*60)
    print("🤖 MECÁNICO DE VENTAS - MONITOREO EN VIVO")
    print("="*60)
    print(f"Última verificación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Intervalo: {CHECK_INTERVAL} segundos")
    print("-"*60)
    
    # Mostrar últimas alertas
    alertas = cargar_alertas()
    if alertas:
        print("\n📋 ÚLTIMAS ALERTAS:")
        for alerta in alertas[-5:]:
            print(f"{alerta['nivel']} {alerta['titulo']}")
            print(f"   {alerta['mensaje'][:80]}...")
    else:
        print("\n✅ Todo funcionando correctamente - Sin alertas")

def main():
    print("🚀 Iniciando monitor de errores...")
    print(f"Intervalo de verificación: {CHECK_INTERVAL} segundos")
    
    while True:
        try:
            mostrar_dashboard()
            
            # Ejecutar todos los análisis
            analizar_ventas_recientes()
            analizar_pagos_fallidos()
            analizar_logs()
            analizar_stock_critico()
            
            time.sleep(CHECK_INTERVAL)
            
        except KeyboardInterrupt:
            print("\n\n👋 Monitor detenido")
            break
        except Exception as e:
            print(f"Error general en monitor: {e}")
            time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
