"""
Conexión a base de datos usando el sistema existente
"""
import sys
from pathlib import Path
from loguru import logger

# Agregar el directorio principal al path
sys.path.append(str(Path(__file__).parent.parent.parent))

from capa_datos.conexion import ConexionDB
from core.config import Config

class Database:
    """Wrapper de tu conexión existente"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Inicializa usando tu ConexionDB"""
        try:
            self.conexion = ConexionDB()
            self.conn = self.conexion.conectar()
            logger.success("✅ Agente conectado a BD usando tu sistema")
        except Exception as e:
            logger.error(f"❌ Error conectando a BD: {e}")
            self.conn = None
    
    def get_connection(self):
        """Retorna la conexión activa"""
        return self.conn
    
    def close(self):
        """Cierra la conexión"""
        if self.conn:
            self.conexion.cerrar()
            logger.info("🔒 Conexión cerrada")
