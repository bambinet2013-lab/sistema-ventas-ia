"""
Agente de Cashea configurable
Lee credenciales de la base de datos
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

import json
import requests
from loguru import logger
import pyodbc

class CasheaAgent:
    """Agente para integrar Cashea en el sistema de ventas"""
    
    def __init__(self):
        self.config = self._cargar_configuracion()
        self.activo = self.config.get('activo', False) if self.config else False
        
    def _get_connection(self):
        """Obtiene conexión a la base de datos"""
        conn_str = (
            "DRIVER={ODBC Driver 18 for SQL Server};"
            "SERVER=localhost,1433;"
            "DATABASE=SistemaVentas;"
            "UID=sa;"
            "PWD=Santi07.;"
            "TrustServerCertificate=yes;"
        )
        return pyodbc.connect(conn_str)
    
    def _cargar_configuracion(self):
        """Lee la configuración de Cashea desde la BD"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT configuracion_json FROM configuracion_medios_pago 
                WHERE medio_pago = 'CASHEA'
            """)
            row = cursor.fetchone()
            conn.close()
            
            if row and row[0]:
                config = json.loads(row[0])
                logger.info(f"✅ Configuración de Cashea cargada")
                return config
            else:
                logger.warning("⚠️ No hay configuración de Cashea")
                return None
        except Exception as e:
            logger.error(f"❌ Error cargando configuración: {e}")
            return None
    
    def esta_activo(self):
        """Retorna True si Cashea está activo y configurado"""
        return self.activo
    
    def probar_conexion(self, public_key, private_key, store_id):
        """
        Prueba las credenciales contra la API de Cashea
        (versión estática para usar desde la UI)
        """
        # Simular prueba (luego se conectará a API real)
        logger.info("🧪 Probando conexión con Cashea")
        return True, "Conexión exitosa"
    
    def solicitar_autorizacion(self, monto_total, id_cliente=None):
        """
        Solicita autorización a la API de Cashea para una venta
        
        Args:
            monto_total: Monto total de la venta en USD
            id_cliente: ID del cliente (opcional)
            
        Returns:
            dict: Resultado de la autorización
        """
        if not self.activo:
            return {
                'success': False,
                'error': 'Cashea no está activo'
            }
        
        # Verificar monto mínimo
        monto_minimo = self.config.get('monto_minimo', 25.0)
        if monto_total < monto_minimo:
            return {
                'success': False,
                'error': f'El monto mínimo para Cashea es ${monto_minimo}'
            }
        
        # Aquí irá la llamada real a la API de Cashea
        # Por ahora simulamos una respuesta exitosa
        logger.info(f"📤 Solicitando autorización para ${monto_total}")
        
        # Simular cálculo de inicial (40% por defecto)
        porcentaje_inicial = 40
        inicial = round(monto_total * porcentaje_inicial / 100, 2)
        
        return {
            'success': True,
            'autorizado': True,
            'monto_total': monto_total,
            'inicial': inicial,
            'porcentaje_inicial': porcentaje_inicial,
            'cuotas': 3,
            'referencia': f"CASHEA-{id_cliente}-{monto_total}",
            'mensaje': 'Autorización exitosa'
        }
    
    def obtener_info(self):
        """Retorna información resumida de la configuración"""
        if not self.config:
            return {'activo': False}
        
        return {
            'activo': self.activo,
            'store_id': self.config.get('store_id', ''),
            'comision': self.config.get('comision', 3.0),
            'monto_minimo': self.config.get('monto_minimo', 25.0)
        }
