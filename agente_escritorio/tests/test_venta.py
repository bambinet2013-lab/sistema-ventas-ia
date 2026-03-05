#!/usr/bin/env python3
"""
Prueba del Agente de Ventas
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from loguru import logger
from agents.venta_agent import VentaAgent

class UsuarioPrueba:
    def __init__(self):
        self.id = 1
        self.idtrabajador = 1
        self.nombre = "Admin Prueba"
        self.rol = "Administrador"

def test_venta():
    logger.info("🧪 Probando VentaAgent...")
    
    usuario = UsuarioPrueba()
    venta = VentaAgent(usuario)
    
    # Iniciar venta como consumidor final
    venta.iniciar_venta(es_consumidor_final=True)
    
    # Buscar y agregar producto
    producto = venta.buscar_producto("QUESO COLOMBIANO")
    if producto:
        venta.agregar_producto(producto, 2)
    
    # Calcular totales
    totales = venta.calcular_totales()
    logger.info(f"💰 Totales: ${totales['total_usd']:.2f} (Bs. {totales['total_bs']:.2f})")
    
    # Procesar venta (comentado para no crear ventas reales en prueba)
    # resultado = venta.procesar_venta()
    # logger.info(f"📦 Resultado: {resultado}")
    
    venta.cerrar()
    logger.success("✅ Prueba completada")

if __name__ == "__main__":
    test_venta()
