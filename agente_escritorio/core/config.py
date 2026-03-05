"""
Configuración central del agente de escritorio
"""
import os
from dotenv import load_dotenv
from pathlib import Path

# Cargar variables de entorno del proyecto principal
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

class Config:
    # Base de datos (usa las mismas credenciales)
    DB_SERVER = os.getenv('DB_SERVER', 'localhost,1433')
    DB_NAME = os.getenv('DB_NAME', 'SistemaVentas')
    DB_USER = os.getenv('DB_USER', 'sa')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'Santi07.')
    DB_DRIVER = os.getenv('DB_DRIVER', '{ODBC Driver 18 for SQL Server}')
    
    # Rutas
    BASE_DIR = Path(__file__).parent.parent
    LOGS_DIR = BASE_DIR / 'logs'
    REPORTS_DIR = BASE_DIR / 'reports'
    
    # Atajos de teclado
    TECLA_CF = 'F8'      # Consumidor Final
    TECLA_BUSCAR = 'F9'   # Búsqueda rápida
    TECLA_PAGAR = 'F10'   # Procesar pago
    
    @classmethod
    def get_db_connection_string(cls):
        """Retorna string de conexión a BD"""
        return (
            f"DRIVER={cls.DB_DRIVER};"
            f"SERVER={cls.DB_SERVER};"
            f"DATABASE={cls.DB_NAME};"
            f"UID={cls.DB_USER};"
            f"PWD={cls.DB_PASSWORD};"
            f"TrustServerCertificate=yes;"
        )
    
    @classmethod
    def ensure_dirs(cls):
        """Crea directorios necesarios"""
        cls.LOGS_DIR.mkdir(exist_ok=True)
        cls.REPORTS_DIR.mkdir(exist_ok=True)
