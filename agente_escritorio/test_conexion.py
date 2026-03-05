#!/usr/bin/env python3
"""
Prueba rápida de conexión
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from core.database import Database
from loguru import logger

def test():
    logger.info("🧪 Probando conexión a BD...")
    db = Database()
    conn = db.get_connection()
    
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT DB_NAME()")
        db_name = cursor.fetchone()[0]
        logger.success(f"✅ Conectado a base de datos: {db_name}")
        
        # Contar usuarios (ajusta el nombre de la tabla si es diferente)
        try:
            cursor.execute("SELECT COUNT(*) FROM usuario")
            count = cursor.fetchone()[0]
            logger.info(f"📊 Usuarios en sistema: {count}")
        except:
            try:
                cursor.execute("SELECT COUNT(*) FROM trabajador")
                count = cursor.fetchone()[0]
                logger.info(f"📊 Trabajadores en sistema: {count}")
            except:
                logger.info("📊 No se pudo contar usuarios")
        
        db.close()
        return True
    else:
        logger.error("❌ No se pudo conectar")
        return False

if __name__ == "__main__":
    test()
