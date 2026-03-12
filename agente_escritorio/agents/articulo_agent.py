
# Funciones de reparación automática - Agregadas por SupremeBot
def safe_get(obj, attr, default=None):
    """Obtiene atributo de forma segura sin NoneType errors"""
    try:
        return getattr(obj, attr) if obj is not None else default
    except:
        return default

def safe_dict_get(d, key, default=None):
    """Obtiene valor de diccionario de forma segura"""
    try:
        return d.get(key, default) if d is not None else default
    except:
        return default

"""
Agente de Artículos - Versión corregida con stock visible
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from loguru import logger
from capa_negocio.articulo_service import ArticuloService
from capa_datos.articulo_repo import ArticuloRepositorio
import pyodbc

class ArticuloAgent:
    def __init__(self):
        logger.info("✅ ArticuloAgent inicializado")
    
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
    
    def _get_service(self):
        conn = self._get_connection()
        repo = ArticuloRepositorio(conn)
        service = ArticuloService(repo)
        return service, conn
    
    def buscar_por_nombre(self, nombre):
        """Busca artículos por nombre y devuelve con stock actual"""
        try:
            if not nombre or len(nombre) < 2:
                return []
            
            logger.info(f"🔍 Buscando: '{nombre}'")
            
            service, conn = self._get_service()
            resultados = service.buscar_por_nombre(nombre)
            
            logger.info(f"📦 {len(resultados)} artículos encontrados en BD")
            
            # Agregar stock a cada artículo
            cursor = conn.cursor()
            for art in resultados:
                try:
                    cursor.execute("""
                        SELECT TOP 1 stock_nuevo FROM kardex 
                        WHERE idarticulo = ? 
                        ORDER BY fecha_movimiento DESC
                    """, (art['idarticulo'],))
                    row = cursor.fetchone()
                    art['stock_actual'] = row[0] if row else 0
                    logger.info(f"  → {art['nombre']}: stock {art['stock_actual']}")
                except:
                    art['stock_actual'] = 0
            
            conn.close()
            return resultados
            
        except Exception as e:
            logger.error(f"❌ Error: {e}")
            return []
    
    def buscar_por_codigo(self, codigo):
        """Busca artículo por código"""
        try:
            if not codigo:
                return None
            
            service, conn = self._get_service()
            articulo = service.buscar_por_codigo(codigo)
            
            if articulo:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT TOP 1 stock_nuevo FROM kardex 
                    WHERE idarticulo = ? 
                    ORDER BY fecha_movimiento DESC
                """, (articulo['idarticulo'],))
                row = cursor.fetchone()
                articulo['stock_actual'] = row[0] if row else 0
                logger.info(f"✅ Encontrado: {articulo['nombre']} (stock: {articulo['stock_actual']})")
            
            conn.close()
            return articulo
            
        except Exception as e:
            logger.error(f"❌ Error: {e}")
            return None
    
    def cerrar(self):
        pass
