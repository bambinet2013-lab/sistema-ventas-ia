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
from datetime import datetime

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
        
        # Calcular inicial según nivel del cliente
        # Por ahora usamos 40% fijo (Nivel 3)
        porcentaje_inicial = 40
        inicial = round(monto_total * porcentaje_inicial / 100, 2)
        resto = round(monto_total - inicial, 2)
        cuotas = 3  # 3 cuotas quincenales
        
        # Simular respuesta exitosa
        return {
            'success': True,
            'autorizado': True,
            'monto_total': monto_total,
            'inicial': inicial,
            'resto': resto,
            'porcentaje_inicial': porcentaje_inicial,
            'cuotas': cuotas,
            'referencia': f"CASHEA-{datetime.now().strftime('%y%m%d%H%M%S')}",
            'mensaje': f'Aprobado: Paga ${inicial} hoy y {cuotas} cuotas de ${round(resto/cuotas, 2)}'
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
        
    def crear_endpoint_notificacion(self):
        """
        Crea el endpoint para recibir notificaciones de Cashea
        Esto sería parte de una API futura, por ahora simulamos
        """
        # En una implementación real, esto sería un servidor web
        # con FastAPI o Flask. Por ahora guardaremos en un archivo
        self.notificaciones_pendientes = []
        
    def recibir_notificacion(self, datos):
        """
        Simula la llegada de una notificación de Cashea
        """
        from datetime import datetime
        
        notificacion = {
            'fecha': datetime.now().strftime('%d/%m/%Y %H:%M'),
            'referencia': datos.get('referencia', 'N/A'),
            'monto_total': datos.get('monto_total', 0),
            'inicial': datos.get('inicial', 0),
            'cuotas': datos.get('cuotas', 0),
            'cliente': datos.get('cliente', 'Cliente Cashea'),
            'leida': False
        }
        
        self.notificaciones_pendientes.append(notificacion)
        return {'success': True, 'mensaje': 'Notificación recibida'}
    
    def obtener_notificaciones_pendientes(self):
        """Retorna las notificaciones no leídas"""
        if not hasattr(self, 'notificaciones_pendientes'):
            return []
        return [n for n in self.notificaciones_pendientes if not n.get('leida', False)]
    
    def consultar_notificaciones_api(self):
        """
        Consulta las notificaciones pendientes desde la API webhook
        """
        import requests
        try:
            response = requests.get("http://localhost:8000/notificaciones/pendientes", timeout=2)
            if response.status_code == 200:
                data = response.json()
                return data.get('notificaciones', [])
        except:
            # Si no hay servidor, usar simulación local
            pass
        return self.obtener_notificaciones_pendientes() if hasattr(self, 'obtener_notificaciones_pendientes') else []    
    
    def marcar_como_leida(self, referencia):
        """Marca una notificación como leída"""
        if hasattr(self, 'notificaciones_pendientes'):
            for n in self.notificaciones_pendientes:
                if n['referencia'] == referencia:
                    n['leida'] = True
                    return True
        return False        
        
        
