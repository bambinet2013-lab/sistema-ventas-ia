"""
Repositorio para gestión del aprendizaje de la IA
"""
from loguru import logger
from typing import List, Dict, Optional

class AprendizajeRepositorio:
    def __init__(self, conn=None):
        """
        Inicializa el repositorio de aprendizaje
        Si no se proporciona conexión, crea una nueva usando conexion.py

        Args:
            conn: Conexión a BD (opcional). Si no se provee, se crea una.
        """
        if conn is not None:
            self.conn = conn
            logger.debug("📦 Usando conexión proporcionada para aprendizaje")
        else:
            try:
                from capa_datos.conexion import ConexionDB  # ← CAMBIO 1
                self.conn = ConexionDB().conectar()        # ← CAMBIO 2
                logger.info("✅ Conexión propia creada para aprendizaje usando ConexionDB")
            except Exception as e:
                logger.error(f"❌ Error creando conexión para aprendizaje: {e}")
                raise

        logger.info("✅ AprendizajeRepositorio inicializado")
    
    def registrar_uso(self, palabra: str, idcategoria: int, id_impuesto: int) -> bool:
        """
        Registra o actualiza una palabra aprendida con ponderación por frecuencia

        Si la palabra ya existe, incrementa sus contadores y ajusta su peso.
        Si es nueva, la inserta con peso inicial.
        """
        try:
            cursor = self.conn.cursor()

            # Verificar si la palabra ya existe
            cursor.execute("""
                SELECT idpalabra, veces_usada, veces_acertada, peso 
                FROM aprendizaje_palabras 
                WHERE palabra = ?
            """, (palabra,))

            existente = cursor.fetchone()

            if existente:
                # Calcular nuevo peso basado en frecuencia
                veces_actuales = existente[1]  # veces_usada
                peso_actual = existente[3] if existente[3] else 1.0
                
                # Fórmula de peso: base 1.0 + 0.1 por cada uso (máximo 5.0)
                nuevo_peso = min(1.0 + ((veces_actuales + 1) * 0.1), 5.0)
                
                # Actualizar palabra existente
                query = """
                UPDATE aprendizaje_palabras 
                SET veces_usada = veces_usada + 1,
                    veces_acertada = veces_acertada + 1,
                    ultima_vez = GETDATE(),
                    peso = ?
                WHERE palabra = ?
                """
                cursor.execute(query, (nuevo_peso, palabra))
                logger.debug(f"📈 Palabra actualizada: '{palabra}' (peso: {peso_actual:.2f} → {nuevo_peso:.2f})")
            else:
                # Insertar nueva palabra con peso inicial
                peso_inicial = 1.0
                query = """
                INSERT INTO aprendizaje_palabras 
                (palabra, idcategoria, id_impuesto, veces_usada, veces_acertada, peso)
                VALUES (?, ?, ?, 1, 1, ?)
                """
                cursor.execute(query, (palabra, idcategoria, id_impuesto, peso_inicial))
                logger.info(f"✨ Nueva palabra aprendida: '{palabra}' → Cat:{idcategoria}, Imp:{id_impuesto} (peso: {peso_inicial})")

            self.conn.commit()
            return True

        except Exception as e:
            logger.error(f"❌ Error registrando aprendizaje: {e}")
            self.conn.rollback()
            return False
    
    def registrar_correccion(self, nombre_producto: str, 
                             idcategoria_sugerida: Optional[int], 
                             id_impuesto_sugerido: Optional[int],
                             idcategoria_asignada: int, 
                             id_impuesto_asignado: int,
                             usuario_id: Optional[int] = None) -> bool:
        """
        Guarda en el historial cuando un usuario corrige a la IA
        """
        try:
            cursor = self.conn.cursor()
            query = """
            INSERT INTO historial_correcciones 
            (producto_nombre, idcategoria_sugerida, id_impuesto_sugerido,
             idcategoria_asignada, id_impuesto_asignado, usuario_id)
            VALUES (?, ?, ?, ?, ?, ?)
            """
            cursor.execute(query, (
                nombre_producto, 
                idcategoria_sugerida, 
                id_impuesto_sugerido,
                idcategoria_asignada, 
                id_impuesto_asignado, 
                usuario_id
            ))
            self.conn.commit()
            logger.info(f"📝 Corrección registrada para '{nombre_producto}'")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error registrando corrección: {e}")
            self.conn.rollback()
            return False
    
    def buscar_por_palabra(self, palabra: str) -> Optional[Dict]:
        """
        Busca una palabra específica en el aprendizaje
        """
        try:
            cursor = self.conn.cursor()
            query = """
            SELECT palabra, idcategoria, id_impuesto, veces_usada, 
                   veces_acertada, CAST(veces_acertada AS FLOAT)/veces_usada as confianza
            FROM aprendizaje_palabras
            WHERE palabra = ? AND activa = 1
            """
            cursor.execute(query, (palabra,))
            row = cursor.fetchone()
            
            if row:
                columns = [column[0] for column in cursor.description]
                return dict(zip(columns, row))
            return None
            
        except Exception as e:
            logger.error(f"Error buscando palabra '{palabra}': {e}")
            return None
    
    def buscar_palabras_similares(self, texto: str, limite: int = 5) -> List[Dict]:
        """
        Busca palabras que contengan el texto (búsqueda parcial)
        """
        try:
            cursor = self.conn.cursor()
            query = """
            SELECT palabra, idcategoria, id_impuesto, veces_usada,
                   CAST(veces_acertada AS FLOAT)/veces_usada as confianza
            FROM aprendizaje_palabras
            WHERE ? LIKE '%' + palabra + '%' AND activa = 1
            ORDER BY veces_usada DESC, confianza DESC
            """
            cursor.execute(query, (texto,))
            
            columns = [column[0] for column in cursor.description]
            rows = cursor.fetchall()
            return [dict(zip(columns, row)) for row in rows][:limite]
            
        except Exception as e:
            logger.error(f"Error buscando palabras similares a '{texto}': {e}")
            return []
    
    def obtener_estadisticas(self) -> Dict:
        """
        Obtiene estadísticas de aprendizaje
        """
        try:
            cursor = self.conn.cursor()
            stats = {}
            
            # Total de palabras aprendidas
            cursor.execute("SELECT COUNT(*) FROM aprendizaje_palabras WHERE activa = 1")
            stats['total_palabras'] = cursor.fetchone()[0]
            
            # Total de correcciones
            cursor.execute("SELECT COUNT(*) FROM historial_correcciones")
            stats['total_correcciones'] = cursor.fetchone()[0]
            
            # Promedio de confianza
            cursor.execute("""
                SELECT AVG(CAST(veces_acertada AS FLOAT)/veces_usada) 
                FROM aprendizaje_palabras 
                WHERE activa = 1
            """)
            stats['confianza_promedio'] = cursor.fetchone()[0] or 0
            
            return stats
            
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {e}")
            return {}

    def buscar_similares(self, texto: str, limite: int = 3) -> List[Dict]:
        """
        Busca palabras similares usando LIKE en lugar de igualdad exacta
        
        Args:
            texto: Texto completo del producto (ej: "PASTILLAS DE FRENO")
            limite: Número máximo de resultados a devolver
            
        Returns:
            List[Dict]: Lista de coincidencias con relevancia
        """
        try:
            cursor = self.conn.cursor()
            # Dividir el texto en palabras individuales
            palabras = texto.upper().split()
            resultados = []
            palabras_vistas = set()
            
            for palabra in palabras:
                if len(palabra) < 3:  # Ignorar palabras muy cortas
                    continue
                
                # Buscar palabras que CONTENGAN la palabra actual
                query = """
                SELECT palabra, idcategoria, id_impuesto, veces_usada,
                       CAST(veces_acertada AS FLOAT)/veces_usada as confianza,
                       peso
                FROM aprendizaje_palabras
                WHERE ? LIKE '%' + palabra + '%' AND activa = 1
                ORDER BY peso DESC, veces_usada DESC
                """
                cursor.execute(query, (texto,))
                
                for row in cursor.fetchall():
                    palabra_encontrada = row[0]
                    if palabra_encontrada not in palabras_vistas:
                        palabras_vistas.add(palabra_encontrada)
                        resultados.append({
                            'palabra': palabra_encontrada,
                            'idcategoria': row[1],
                            'id_impuesto': row[2],
                            'veces_usada': row[3],
                            'confianza': row[4],
                            'peso': row[5],
                            'relevancia': len(palabra_encontrada)  # Palabras más largas = más relevantes
                        })
            
            # Ordenar por relevancia y peso
            resultados.sort(key=lambda x: (-x['relevancia'], -x['peso'], -x['veces_usada']))
            
            logger.info(f"🔍 Búsqueda por similitud: {len(resultados)} resultados para '{texto}'")
            return resultados[:limite]
            
        except Exception as e:
            logger.error(f"❌ Error en búsqueda por similitud: {e}")
            return []

    # ===== NUEVO MÉTODO UNIFICADO =====
    def buscar_por_similitud(self, texto: str, limite: int = 5) -> List[Dict]:
        """
        [MÉTODO PRINCIPAL UNIFICADO]
        Busca palabras similares usando LIKE con ponderación por peso
        
        Args:
            texto: Texto completo del producto
            limite: Número máximo de resultados
            
        Returns:
            List[Dict]: Lista de coincidencias con relevancia
        """
        try:
            cursor = self.conn.cursor()
            # Dividir el texto en palabras individuales
            palabras = texto.upper().split()
            resultados = []
            palabras_vistas = set()
            
            for palabra in palabras:
                if len(palabra) < 3:  # Ignorar palabras muy cortas
                    continue
                
                # Buscar palabras que CONTENGAN la palabra actual
                query = """
                SELECT palabra, idcategoria, id_impuesto, veces_usada,
                       CAST(veces_acertada AS FLOAT)/veces_usada as confianza,
                       peso,
                       LEN(palabra) as longitud
                FROM aprendizaje_palabras
                WHERE ? LIKE '%' + palabra + '%' AND activa = 1
                ORDER BY peso DESC, veces_usada DESC, confianza DESC
                """
                cursor.execute(query, (texto,))
                
                for row in cursor.fetchall():
                    palabra_encontrada = row[0]
                    if palabra_encontrada not in palabras_vistas:
                        palabras_vistas.add(palabra_encontrada)
                        resultados.append({
                            'palabra': palabra_encontrada,
                            'idcategoria': row[1],
                            'id_impuesto': row[2],
                            'veces_usada': row[3],
                            'confianza': row[4],
                            'peso': row[5] if row[5] else 1.0,
                            'relevancia': row[6]  # Longitud de la palabra
                        })
            
            # Ordenar por peso, relevancia y frecuencia
            resultados.sort(key=lambda x: (-x['peso'], -x['relevancia'], -x['veces_usada']))
            
            logger.info(f"🔍 Búsqueda por similitud: {len(resultados)} resultados para '{texto}'")
            return resultados[:limite]
            
        except Exception as e:
            logger.error(f"❌ Error en búsqueda por similitud: {e}")
            return []
    
    # ===== MÉTODOS DE COMPATIBILIDAD =====
    def buscar_similares(self, texto: str, limite: int = 3) -> List[Dict]:
        """
        [COMPATIBILIDAD] Llama al método unificado con límite por defecto 3
        Mantenido para no romper código existente
        """
        logger.debug("🔄 buscar_similares usando método unificado buscar_por_similitud")
        return self.buscar_por_similitud(texto, limite)
    
    def buscar_palabras_similares(self, texto: str, limite: int = 5) -> List[Dict]:
        """
        [COMPATIBILIDAD] Llama al método unificado con límite por defecto 5
        Mantenido para no romper código existente
        """
        logger.debug("🔄 buscar_palabras_similares usando método unificado buscar_por_similitud")
        return self.buscar_por_similitud(texto, limite)
