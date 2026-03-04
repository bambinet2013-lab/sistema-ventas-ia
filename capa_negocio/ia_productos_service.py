"""
Servicio de Inteligencia Artificial para clasificación automática de productos
"""
from loguru import logger
from typing import Dict, List, Optional, Tuple
from capa_datos.familia_repo import FamiliaRepositorio
from capa_datos.codigo_barras_repo import CodigoBarrasRepositorio
import re

class IAProductosService:
    def __init__(self, repo_aprendizaje=None, repo_reglas=None, repo_impuestos=None, repo_familia=None, repo_codigo_barras=None):
        """
        Inicializa el servicio de IA para productos

        Args:
            repo_aprendizaje: Repositorio de aprendizaje (opcional)
            repo_reglas: Repositorio de reglas (opcional)
            repo_impuestos: Repositorio de impuestos (opcional)
            repo_familia: Repositorio de familias (opcional)
            repo_codigo_barras: Repositorio de códigos de barras (opcional)
        """
        # ===== Repositorio de aprendizaje =====
        if repo_aprendizaje is not None:
            self.repo_aprendizaje = repo_aprendizaje
            logger.info("✅ Usando repositorio de aprendizaje proporcionado")
        else:
            try:
                from capa_datos.aprendizaje_repo import AprendizajeRepositorio
                self.repo_aprendizaje = AprendizajeRepositorio()
                logger.info("✅ Repositorio de aprendizaje creado automáticamente")
            except Exception as e:
                logger.error(f"❌ Error creando repositorio de aprendizaje: {e}")
                self.repo_aprendizaje = None
        # =====================================

        self.repo_reglas = repo_reglas
        self.repo_impuestos = repo_impuestos

        # ===== Repositorio de familias =====
        if repo_familia is not None:
            self.repo_familia = repo_familia
            logger.info("✅ Usando repositorio de familias proporcionado")
        else:
            try:
                from capa_datos.familia_repo import FamiliaRepositorio
                if self.repo_aprendizaje and hasattr(self.repo_aprendizaje, 'conn'):
                    self.repo_familia = FamiliaRepositorio(self.repo_aprendizaje.conn)
                else:
                    self.repo_familia = FamiliaRepositorio()
                logger.info("✅ Repositorio de familias creado automáticamente")
            except Exception as e:
                logger.warning(f"⚠️ No se pudo crear repositorio de familias: {e}")
                self.repo_familia = None
        # =================================

        # ===== Repositorio de códigos de barras =====
        if repo_codigo_barras is not None:
            self.repo_codigo_barras = repo_codigo_barras
            logger.info("✅ Usando repositorio de códigos de barras proporcionado")
        else:
            try:
                from capa_datos.codigo_barras_repo import CodigoBarrasRepositorio
                if self.repo_aprendizaje and hasattr(self.repo_aprendizaje, 'conn'):
                    self.repo_codigo_barras = CodigoBarrasRepositorio(self.repo_aprendizaje.conn)
                else:
                    self.repo_codigo_barras = CodigoBarrasRepositorio()
                logger.info("✅ Repositorio de códigos de barras creado automáticamente")
            except Exception as e:
                logger.warning(f"⚠️ No se pudo crear repositorio de códigos de barras: {e}")
                self.repo_codigo_barras = None
        # ===========================================

        self.reglas_cargadas = False
        self.palabras_clave = {}
        self.marcas_conocidas = {}
        self.palabras_aprendidas = {}

        self.cargar_reglas_iniciales()

        if self.repo_aprendizaje:
            self.cargar_aprendizaje()
        else:
            logger.warning("⚠️ No se pudo cargar aprendizaje - IA funcionará solo con reglas fijas")

    def detectar_por_codigo_barras(self, codigo: str, nombre: str) -> Optional[Dict]:
        """
        Detecta información usando el código de barras como pista
        
        Args:
            codigo: Código de barras del producto
            nombre: Nombre del producto (para contexto)
            
        Returns:
            Diccionario con sugerencias o None
        """
        if not codigo or not hasattr(self, 'repo_codigo_barras') or not self.repo_codigo_barras:
            return None
        
        try:
            # Analizar código de barras
            resultado = self.repo_codigo_barras.sugerir_categoria_por_pais(codigo, nombre)
            
            if resultado:
                logger.info(f"📦 Producto detectado por código de barras: {resultado.get('pais', 'desconocido')}")
                
                # Si el código de barras sugiere una categoría concreta, usarla
                if resultado.get('idcategoria'):
                    return {
                        'idcategoria': resultado['idcategoria'],
                        'id_impuesto': resultado['id_impuesto'],
                        'confianza': resultado['confianza'],
                        'metodo': resultado['metodo'],
                        'pais': resultado.get('pais'),
                        'prefijo': resultado.get('prefijo')
                    }
                
                # Si solo da pista de impuesto (importado), devolver eso
                if resultado.get('id_impuesto'):
                    return {
                        'idcategoria': None,  # Sin categoría definida
                        'id_impuesto': resultado['id_impuesto'],
                        'confianza': resultado['confianza'],
                        'metodo': resultado['metodo'],
                        'pais': resultado.get('pais'),
                        'nota': 'Producto importado - requiere verificación de categoría'
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"Error en detección por código de barras: {e}")
            return None

    def detectar_por_familia(self, nombre: str) -> Optional[Dict]:
        """
        Detecta productos basándose en familias de palabras
        """
        if not nombre or not hasattr(self, 'repo_familia') or not self.repo_familia:
            return None
        
        try:
            # Buscar por familia
            resultados = self.repo_familia.buscar_por_familia(nombre, 1)
            
            if resultados:
                r = resultados[0]
                logger.info(f"👪 Producto detectado por familia: {r['familia']} → '{r['palabra']}'")
                
                # Registrar uso para reforzar
                if hasattr(self, 'repo_aprendizaje') and self.repo_aprendizaje:
                    self.repo_aprendizaje.registrar_uso(
                        palabra=r['palabra'],
                        idcategoria=r['idcategoria'],
                        id_impuesto=r['id_impuesto']
                    )
                
                return {
                    'idcategoria': r['idcategoria'],
                    'id_impuesto': r['id_impuesto'],
                    'confianza': 0.92,
                    'metodo': 'familia_palabras',
                    'familia': r['familia'],
                    'palabra': r['palabra']
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error en detección por familia: {e}")
            return None

    def normalizar_texto(self, texto: str) -> str:
        """
        Elimina tildes, diéresis y convierte a mayúsculas
        Ejemplo: "ACEITE DE OLIVA" → "ACEITE DE OLIVA"
                 "CAFÉ YOCOIMA" → "CAFE YOCOIMA"
                 "PIÑA" → "PINA"
        """
        if not texto or not isinstance(texto, str):
            return ""
        
        import unicodedata
        
        # 1. Convertir a mayúsculas
        texto_mayusculas = texto.upper()
        
        # 2. Normalizar para separar tildes (NFKD descompone caracteres)
        texto_normalizado = unicodedata.normalize('NFKD', texto_mayusculas)
        
        # 3. Eliminar los caracteres combinados (tildes, diéresis)
        texto_sin_tildes = ''.join([c for c in texto_normalizado if not unicodedata.combining(c)])
        
        return texto_sin_tildes

    def detectar_marca(self, nombre: str) -> Optional[Dict]:
        """
        Detecta si el nombre del producto contiene una marca conocida
        Las marcas se cargan desde la base de datos
        """
        if not nombre or not hasattr(self, 'repo_aprendizaje') or not self.repo_aprendizaje:
            return None
        
        try:
            cursor = self.repo_aprendizaje.conn.cursor()
            
            # Buscar marcas que estén contenidas en el nombre
            query = """
            SELECT nombre_marca, idcategoria_predeterminada, id_impuesto_predeterminado, veces_vista
            FROM marcas_conocidas
            WHERE ? LIKE '%' + nombre_marca + '%' 
              AND activa = 1
            ORDER BY LEN(nombre_marca) DESC  -- Marcas más largas primero (más específicas)
            """
            
            cursor.execute(query, (nombre,))
            resultado = cursor.fetchone()
            
            if resultado:
                # Actualizar contador de veces vista
                update_query = """
                UPDATE marcas_conocidas 
                SET veces_vista = veces_vista + 1,
                    ultima_vez_vista = GETDATE()
                WHERE nombre_marca = ?
                """
                cursor.execute(update_query, (resultado[0],))
                self.repo_aprendizaje.conn.commit()
                
                logger.info(f"🏷️ Marca detectada: '{resultado[0]}'")
                
                return {
                    'idcategoria': resultado[1],
                    'id_impuesto': resultado[2],
                    'confianza': 0.98,  # Alta confianza por ser marca conocida
                    'metodo': 'marca_conocida',
                    'marca': resultado[0],
                    'veces_vista': resultado[3] + 1
                }
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error detectando marca: {e}")
            return None

    def cargar_aprendizaje(self):
        """
        Carga las palabras aprendidas desde la base de datos
        """
        if not self.repo_aprendizaje:
            logger.warning("⚠️ Repositorio de aprendizaje no disponible")
            return
        
        try:
            # Obtener estadísticas para debug
            stats = self.repo_aprendizaje.obtener_estadisticas()
            if stats.get('total_palabras', 0) > 0:
                logger.info(f"📚 Aprendizaje cargado: {stats['total_palabras']} palabras (confianza: {stats['confianza_promedio']:.0%})")
        except Exception as e:
            logger.error(f"❌ Error cargando aprendizaje: {e}")

    def buscar_en_aprendizaje(self, nombre: str) -> Optional[Dict]:
        """
        Busca el producto en las palabras aprendidas
        
        Devuelve sugerencia basada en aprendizaje previo
        """
        if not self.repo_aprendizaje or not nombre:
            return None
        
        nombre_upper = nombre.upper()
        palabras = nombre_upper.split()
        
        # Buscar cada palabra en el aprendizaje
        for palabra in palabras:
            if len(palabra) < 3:  # Ignorar palabras muy cortas
                continue
            
            resultado = self.repo_aprendizaje.buscar_por_palabra(palabra)
            if resultado:
                confianza = resultado.get('confianza', 0.8)
                return {
                    'idcategoria': resultado['idcategoria'],
                    'id_impuesto': resultado['id_impuesto'],
                    'confianza': confianza,
                    'metodo': 'aprendizaje',
                    'palabra': resultado['palabra'],
                    'veces_usada': resultado['veces_usada']
                }
        
        # Si no encuentra palabra exacta, buscar similares
        similares = self.repo_aprendizaje.buscar_palabras_similares(nombre_upper, 1)
        if similares:
            s = similares[0]
            return {
                'idcategoria': s['idcategoria'],
                'id_impuesto': s['id_impuesto'],
                'confianza': s['confianza'] * 0.85,  # Penalizar por similitud
                'metodo': 'aprendizaje_similar',
                'palabra': s['palabra']
            }
        
        return None

    def registrar_aprendizaje(self, nombre: str, idcategoria: int, 
                              id_impuesto: int, usuario_id: int = None):
        """
        Registra una corrección manual del usuario para que la IA aprenda
        Ahora incluye categorías de motos (101-111)
        """
        if not self.repo_aprendizaje:
            logger.warning("⚠️ No se puede aprender: repositorio no disponible")
            return
        
        try:
            # Extraer palabras clave del nombre
            palabras = nombre.upper().split()
            palabras_aprendidas = []
            
            for palabra in palabras:
                if len(palabra) < 3:  # Ignorar palabras muy cortas
                    continue
                    
                if self.repo_aprendizaje.registrar_uso(palabra, idcategoria, id_impuesto):
                    palabras_aprendidas.append(palabra)
            
            # Determinar el tipo de categoría para el mensaje
            tipo_cat = "MOTOS" if idcategoria >= 100 else "SUPERMERCADO"
            
            if palabras_aprendidas:
                logger.info(f"🧠 IA aprendió ({tipo_cat}): '{', '.join(palabras_aprendidas)}' → Cat:{idcategoria}, Imp:{id_impuesto}")
            
        except Exception as e:
            logger.error(f"❌ Error registrando aprendizaje: {e}")

    def detectar_categoria_motos(self, nombre: str) -> Optional[Dict]:
        """
        Detecta si el producto pertenece a la categoría de motos
        y devuelve el ID de categoría (101-111) e impuesto (siempre 2 - General)
        """
        if not nombre:
            return None
        
        nombre_upper = nombre.upper()
        
        # Reglas para cada categoría de motos
        reglas_motos = [
            # (palabras clave, idcategoria, nombre_categoria)
            (['PISTON', 'ANILLO', 'CIGUEÑAL', 'VALVULA', 'EMPACADURA'], 101, 'Motor'),
            (['CADENA', 'PIÑON', 'CORONA', 'CORREA', 'EMBRAGUE'], 102, 'Transmisión'),
            (['PASTILLA', 'BANDA', 'DISCO FRENO', 'GUAYA', 'FRENO'], 103, 'Frenos'),
            (['AMORTIGUADOR', 'BARRA', 'RODAMIENTO', 'SUSPENSION'], 104, 'Suspensión'),
            (['BATERIA', 'BUJIA', 'CDI', 'REGULADOR', 'BOMBILLO', 'BOYA'], 105, 'Eléctrico'),
            (['ACEITE 2T', 'ACEITE 4T', 'LIGA FRENO', 'LUBRICANTE', 'ACEITE MOTOR'], 106, 'Lubricantes'),
            (['FILTRO ACEITE', 'FILTRO AIRE', 'FILTRO GASOLINA'], 107, 'Filtros'),
            (['CAUCHO', 'LLANTA', 'TRIPA', 'NEUMATICO', 'CAMARA'], 108, 'Cauchos'),
            (['CASCO', 'GUANTE', 'CHAQUETA', 'MALETERO', 'CALCOMANIA', 'PEGATINA'], 109, 'Accesorios'),
            (['HERRAMIENTA', 'LLAVE', 'DESARMADOR', 'ALICATE', 'JUEGO LLAVES'], 110, 'Herramientas'),
            (['SERVICIO', 'MANO OBRA', 'REPARACION', 'CAMBIO ACEITE', 'ENTONACION'], 111, 'Servicios')
        ]
        
        # Buscar coincidencias
        for palabras, cat_id, cat_nombre in reglas_motos:
            for palabra in palabras:
                if palabra in nombre_upper:
                    # Encontrar la palabra exacta que coincidió
                    palabra_encontrada = palabra
                    return {
                        'idcategoria': cat_id,
                        'nombre_categoria': cat_nombre,
                        'id_impuesto': 2,  # Siempre General (G) para motos
                        'confianza': 0.90,
                        'tipo': 'MOTOS',
                        'palabra_encontrada': palabra_encontrada,
                        'metodo': 'regla_fija_motos'
                    }
        
        return None
    
    def cargar_reglas_iniciales(self):
        """Carga reglas por defecto en memoria"""
        # Exentos (id_impuesto=1)
        self.palabras_clave = {
            'harina': 1, 'arroz': 1, 'azucar': 1, 'leche': 1, 'huevo': 1,
            'pan': 1, 'pasta': 1, 'carne': 1, 'pollo': 1, 'pescado': 1,
            'fruta': 1, 'verdura': 1, 'legumbre': 1, 'medicina': 1,
            # Generales (id_impuesto=2)
            'mayonesa': 2, 'salsa': 2, 'atun': 2, 'gaseosa': 2, 'refresco': 2,
            'jabon': 2, 'detergente': 2, 'shampoo': 2, 'desodorante': 2,
        }
        
        self.marcas_conocidas = {
            'santoni': 1, 'bondora': 1, 'konfit': 1, 'pampa': 1,
            'ole': 2, 'ronco': 2,
        }
        
        self.reglas_cargadas = True
        logger.info(f"✅ IAProductosService inicializado con {len(self.palabras_clave)} palabras clave")
    
    def analizar_producto(self, nombre: str, codigo_barras: str = None) -> Optional[Dict]:
        """
        Analiza el nombre del producto y sugiere categoría e impuesto
        Primero intenta con reglas fijas, luego con aprendizaje

        Args:
            nombre: Nombre del producto
            codigo_barras: Código de barras (opcional)
        """
        if not nombre:
            return None

        # Normalizar texto para ignorar tildes
        nombre_normalizado = self.normalizar_texto(nombre)
        logger.debug(f"🔍 Normalizado: '{nombre}' → '{nombre_normalizado}'")

        # ===== NUEVO: Detección por código de barras (si disponible) =====
        pista_impuesto = None
        if codigo_barras:
            resultado_codigo = self.detectar_por_codigo_barras(codigo_barras, nombre_normalizado)
            if resultado_codigo:
                # Si el código de barras dio una categoría específica, usarla
                if resultado_codigo.get('idcategoria'):
                    logger.info(f"📦 Detectado por código de barras: {resultado_codigo.get('pais')} → Cat:{resultado_codigo['idcategoria']}")
                    return resultado_codigo

                # Si solo dio pista de impuesto, guardarla para después
                pista_impuesto = resultado_codigo.get('id_impuesto')
                logger.info(f"📦 Pista por código de barras: producto importado (impuesto {pista_impuesto})")
        # ================================================================

        # ===== DETECCIÓN POR MARCA =====
        resultado_marca = self.detectar_marca(nombre_normalizado)
        if resultado_marca:
            logger.info(f"🏷️ Producto detectado por marca: {resultado_marca['marca']}")
            
            # Aprendizaje por acierto de marca
            if hasattr(self, 'repo_aprendizaje') and self.repo_aprendizaje:
                try:
                    self.repo_aprendizaje.registrar_uso(
                        palabra=resultado_marca['marca'],
                        idcategoria=resultado_marca['idcategoria'],
                        id_impuesto=resultado_marca['id_impuesto']
                    )
                    logger.info(f"🧠 Reforzando aprendizaje por marca: '{resultado_marca['marca']}'")
                except Exception as e:
                    logger.error(f"Error registrando aprendizaje de marca: {e}")
            
            return resultado_marca
        # =============================================================

        # ===== NUEVO: Detección por familia =====
        if hasattr(self, 'repo_familia') and self.repo_familia:
            resultado_familia = self.detectar_por_familia(nombre_normalizado)
            if resultado_familia:
                return resultado_familia
        # =======================================

        # 1. Intentar detectar si es producto de motos (reglas fijas)
        resultado_motos = self.detectar_categoria_motos(nombre_normalizado)
        if resultado_motos:
            logger.info(f"🏍️ Producto de motos detectado por reglas: {resultado_motos['nombre_categoria']}")

            # ===== APRENDIZAJE POR ACIERTO DE MOTOS =====
            if hasattr(self, 'repo_aprendizaje') and self.repo_aprendizaje:
                try:
                    palabra = resultado_motos.get('palabra_encontrada', '')
                    if palabra:
                        self.repo_aprendizaje.registrar_uso(
                            palabra=palabra,
                            idcategoria=resultado_motos['idcategoria'],
                            id_impuesto=resultado_motos['id_impuesto']
                        )
                        logger.info(f"🧠 Reforzando aprendizaje de motos: '{palabra}'")
                except Exception as e:
                    logger.error(f"Error registrando aprendizaje de motos: {e}")
            # ============================================

            return resultado_motos

        # 2. Intentar con aprendizaje (si existe)
        if hasattr(self, 'repo_aprendizaje') and self.repo_aprendizaje:
            # Primero buscar por similitud
            resultados_similares = self.repo_aprendizaje.buscar_similares(nombre_normalizado, 1)
            if resultados_similares:
                r = resultados_similares[0]
                logger.info(f"🧠 Producto reconocido por similitud: '{r['palabra']}' (confianza: {r['confianza']:.0%})")
                return {
                    'idcategoria': r['idcategoria'],
                    'id_impuesto': r['id_impuesto'],
                    'confianza': r['confianza'] * 0.95,
                    'metodo': 'aprendizaje_similar',
                    'palabra': r['palabra']
                }

            # Si no hay similitud, intentar búsqueda exacta
            resultado_aprendizaje = self.buscar_en_aprendizaje(nombre_normalizado)
            if resultado_aprendizaje:
                logger.info(f"🧠 Producto reconocido por aprendizaje exacto (confianza: {resultado_aprendizaje['confianza']:.0%})")
                return resultado_aprendizaje

        # 3. Reglas fijas de supermercado
        # ===== CHUCHERÍAS =====
        if any(p in nombre_normalizado for p in ['PAPITA', 'DORITO', 'SNACK', 'BOTANA', 'CHIPS']):
            return {
                'idcategoria': 2,
                'id_impuesto': 2,
                'confianza': 0.90,
                'tipo': 'SUPERMERCADO',
                'categoria_nombre': 'Víveres',
                'metodo': 'regla_fija'
            }

        # ===== BEBIDAS PROCESADAS =====
        if any(p in nombre_normalizado for p in ['MALTA', 'MALTIN', 'POLAR', 'JUGO', 'NECTAR']):
            return {
                'idcategoria': 3,
                'id_impuesto': 2,
                'confianza': 0.90,
                'tipo': 'SUPERMERCADO',
                'categoria_nombre': 'Bebidas',
                'metodo': 'regla_fija'
            }

        # ===== ENLATADOS =====
        if any(p in nombre_normalizado for p in ['ATUN', 'SARDINA', 'MAYONESA']):
            return {
                'idcategoria': 2,
                'id_impuesto': 2,
                'confianza': 0.90,
                'tipo': 'SUPERMERCADO',
                'categoria_nombre': 'Víveres',
                'metodo': 'regla_fija'
            }

        # ===== EMBUTIDOS =====
        if any(p in nombre_normalizado for p in ['JAMON', 'SALCHICHA', 'MORTADELA']):
            return {
                'idcategoria': 7,
                'id_impuesto': 1,
                'confianza': 0.90,
                'tipo': 'SUPERMERCADO',
                'categoria_nombre': 'Perecederos',
                'metodo': 'regla_fija'
            }

        # ===== PISTA DE IMPUESTO POR CÓDIGO DE BARRAS =====
        if pista_impuesto:
            logger.info(f"📦 Usando pista de código de barras: impuesto {pista_impuesto}")
            return {
                'idcategoria': None,
                'id_impuesto': pista_impuesto,
                'confianza': 0.60,
                'metodo': 'codigo_barras_solo_impuesto',
                'nota': 'Producto importado - requiere categoría'
            }
        # ==================================================

        # 4. Si nada funciona, devolver None
        logger.info(f"🤔 IA no reconoce '{nombre}', se preguntará al usuario")
        return None
    
    def obtener_nombre_impuesto(self, id_impuesto: int) -> str:
        """Obtiene el nombre del impuesto por su ID"""
        mapa = {1: 'Exento', 2: 'General', 3: 'Reducida', 4: 'Adicional'}
        return mapa.get(id_impuesto, 'Desconocido')
    
    def obtener_letra_fiscal(self, id_impuesto: int) -> str:
        """Obtiene la letra fiscal por ID de impuesto"""
        mapa = {1: 'E', 2: 'G', 3: 'R', 4: 'A'}
        return mapa.get(id_impuesto, '?')

    def detectar_categoria_venezolana(self, nombre: str) -> int:
        """
        Detecta la categoría venezolana basada en el nombre del producto
        Usando los IDs REALES de la BD:
        1: Electrónicos
        2: Viveres
        3: Bebidas
        4: Lácteos
        5: Otros
        7: Perecederos
        8: Limpieza
        9: Higiene
        """
        if not nombre:
            return 5  # Otros por defecto
        
        nombre_upper = nombre.upper()
        
        # ELECTRÓNICOS (ID 1)
        if any(palabra in nombre_upper for palabra in ['LAPTOP', 'COMPUTADORA', 'MOUSE', 'TECLADO', 
                                                        'MONITOR', 'CELULAR', 'TELEFONO', 'IMPRESORA']):
            return 1
        
        # VÍVERES (ID 2)
        if any(palabra in nombre_upper for palabra in ['HARINA', 'ARROZ', 'PASTA', 'GRANO', 'LENTEJA', 
                                                        'CARAOTA', 'QUINCHONCHO', 'AZUCAR', 'SAL', 
                                                        'ATUN', 'SARDINA', 'ENLATADO', 'MAYONESA', 
                                                        'SALSA', 'VINAGRE', 'ACEITE', 'CAFE']):
            return 2
        
        # BEBIDAS (ID 3)
        if any(palabra in nombre_upper for palabra in ['REFRESCO', 'GASEOSA', 'JUGO', 'MALTA', 'AGUA',
                                                        'POLAR', 'COCA', 'PEPSI', 'CHINOTO', 'FRESCOLITA']):
            return 3
        
        # LÁCTEOS (ID 4)
        if any(palabra in nombre_upper for palabra in ['LECHE', 'QUESO', 'YOGURT', 'MANTEQUILLA', 
                                                        'MARGARINA', 'KUMIS']):
            return 4
        
        # PERECEDEROS (ID 7)
        if any(palabra in nombre_upper for palabra in ['CARNE', 'POLLO', 'PESCADO', 'RES', 'CERDO',
                                                        'FRUTA', 'VERDURA', 'CEBOLLA', 'TOMATE',
                                                        'PIMENTON', 'Auyama', 'LECHOSA', 'PATILLA',
                                                        'MELON', 'CAMBUR', 'PLATANO']):
            return 7
        
        # LIMPIEZA (ID 8)
        if any(palabra in nombre_upper for palabra in ['JABON', 'DETERGENTE', 'CLORO', 'LIMPIDO',
                                                        'SUAVIZANTE', 'LYSOL', 'FAB', 'ARIEL']):
            return 8
        
        # HIGIENE (ID 9)
        if any(palabra in nombre_upper for palabra in ['SHAMPOO', 'ACONDICIONADOR', 'DESODORANTE',
                                                        'PASTA DENTAL', 'CEPILLO', 'JABON DE BAÑO',
                                                        'PREND', 'COLGATE', 'AXE']):
            return 9
        
        # OTROS (ID 5) - por defecto
        return 5
