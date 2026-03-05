#!/usr/bin/env python3
"""
Prueba de los agentes creados - Versión con conexión propia
"""
import sys
from pathlib import Path

# Agregar el directorio del agente al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from loguru import logger
from agents.cliente_agent import ClienteAgent
from capa_negocio.articulo_service import ArticuloService
from capa_datos.articulo_repo import ArticuloRepositorio
import pyodbc

def test_clientes():
    """Prueba el agente de clientes"""
    logger.info("🧪 Probando ClienteAgent...")
    
    agent = ClienteAgent()
    
    try:
        cliente = agent.buscar_por_documento("V12345678")
        if cliente:
            logger.success(f"✅ Cliente encontrado: {cliente.get('nombre')} {cliente.get('apellidos')}")
        else:
            logger.info("ℹ️ Cliente no encontrado (es normal si no existe)")
        
        cf_id = agent.obtener_consumidor_final()
        logger.info(f"👤 Consumidor Final ID: {cf_id}")
        
    finally:
        agent.cerrar()
        logger.info("🔒 Conexión de clientes cerrada")

def test_articulos_directo():
    """
    Prueba artículos con conexión propia
    """
    logger.info("🧪 Probando artículos con conexión propia...")
    
    # Crear conexión propia
    conn_str = (
        "DRIVER={ODBC Driver 18 for SQL Server};"
        "SERVER=localhost,1433;"
        "DATABASE=SistemaVentas;"
        "UID=sa;"
        "PWD=Santi07.;"
        "TrustServerCertificate=yes;"
    )
    
    conn = None
    try:
        conn = pyodbc.connect(conn_str)
        logger.success("✅ Conexión propia exitosa")
        
        repo = ArticuloRepositorio(conn)
        service = ArticuloService(repo)
        
        articulos = service.listar_articulos()
        logger.info(f"📦 Total artículos: {len(articulos)}")
        
        if len(articulos) > 0:
            primero = articulos[0]
            logger.info(f"📦 Primer artículo: {primero.get('nombre')}")
            logger.info(f"   Precio: {primero.get('precio_venta')}")
            logger.info(f"   Impuesto: {primero.get('id_impuesto')}")
            
    except Exception as e:
        logger.error(f"❌ Error: {e}")
    finally:
        if conn:
            conn.close()
            logger.info("🔒 Conexión de artículos cerrada")

if __name__ == "__main__":
    logger.info("🚀 Iniciando pruebas")
    test_clientes()
    test_articulos_directo()
    logger.success("✅ Pruebas completadas")
