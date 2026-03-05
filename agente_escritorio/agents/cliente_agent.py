"""
Agente de Clientes - Solo con Consumidor Final
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from loguru import logger
import pyodbc

class ClienteAgent:
    def __init__(self):
        logger.info("✅ ClienteAgent inicializado")
    
    def _get_connection(self):
        conn_str = (
            "DRIVER={ODBC Driver 18 for SQL Server};"
            "SERVER=localhost,1433;"
            "DATABASE=SistemaVentas;"
            "UID=sa;"
            "PWD=Santi07.;"
            "TrustServerCertificate=yes;"
        )
        return pyodbc.connect(conn_str)
    
    def obtener_consumidor_final(self):
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Buscar CF
            cursor.execute("SELECT idcliente FROM cliente WHERE tipo_documento = 'CF'")
            row = cursor.fetchone()
            
            if row:
                conn.close()
                return row[0]
            
            # Crear CF
            cursor.execute("""
                INSERT INTO cliente (nombre, apellidos, tipo_documento, num_documento)
                OUTPUT INSERTED.idcliente
                VALUES ('CONSUMIDOR', 'FINAL', 'CF', '')
            """)
            row = cursor.fetchone()
            conn.commit()
            conn.close()
            return row[0] if row else None
            
        except Exception as e:
            logger.error(f"❌ Error: {e}")
            return None
    
    def cerrar(self):
        pass
