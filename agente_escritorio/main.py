#!/usr/bin/env python3
"""
Punto de entrada del Agente de Escritorio
"""
import sys
from pathlib import Path

# Agregar el directorio del agente al path
sys.path.insert(0, str(Path(__file__).parent))

from loguru import logger
from core.database import Database
from core.config import Config
from agents.cliente_agent import ClienteAgent
from agents.articulo_agent import ArticuloAgent

def main():
    """Inicia el agente"""
    logger.info("🚀 Iniciando Agente de Escritorio")
    
    # Crear directorios necesarios
    Config.ensure_dirs()
    
    # Probar conexión
    db = Database()
    if not db.get_connection():
        logger.error("❌ No se pudo conectar a la BD")
        input("Presione Enter para salir...")
        return
    
    logger.success("✅ Sistema listo")
    
    # Probar agentes
    logger.info("📦 Inicializando agentes...")
    
    cliente_agent = ClienteAgent()
    articulo_agent = ArticuloAgent()
    
    logger.info("✅ Agentes listos")
    logger.info(f"👤 Consumidor Final ID: {cliente_agent.obtener_consumidor_final()}")
    
    articulos = articulo_agent.listar_articulos()
    logger.info(f"📦 Artículos en sistema: {len(articulos)}")
    
    input("\nPresione Enter para salir...")
    
    # Cerrar recursos
    cliente_agent.cerrar()
    articulo_agent.cerrar()
    db.close()

if __name__ == "__main__":
    main()
