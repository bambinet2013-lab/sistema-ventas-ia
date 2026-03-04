"""
Repositorio para gestión de familias de palabras
"""
from loguru import logger
from typing import List, Dict, Optional

class FamiliaRepositorio:
    """Repositorio para administrar familias de palabras"""
    
    def __init__(self, conn=None):
        """
        Inicializa el repositorio de familias
        Si no se proporciona conexión, crea una nueva
        """
        if conn is not None:
            self.conn = conn
        else:
            try:
                from capa_datos.conexion import ConexionDB
                self.conn = ConexionDB().conectar()
                logger.info("✅ Conexión propia creada para FamiliaRepositorio")
            except Exception as e:
                logger.error(f"❌ Error creando conexión: {e}")
                raise
        
        logger.info("✅ FamiliaRepositorio inicializado")
    
    def crear_familia(self, nombre: str, descripcion: str = None) -> Optional[int]:
        """
        Crea una nueva familia de palabras
        
        Args:
            nombre: Nombre de la familia (ej: 'LACTEOS')
            descripcion: Descripción opcional
            
        Returns:
            ID de la familia creada o None si error
        """
        try:
            cursor = self.conn.cursor()
            
            # Verificar si ya existe
            cursor.execute("SELECT idfamilia FROM familias_palabras WHERE nombre_familia = ?", (nombre.upper(),))
            existente = cursor.fetchone()
            
            if existente:
                logger.warning(f"⚠️ La familia '{nombre}' ya existe")
                return existente[0]
            
            # Insertar nueva familia
            query = """
            INSERT INTO familias_palabras (nombre_familia, descripcion)
            OUTPUT INSERTED.idfamilia
            VALUES (?, ?)
            """
            cursor.execute(query, (nombre.upper(), descripcion))
            idfamilia = cursor.fetchone()[0]
            
            self.conn.commit()
            logger.info(f"✅ Familia '{nombre}' creada con ID {idfamilia}")
            return idfamilia
            
        except Exception as e:
            logger.error(f"❌ Error creando familia: {e}")
            self.conn.rollback()
            return None
    
    def asignar_palabra_a_familia(self, idpalabra: int, idfamilia: int) -> bool:
        """
        Asigna una palabra aprendida a una familia
        
        Args:
            idpalabra: ID de la palabra en aprendizaje_palabras
            idfamilia: ID de la familia
            
        Returns:
            True si se asignó correctamente
        """
        try:
            cursor = self.conn.cursor()
            
            query = """
            INSERT INTO palabras_familia (idpalabra, idfamilia)
            VALUES (?, ?)
            """
            cursor.execute(query, (idpalabra, idfamilia))
            
            self.conn.commit()
            logger.info(f"✅ Palabra {idpalabra} asignada a familia {idfamilia}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error asignando palabra a familia: {e}")
            self.conn.rollback()
            return False
    
    def obtener_familia_de_palabra(self, palabra: str) -> Optional[Dict]:
        """
        Obtiene la familia de una palabra específica
        
        Args:
            palabra: La palabra a buscar
            
        Returns:
            Diccionario con info de la familia o None
        """
        try:
            cursor = self.conn.cursor()
            
            query = """
            SELECT f.idfamilia, f.nombre_familia, f.descripcion,
                   ap.idpalabra, ap.palabra, ap.idcategoria, ap.id_impuesto
            FROM aprendizaje_palabras ap
            INNER JOIN palabras_familia pf ON ap.idpalabra = pf.idpalabra
            INNER JOIN familias_palabras f ON pf.idfamilia = f.idfamilia
            WHERE ap.palabra = ? AND ap.activa = 1
            """
            cursor.execute(query, (palabra,))
            
            row = cursor.fetchone()
            if row:
                return {
                    'idfamilia': row[0],
                    'nombre_familia': row[1],
                    'descripcion': row[2],
                    'idpalabra': row[3],
                    'palabra': row[4],
                    'idcategoria': row[5],
                    'id_impuesto': row[6]
                }
            return None
            
        except Exception as e:
            logger.error(f"Error obteniendo familia de '{palabra}': {e}")
            return None
    
    def buscar_por_familia(self, texto: str, limite: int = 5) -> List[Dict]:
        """
        Busca palabras que pertenezcan a la misma familia que palabras similares al texto
        
        Args:
            texto: Texto a buscar
            limite: Máximo de resultados
            
        Returns:
            Lista de palabras de la familia
        """
        try:
            cursor = self.conn.cursor()
            
            # Primero buscar palabras similares al texto
            palabras = texto.upper().split()
            resultados = []
            familias_vistas = set()
            
            for palabra in palabras:
                if len(palabra) < 3:
                    continue
                
                # Buscar familias de palabras similares
                query = """
                SELECT DISTINCT f.idfamilia, f.nombre_familia, 
                       ap.idpalabra, ap.palabra, ap.idcategoria, ap.id_impuesto,
                       ap.veces_usada, ap.peso
                FROM aprendizaje_palabras ap
                INNER JOIN palabras_familia pf ON ap.idpalabra = pf.idpalabra
                INNER JOIN familias_palabras f ON pf.idfamilia = f.idfamilia
                WHERE ? LIKE '%' + ap.palabra + '%' 
                  AND ap.activa = 1
                  AND f.activa = 1
                ORDER BY ap.peso DESC, ap.veces_usada DESC
                """
                cursor.execute(query, (texto,))
                
                for row in cursor.fetchall():
                    idfamilia = row[0]
                    if idfamilia not in familias_vistas:
                        familias_vistas.add(idfamilia)
                        resultados.append({
                            'idfamilia': idfamilia,
                            'nombre_familia': row[1],
                            'idpalabra': row[2],
                            'palabra': row[3],
                            'idcategoria': row[4],
                            'id_impuesto': row[5],
                            'veces_usada': row[6],
                            'peso': row[7] if row[7] else 1.0,
                            'metodo': 'familia'
                        })
            
            # Si encontramos familias, buscar más palabras de esas familias
            if resultados:
                familias_ids = [r['idfamilia'] for r in resultados]
                placeholders = ','.join('?' * len(familias_ids))
                
                query = f"""
                SELECT ap.idpalabra, ap.palabra, ap.idcategoria, 
                       ap.id_impuesto, ap.veces_usada, ap.peso,
                       f.nombre_familia
                FROM aprendizaje_palabras ap
                INNER JOIN palabras_familia pf ON ap.idpalabra = pf.idpalabra
                INNER JOIN familias_palabras f ON pf.idfamilia = f.idfamilia
                WHERE pf.idfamilia IN ({placeholders})
                  AND ap.activa = 1
                ORDER BY ap.peso DESC, ap.veces_usada DESC
                """
                cursor.execute(query, familias_ids)
                
                palabras_familia = []
                palabras_vistas = set()
                for row in cursor.fetchall():
                    if row[1] not in palabras_vistas:
                        palabras_vistas.add(row[1])
                        palabras_familia.append({
                            'idpalabra': row[0],
                            'palabra': row[1],
                            'idcategoria': row[2],
                            'id_impuesto': row[3],
                            'veces_usada': row[4],
                            'peso': row[5] if row[5] else 1.0,
                            'familia': row[6],
                            'metodo': 'familia_extendida'
                        })
                
                logger.info(f"🔍 Búsqueda por familia: {len(palabras_familia)} resultados")
                return palabras_familia[:limite]
            
            return []
            
        except Exception as e:
            logger.error(f"❌ Error en búsqueda por familia: {e}")
            return []
    
    def obtener_todas_familias(self) -> List[Dict]:
        """Obtiene todas las familias con estadísticas"""
        try:
            cursor = self.conn.cursor()
            
            query = """
            SELECT f.idfamilia, f.nombre_familia, f.descripcion,
                   COUNT(DISTINCT pf.idpalabra) as total_palabras,
                   SUM(ap.veces_usada) as usos_totales,
                   AVG(ap.peso) as peso_promedio
            FROM familias_palabras f
            LEFT JOIN palabras_familia pf ON f.idfamilia = pf.idfamilia
            LEFT JOIN aprendizaje_palabras ap ON pf.idpalabra = ap.idpalabra
            WHERE f.activa = 1
            GROUP BY f.idfamilia, f.nombre_familia, f.descripcion
            ORDER BY f.nombre_familia
            """
            
            cursor.execute(query)
            columns = [column[0] for column in cursor.description]
            rows = cursor.fetchall()
            
            return [dict(zip(columns, row)) for row in rows]
            
        except Exception as e:
            logger.error(f"Error obteniendo familias: {e}")
            return []
