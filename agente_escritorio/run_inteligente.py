#!/usr/bin/env python3
"""
Punto de entrada con logs detallados
"""
import sys
from pathlib import Path

# Agregar paths
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

# Configurar logging
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

from loguru import logger
import sys

# Configurar loguru para mostrar todo
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan> - <level>{message}</level>",
    level="DEBUG",
    colorize=True
)

from ui.main_window_inteligente import MainWindowInteligente

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🚀 INICIANDO SISTEMA DE VENTAS INTELIGENTE")
    print("="*60 + "\n")
    
    try:
        app = MainWindowInteligente()
        print("✅ Ventana principal creada")
        app.run()
    except Exception as e:
        print(f"❌ Error fatal: {e}")
        import traceback
        traceback.print_exc()
        input("\nPresione Enter para salir...")
