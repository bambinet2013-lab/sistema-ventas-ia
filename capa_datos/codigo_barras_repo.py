"""
Repositorio para análisis de códigos de barras
Basado en estándares GS1 [citation:6][citation:7]
"""
from loguru import logger
from typing import Optional, Dict

class CodigoBarrasRepositorio:
    """Repositorio para analizar prefijos de códigos de barras"""
    
    def __init__(self, conn=None):
        """
        Inicializa el repositorio de códigos de barras
        """
        if conn is not None:
            self.conn = conn
        else:
            try:
                from capa_datos.conexion import ConexionDB
                self.conn = ConexionDB().conectar()
                logger.info("✅ Conexión propia creada para CodigoBarrasRepositorio")
            except Exception as e:
                logger.error(f"❌ Error creando conexión: {e}")
                raise
        
        logger.info("✅ CodigoBarrasRepositorio inicializado")
    
    def analizar_codigo(self, codigo: str) -> Optional[Dict]:
        """
        Analiza un código de barras y extrae información del país de origen
        
        Args:
            codigo: Código de barras completo (ej: '7591234567890')
            
        Returns:
            Diccionario con información del país o None si no se reconoce
        """
        if not codigo or not isinstance(codigo, str):
            return None
        
        try:
            # Limpiar código (quitar espacios, guiones)
            codigo_limpio = ''.join(c for c in codigo if c.isdigit())
            
            if len(codigo_limpio) < 3:
                return None
            
            cursor = self.conn.cursor()
            
            # Buscar por prefijo (de mayor a menor longitud)
            # Probamos con prefijos de 3 dígitos primero, luego 2
            prefijos_a_probar = [
                codigo_limpio[:3],  # 3 dígitos
                codigo_limpio[:2]   # 2 dígitos
            ]
            
            for prefijo in prefijos_a_probar:
                query = """
                SELECT prefijo, pais, continente, idcategoria_sugerida, id_impuesto_sugerido
                FROM prefijos_codigo_barras
                WHERE prefijo = ? AND activo = 1
                """
                cursor.execute(query, (prefijo,))
                row = cursor.fetchone()
                
                if row:
                    resultado = {
                        'prefijo': row[0],
                        'pais': row[1],
                        'continente': row[2],
                        'idcategoria_sugerida': row[3],
                        'id_impuesto_sugerido': row[4],
                        'confianza': 0.85  # Confianza base por código de barras
                    }
                    
                    logger.info(f"🌍 Código {codigo} detectado: País {row[1]} (prefijo {row[0]})")
                    return resultado
            
            logger.debug(f"❓ Prefijo no reconocido para código: {codigo}")
            return None
            
        except Exception as e:
            logger.error(f"❌ Error analizando código {codigo}: {e}")
            return None
    
    def sugerir_categoria_por_pais(self, codigo: str, nombre_producto: str) -> Optional[Dict]:
        """
        Sugiere categoría basada en país de origen + nombre del producto
        
        Args:
            codigo: Código de barras
            nombre_producto: Nombre del producto para contexto adicional
            
        Returns:
            Sugerencia de categoría/impuesto o None
        """
        info_pais = self.analizar_codigo(codigo)
        if not info_pais:
            return None
        
        # Si el país tiene categoría sugerida predefinida, usarla
        if info_pais['idcategoria_sugerida']:
            return {
                'idcategoria': info_pais['idcategoria_sugerida'],
                'id_impuesto': info_pais['id_impuesto_sugerido'] or 2,  # General por defecto
                'confianza': 0.80,
                'metodo': 'codigo_barras_pais',
                'pais': info_pais['pais'],
                'prefijo': info_pais['prefijo']
            }
        
        # Si no hay categoría predefinida, podemos inferir por tipo de producto + país
        nombre_upper = nombre_producto.upper()
        
        # Reglas simples basadas en país + tipo de producto
        if info_pais['pais'] == 'Venezuela' and any(p in nombre_upper for p in ['HARINA', 'MAIZ', 'PAN']):
            return {
                'idcategoria': 2,  # Víveres
                'id_impuesto': 1,   # Exento (productos básicos venezolanos)
                'confianza': 0.75,
                'metodo': 'codigo_barras_pais_tipo',
                'pais': info_pais['pais']
            }
        
        if info_pais['pais'] == 'Colombia' and any(p in nombre_upper for p in ['CAFE', 'CAFÉ']):
            return {
                'idcategoria': 2,
                'id_impuesto': 1,
                'confianza': 0.75,
                'metodo': 'codigo_barras_pais_tipo',
                'pais': info_pais['pais']
            }
        
        # Por defecto, productos importados (no venezolanos) tienden a ser generales
        if info_pais['pais'] != 'Venezuela':
            return {
                'idcategoria': None,  # Sin categoría específica
                'id_impuesto': 2,      # General (importados)
                'confianza': 0.60,
                'metodo': 'codigo_barras_importado',
                'pais': info_pais['pais'],
                'nota': 'Producto importado - verificar categoría'
            }
        
        return None

    def obtener_estadisticas_paises(self) -> Dict:
        """Obtiene estadísticas de prefijos por país"""
        try:
            cursor = self.conn.cursor()
            
            query = """
            SELECT pais, continente, COUNT(*) as total_prefijos
            FROM prefijos_codigo_barras
            WHERE activo = 1
            GROUP BY pais, continente
            ORDER BY total_prefijos DESC
            """
            
            cursor.execute(query)
            columns = [column[0] for column in cursor.description]
            rows = cursor.fetchall()
            
            return {
                'total_paises': len(rows),
                'total_prefijos': sum(row[2] for row in rows),
                'detalle': [dict(zip(columns, row)) for row in rows]
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {e}")
            return {}
