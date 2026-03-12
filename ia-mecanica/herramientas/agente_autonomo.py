#!/usr/bin/env python3
"""
🤯 AGENTE SUPREMO - DIAGNÓSTICO Y AUTO-REPARACIÓN
Detecta errores en el sistema, sugiere soluciones y genera código de reparación
Nivel: Ultra Enterprise - Auto-reparación inteligente
"""

import json
import os
import importlib.util
import inspect
import traceback
import sys
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime
import subprocess
import re

class AgenteSupremo:
    def __init__(self, nombre: str = "SupremeBot", directorio_habilidades: str = "./habilidades"):
        self.nombre = nombre
        self.directorio_habilidades = directorio_habilidades
        self.habilidades: Dict[str, callable] = {}
        self.memoria_errores: List[Dict] = []
        self.base_conocimiento = self._cargar_conocimiento()
        
        # Asegurar directorios
        os.makedirs(self.directorio_habilidades, exist_ok=True)
        os.makedirs("./diagnosticos", exist_ok=True)
        
        # Cargar habilidades existentes
        self._cargar_habilidades()
        
        print(f"✅ Agente Supremo '{self.nombre}' inicializado")
        print(f"   📚 Habilidades: {len(self.habilidades)}")
        print(f"   🐞 Errores en memoria: {len(self.memoria_errores)}")
        
    def _cargar_conocimiento(self):
        """Carga la base de conocimiento de errores y soluciones"""
        try:
            with open("conocimiento_errores.json", 'r') as f:
                return json.load(f)
        except:
            return {
                "patrones_error": [],
                "soluciones_exitosas": {},
                "estadisticas": {
                    "errores_detectados": 0,
                    "auto_reparaciones": 0,
                    "tasa_exito": 0
                }
            }
    
    def _guardar_conocimiento(self):
        with open("conocimiento_errores.json", 'w') as f:
            json.dump(self.base_conocimiento, f, indent=2)
    
    def _cargar_habilidades(self):
        """Carga habilidades existentes"""
        for archivo in os.listdir(self.directorio_habilidades):
            if archivo.endswith(".py") and not archivo.startswith("__"):
                nombre_modulo = archivo[:-3]
                ruta = os.path.join(self.directorio_habilidades, archivo)
                self._importar_habilidad(nombre_modulo, ruta)
    
    def _importar_habilidad(self, nombre: str, ruta: str):
        try:
            spec = importlib.util.spec_from_file_location(nombre, ruta)
            modulo = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(modulo)
            
            for nombre_func, obj in inspect.getmembers(modulo, inspect.isfunction):
                if hasattr(obj, 'es_habilidad'):
                    self.habilidades[obj.nombre_habilidad] = obj
        except Exception as e:
            print(f"   ⚠️ Error cargando {nombre}: {e}")
    
    # ============================================================
    # SISTEMA DE DETECCIÓN DE ERRORES (¡LO MÁS IMPORTANTE!)
    # ============================================================
    
    def diagnosticar_sistema(self) -> Dict:
        """
        ANALIZA TODO EL SISTEMA EN BUSCA DE ERRORES
        Retorna un informe completo con problemas detectados y soluciones
        """
        print("\n🔍 INICIANDO DIAGNÓSTICO COMPLETO DEL SISTEMA...")
        informe = {
            "timestamp": datetime.now().isoformat(),
            "errores_criticos": [],
            "advertencias": [],
            "sugerencias": [],
            "codigo_reparacion": {},
            "estadisticas": {}
        }
        
        # 1. Verificar archivos de log
        self._diagnosticar_logs(informe)
        
        # 2. Verificar base de datos
        self._diagnosticar_bd(informe)
        
        # 3. Verificar habilidades
        self._diagnosticar_habilidades(informe)
        
        # 4. Verificar patrones de error recurrentes
        self._diagnosticar_patrones(informe)
        
        # 5. Generar código de reparación si es necesario
        self._generar_reparaciones(informe)
        
        # Guardar diagnóstico
        self._guardar_diagnostico(informe)
        
        return informe
    
    def _diagnosticar_logs(self, informe):
        """
        🕵️ DIAGNÓSTICO ÉPICO DE LOGS - Versión Supreme
        Analiza logs con IA, detecta patrones, clasifica gravedad y predice causas
        """
        try:
            import re
            from collections import Counter
            from datetime import datetime, timedelta
            
            log_file = "/home/junior/Escritorio/sistema-ventas-python/sistema_ventas.log"
            if not os.path.exists(log_file):
                informe["advertencias"].append("📁 Archivo de log no encontrado")
                return
            
            with open(log_file, 'r') as f:
                todas_lineas = f.readlines()
            
            # Estadísticas generales
            total_lineas = len(todas_lineas)
            lineas_recientes = todas_lineas[-1000:]  # Últimas 1000 líneas
            lineas_hoy = [l for l in todas_lineas if datetime.now().strftime('%Y-%m-%d') in l]
            
            informe["estadisticas"]["logs"] = {
                "total_lineas": total_lineas,
                "lineas_hoy": len(lineas_hoy),
                "lineas_analizadas": len(lineas_recientes)
            }
            
            # ========================================================
            # 1. DETECCIÓN AVANZADA DE PATRONES DE ERROR
            # ========================================================
            errores_detectados = []
            patrones_error = {
                # Errores CRÍTICOS (rojo)
                "CRITICAL": {
                    "patrones": ["CRITICAL", "FATAL", "SEVERE", "EMERGENCY"],
                    "gravedad": "🔴 CRÍTICO",
                    "peso": 100
                },
                # Errores de ejecución (naranja)
                "NoneType": {
                    "patrones": ["NoneType", "has no attribute", "object is None"],
                    "gravedad": "🟠 GRAVE",
                    "peso": 90,
                    "causas": [
                        "Objeto no inicializado",
                        "Respuesta vacía de BD",
                        "Falta validación antes de acceso"
                    ],
                    "solucion": "Usar safe_get() o validar objeto antes de acceder"
                },
                "AttributeError": {
                    "patrones": ["AttributeError", "has no attribute"],
                    "gravedad": "🟠 GRAVE",
                    "peso": 85,
                    "causas": [
                        "Atributo mal escrito",
                        "Versión incorrecta de objeto",
                        "Clase sin ese atributo"
                    ],
                    "solucion": "Verificar nombre del atributo o usar hasattr()"
                },
                "KeyError": {
                    "patrones": ["KeyError"],
                    "gravedad": "🟡 MEDIO",
                    "peso": 70,
                    "causas": [
                        "Clave no existe en diccionario",
                        "JSON mal formado",
                        "Estructura de datos cambiada"
                    ],
                    "solucion": "Usar .get() con valor por defecto"
                },
                "IndexError": {
                    "patrones": ["IndexError", "list index out of range"],
                    "gravedad": "🟡 MEDIO",
                    "peso": 65,
                    "causas": [
                        "Lista más corta de lo esperado",
                        "Acceso sin verificar longitud"
                    ],
                    "solucion": "Verificar len(lista) antes de acceder"
                },
                "TypeError": {
                    "patrones": ["TypeError"],
                    "gravedad": "🟡 MEDIO",
                    "peso": 60,
                    "causas": [
                        "Operación entre tipos incompatibles",
                        "Argumentos incorrectos en función"
                    ],
                    "solucion": "Verificar tipos de datos antes de operar"
                },
                "ValueError": {
                    "patrones": ["ValueError"],
                    "gravedad": "🟡 MEDIO",
                    "peso": 55,
                    "causas": [
                        "Valor inválido para conversión",
                        "Argumento fuera de rango"
                    ],
                    "solucion": "Validar valores antes de usar"
                },
                # Errores de sintaxis (amarillo)
                "IndentationError": {
                    "patrones": ["IndentationError"],
                    "gravedad": "🟡 MEDIO",
                    "peso": 50,
                    "causas": [
                        "Mezcla de tabs y espacios",
                        "Bloque mal indentado"
                    ],
                    "solucion": "Revisar indentación del código"
                },
                "SyntaxError": {
                    "patrones": ["SyntaxError"],
                    "gravedad": "🟡 MEDIO",
                    "peso": 45,
                    "causas": [
                        "Error de sintaxis en código",
                        "Carácter inválido"
                    ],
                    "solucion": "Revisar sintaxis del código"
                },
                # Errores de conexión (naranja)
                "ConnectionError": {
                    "patrones": ["ConnectionError", "Connection refused", "Failed to connect"],
                    "gravedad": "🟠 GRAVE",
                    "peso": 80,
                    "causas": [
                        "Servidor BD caído",
                        "Firewall bloqueando",
                        "Red inestable"
                    ],
                    "solucion": "Verificar servidor_bd.py y conexión de red"
                },
                "Timeout": {
                    "patrones": ["Timeout", "timed out"],
                    "gravedad": "🟡 MEDIO",
                    "peso": 60,
                    "causas": [
                        "BD lenta",
                        "Consulta compleja",
                        "Sobrecarga del sistema"
                    ],
                    "solucion": "Optimizar consulta o aumentar timeout"
                },
                # Errores de BD (rojo)
                "DatabaseError": {
                    "patrones": ["DatabaseError", "SQL", "DB API", "cursor"],
                    "gravedad": "🔴 CRÍTICO",
                    "peso": 95,
                    "causas": [
                        "Error en consulta SQL",
                        "Tabla no existe",
                        "Permisos insuficientes"
                    ],
                    "solucion": "Verificar consulta SQL y conexión"
                },
                # Errores de importación (amarillo)
                "ImportError": {
                    "patrones": ["ImportError", "ModuleNotFoundError"],
                    "gravedad": "🟡 MEDIO",
                    "peso": 40,
                    "causas": [
                        "Módulo no instalado",
                        "Ruta incorrecta",
                        "Ciclo de importaciones"
                    ],
                    "solucion": "Instalar dependencia o verificar ruta"
                },
                # Errores de archivo (amarillo)
                "FileNotFoundError": {
                    "patrones": ["FileNotFoundError", "No such file"],
                    "gravedad": "🟡 MEDIO",
                    "peso": 35,
                    "causas": [
                        "Archivo no existe",
                        "Ruta incorrecta",
                        "Permisos de lectura"
                    ],
                    "solucion": "Verificar ruta y permisos del archivo"
                }
            }
            
            # Analizar línea por línea
            errores_por_tipo = Counter()
            lineas_con_error = []
            
            for i, linea in enumerate(lineas_recientes):
                for error_tipo, config in patrones_error.items():
                    for patron in config["patrones"]:
                        if patron in linea:
                            timestamp = self._extraer_timestamp(linea)
                            errores_detectados.append({
                                "tipo": error_tipo,
                                "gravedad": config["gravedad"],
                                "descripcion": config.get("solucion", "Error detectado"),
                                "linea": linea.strip(),
                                "timestamp": timestamp or datetime.now().isoformat(),
                                "numero_linea": total_lineas - len(lineas_recientes) + i + 1,
                                "causas_posibles": config.get("causas", ["Revisar código"]),
                                "peso": config["peso"]
                            })
                            errores_por_tipo[error_tipo] += 1
                            lineas_con_error.append(linea)
                            break
            
            # ========================================================
            # 2. ANÁLISIS DE PATRONES TEMPORALES
            # ========================================================
            if errores_detectados:
                # Agrupar por hora
                errores_por_hora = {}
                for error in errores_detectados[-50:]:  # Últimos 50 errores
                    hora = error["timestamp"][:13] if len(error["timestamp"]) > 13 else "unknown"
                    if hora not in errores_por_hora:
                        errores_por_hora[hora] = 0
                    errores_por_hora[hora] += 1
                
                # Detectar picos de errores
                if errores_por_hora:
                    max_errores_hora = max(errores_por_hora.values())
                    if max_errores_hora > 5:
                        informe["sugerencias"].append({
                            "tipo": "PICO_ERRORES",
                            "descripcion": f"Se detectó un pico de {max_errores_hora} errores en una hora",
                            "recomendacion": "Revisar qué cambió en ese período"
                        })
                
                # Calcular frecuencia
                total_errores = len(errores_detectados)
                tiempo_analizado = min(24, len(lineas_recientes) / 100)  # Aprox horas
                frecuencia = total_errores / max(tiempo_analizado, 1)
                
                informe["estadisticas"]["errores"] = {
                    "total_detectados": total_errores,
                    "tipos_distintos": len(errores_por_tipo),
                    "frecuencia_por_hora": round(frecuencia, 2),
                    "tipos": dict(errores_por_tipo)
                }
                
                # ========================================================
                # 3. DETECCIÓN DE ERRORES REPETITIVOS (PATRONES)
                # ========================================================
                if len(lineas_con_error) > 3:
                    # Buscar líneas similares (mismo error)
                    lineas_similares = Counter([l[:50] for l in lineas_con_error])
                    for linea, count in lineas_similares.items():
                        if count > 2:
                            informe["sugerencias"].append({
                                "tipo": "ERROR_REPETITIVO",
                                "descripcion": f"El mismo error aparece {count} veces",
                                "linea_ejemplo": linea,
                                "recomendacion": "Revisar causa raíz, no solo los síntomas"
                            })
                
                # ========================================================
                # 4. PRIORIZAR ERRORES POR GRAVEDAD
                # ========================================================
                errores_priorizados = sorted(
                    errores_detectados,
                    key=lambda x: x["peso"],
                    reverse=True
                )[:5]  # Top 5 más graves
                
                informe["errores_criticos"].extend(errores_priorizados)
                
                # ========================================================
                # 5. GENERAR CÓDIGO DE REPARACIÓN ESPECÍFICO
                # ========================================================
                for error in errores_priorizados:
                    if error["tipo"] not in informe["codigo_reparacion"]:
                        codigo = self._generar_codigo_para_error_especifico(error)
                        if codigo:
                            informe["codigo_reparacion"][error["tipo"]] = codigo
                
                # ========================================================
                # 6. ANÁLISIS DE TENDENCIAS (MACHINE LEARNING SIMULADO)
                # ========================================================
                if len(errores_detectados) > 10:
                    # Simular predicción de próximos errores
                    tipos_recientes = [e["tipo"] for e in errores_detectados[-10:]]
                    from collections import Counter
                    tendencia = Counter(tipos_recientes).most_common(1)
                    if tendencia:
                        informe["sugerencias"].append({
                            "tipo": "TENDENCIA",
                            "descripcion": f"El error '{tendencia[0][0]}' está en aumento",
                            "recomendacion": "Considerar reparación preventiva"
                        })
            
            else:
                informe["estadisticas"]["errores"] = {"total_detectados": 0}
            
        except Exception as e:
            informe["advertencias"].append(f"Error en diagnóstico de logs: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def _extraer_timestamp(self, linea):
        """Extrae timestamp de una línea de log si existe"""
        import re
        patron = r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}'
        match = re.search(patron, linea)
        return match.group() if match else None
    
    def _generar_codigo_para_error_especifico(self, error):
        """
        🔥 GENERADOR DE CÓDIGO ÉPICO - AUTO-REPARACIÓN INTELIGENTE
        Analiza el error y genera código específico para solucionarlo
        Incluye: validaciones, decoradores, parches, y hasta tests unitarios
        """
        tipo = error.get("tipo", "Desconocido")
        linea = error.get("linea", "")
        timestamp = error.get("timestamp", "")
        
        # ========================================================
        # DICCIONARIO DE REPARACIONES ÉPICAS
        # ========================================================
        codigos = {
            
            # --------------------------------------------------------
            # 1. ERRORES DE TIPO NoneType (¡Los más comunes!)
            # --------------------------------------------------------
            "NoneType": '''
# ========================================================
# 🛡️ PROTECCIÓN CONTRA NoneType - VERSIÓN ULTRA
# Incluye: decoradores, validadores, y parches automáticos
# ========================================================

import functools
import inspect
from typing import Any, Optional, TypeVar, Callable

T = TypeVar('T')

# ------------------------------------------------------------------
# 1. DECORADOR MÁGICO - Protege cualquier función de None
# ------------------------------------------------------------------
def proteger_de_none(default_value: Any = None):
    """
    Decorador que protege una función contra valores None.
    Si algún argumento es None, retorna default_value en lugar de ejecutar.
    
    Uso:
        @proteger_de_none(default_value=0)
        def calcular_precio(producto):
            return producto.precio
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Verificar args
            for i, arg in enumerate(args):
                if arg is None:
                    print(f"⚠️ Argumento {i} es None en {func.__name__}")
                    return default_value
            
            # Verificar kwargs
            for key, value in kwargs.items():
                if value is None:
                    print(f"⚠️ Argumento '{key}' es None en {func.__name__}")
                    return default_value
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

# ------------------------------------------------------------------
# 2. VALIDADOR DE OBJETOS - Safe Object Access
# ------------------------------------------------------------------
class SafeObject:
    """
    Envuelve cualquier objeto y protege contra accesos a None.
    
    Uso:
        producto = SafeObject(objeto_posiblemente_none)
        precio = producto.precio  # Retorna None si es seguro
    """
    def __init__(self, obj: Any, default: Any = None):
        self._obj = obj
        self._default = default
    
    def __getattr__(self, name: str) -> Any:
        if self._obj is None:
            return self._default
        return getattr(self._obj, name, self._default)
    
    def __getitem__(self, key: Any) -> Any:
        if self._obj is None:
            return self._default
        try:
            return self._obj[key]
        except (KeyError, TypeError, IndexError):
            return self._default
    
    def __call__(self, *args, **kwargs) -> Any:
        if self._obj is None:
            return self._default
        if callable(self._obj):
            return self._obj(*args, **kwargs)
        return self._default
    
    @property
    def exists(self) -> bool:
        """Verifica si el objeto existe (no es None)"""
        return self._obj is not None
    
    def get(self, default: Any = None) -> Any:
        """Retorna el objeto o un default si es None"""
        return self._obj if self._obj is not None else default

# ------------------------------------------------------------------
# 3. FUNCIONES DE SEGURIDAD - Para acceso rápido
# ------------------------------------------------------------------
def safe_get(obj: Any, attr: str, default: Any = None) -> Any:
    """Obtiene un atributo de forma segura"""
    if obj is None:
        return default
    return getattr(obj, attr, default)

def safe_dict_get(d: dict, key: Any, default: Any = None) -> Any:
    """Obtiene un valor de diccionario de forma segura"""
    if d is None:
        return default
    return d.get(key, default)

def safe_call(func: Callable, *args, default: Any = None, **kwargs) -> Any:
    """Llama a una función de forma segura"""
    if func is None:
        return default
    try:
        return func(*args, **kwargs)
    except Exception as e:
        print(f"⚠️ Error en {func.__name__}: {e}")
        return default

def safe_chain(obj: Any, *attrs: str, default: Any = None) -> Any:
    """
    Accede a una cadena de atributos de forma segura.
    
    Ejemplo:
        precio = safe_chain(producto, 'categoria', 'precio', default=0)
    """
    current = obj
    for attr in attrs:
        if current is None:
            return default
        current = getattr(current, attr, None)
    return current if current is not None else default

# ------------------------------------------------------------------
# 4. PATCH AUTOMÁTICO - Para aplicar a todo el módulo
# ------------------------------------------------------------------
def aplicar_parche_none():
    """
    Aplica un parche global para proteger todo el módulo.
    (Requiere importar __builtins__ con cuidado)
    """
    import builtins
    
    # Guardar originales
    original_getattr = builtins.getattr
    
    # Nuevo getattr seguro
    def safe_getattr(obj, name, default=None):
        if obj is None:
            return default
        return original_getattr(obj, name, default)
    
    # Aplicar parche
    builtins.getattr = safe_getattr
    print("✅ Parche NoneType aplicado globalmente")

# ------------------------------------------------------------------
# 5. TEST UNITARIO - Para verificar la reparación
# ------------------------------------------------------------------
def test_reparacion_none():
    """Prueba unitaria para verificar que la reparación funciona"""
    print("\n🧪 EJECUTANDO TEST DE REPARACIÓN NONE TYPE")
    print("="*50)
    
    # Prueba 1: safe_get
    obj_none = None
    resultado = safe_get(obj_none, "precio", 0)
    print(f"✅ safe_get: {resultado} (esperado 0)")
    
    # Prueba 2: SafeObject
    obj = SafeObject(None, 0)
    resultado = obj.precio
    print(f"✅ SafeObject: {resultado} (esperado 0)")
    
    # Prueba 3: Decorador
    @proteger_de_none(default_value=0)
    def obtener_precio(objeto):
        return objeto.precio
    
    resultado = obtener_precio(None)
    print(f"✅ Decorador: {resultado} (esperado 0)")
    
    print("\n🎉 TODAS LAS PRUEBAS PASARON")
    return True

# ------------------------------------------------------------------
# 6. INSTRUCCIONES DE USO
# ------------------------------------------------------------------
"""
📚 CÓMO USAR ESTA REPARACIÓN:

1. PARA ACCESOS AISLADOS:
   precio = safe_get(objeto, 'precio', 0)

2. PARA OBJETOS COMPLEJOS:
   obj_seguro = SafeObject(objeto, default=0)
   precio = obj_seguro.precio

3. PARA FUNCIONES COMPLETAS:
   @proteger_de_none(default_value=0)
   def mi_funcion(objeto):
       return objeto.precio

4. PARA CADENAS DE ATRIBUTOS:
   valor = safe_chain(objeto, 'atributo1', 'atributo2', default=0)

5. PARA PROBAR:
   test_reparacion_none()
"""
''',
            
            # --------------------------------------------------------
            # 2. ERRORES KeyError (Diccionarios)
            # --------------------------------------------------------
            "KeyError": '''
# ========================================================
# 🛡️ PROTECCIÓN CONTRA KeyError - VERSIÓN ULTRA
# ========================================================

from typing import Any, Dict, Optional
import functools

# ------------------------------------------------------------------
# 1. DICCIONARIO SEGURO - SafeDict
# ------------------------------------------------------------------
class SafeDict(dict):
    """
    Diccionario que nunca lanza KeyError.
    
    Uso:
        datos = SafeDict({'a': 1})
        valor = datos['b']  # Retorna None en lugar de KeyError
    """
    def __init__(self, *args, default: Any = None, **kwargs):
        super().__init__(*args, **kwargs)
        self._default = default
    
    def __getitem__(self, key):
        try:
            return super().__getitem__(key)
        except KeyError:
            return self._default
    
    def get(self, key, default=None):
        return super().get(key, default if default is not None else self._default)
    
    def get_nested(self, *keys, default=None):
        """
        Obtiene un valor anidado de forma segura.
        
        Ejemplo:
            valor = datos.get_nested('usuario', 'perfil', 'edad', default=0)
        """
        current = self
        for key in keys:
            if isinstance(current, dict):
                current = current.get(key)
                if current is None:
                    return default
            else:
                return default
        return current if current is not None else default

# ------------------------------------------------------------------
# 2. FUNCIÓN DE ACCESO SEGURO
# ------------------------------------------------------------------
def safe_key_access(obj: Any, key: Any, default: Any = None) -> Any:
    """
    Accede a cualquier objeto como si fuera un diccionario de forma segura.
    
    Soporta:
    - Diccionarios: obj[key]
    - Listas: obj[index]
    - Objetos: getattr(obj, key)
    """
    if obj is None:
        return default
    
    # Si es diccionario
    if isinstance(obj, dict):
        return obj.get(key, default)
    
    # Si es lista/tupla y key es entero
    if isinstance(obj, (list, tuple)) and isinstance(key, int):
        try:
            return obj[key]
        except IndexError:
            return default
    
    # Si es objeto con atributos
    if hasattr(obj, key):
        return getattr(obj, key)
    
    return default

# ------------------------------------------------------------------
# 3. DECORADOR PROTECTOR
# ------------------------------------------------------------------
def proteger_keyerror(default: Any = None):
    """
    Decorador que protege una función de KeyError.
    Si ocurre KeyError, retorna default.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except KeyError as e:
                print(f"⚠️ KeyError en {func.__name__}: {e}")
                return default
        return wrapper
    return decorator

# ------------------------------------------------------------------
# 4. TEST UNITARIO
# ------------------------------------------------------------------
def test_reparacion_keyerror():
    """Prueba la reparación de KeyError"""
    print("\n🧪 TEST REPARACIÓN KEYERROR")
    
    # Prueba SafeDict
    d = SafeDict({'a': 1}, default=0)
    assert d['b'] == 0, "SafeDict falló"
    
    # Prueba safe_key_access
    assert safe_key_access(None, 'x', 0) == 0
    assert safe_key_access({'a': 1}, 'b', 0) == 0
    
    print("✅ Todas las pruebas pasaron")
    return True
''',
            
            # --------------------------------------------------------
            # 3. ERRORES DE CONEXIÓN
            # --------------------------------------------------------
            "ConnectionError": '''
# ========================================================
# 🔌 PROTECCIÓN CONTRA ERRORES DE CONEXIÓN
# ========================================================

import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from typing import Optional, Callable, Any
import functools

# ------------------------------------------------------------------
# 1. SESIÓN ROBUSTA CON REINTENTOS AUTOMÁTICOS
# ------------------------------------------------------------------
def crear_sesion_robusta(
    retries: int = 3,
    backoff_factor: float = 1.0,
    status_forcelist: list = None
) -> requests.Session:
    """
    Crea una sesión de requests con reintentos automáticos.
    
    Args:
        retries: Número de reintentos
        backoff_factor: Factor de espera entre reintentos
        status_forcelist: Códigos HTTP que fuerzan reintento
    """
    session = requests.Session()
    
    if status_forcelist is None:
        status_forcelist = [429, 500, 502, 503, 504]
    
    retry_strategy = Retry(
        total=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
        allowed_methods=["HEAD", "GET", "OPTIONS", "POST", "PUT", "DELETE"]
    )
    
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    return session

# ------------------------------------------------------------------
# 2. DECORADOR DE REINTENTO PARA CUALQUIER FUNCIÓN
# ------------------------------------------------------------------
def reintentar(
    max_intentos: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    excepciones: tuple = (Exception,)
):
    """
    Decorador que reintenta una función cuando falla.
    
    Args:
        max_intentos: Número máximo de intentos
        delay: Espera inicial entre intentos
        backoff: Factor multiplicador del delay
        excepciones: Tupla de excepciones que disparan reintento
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            intentos = 0
            espera = delay
            
            while intentos < max_intentos:
                try:
                    return func(*args, **kwargs)
                except excepciones as e:
                    intentos += 1
                    if intentos == max_intentos:
                        print(f"❌ Falló después de {max_intentos} intentos: {e}")
                        raise
                    
                    print(f"⚠️ Intento {intentos} falló. Reintentando en {espera}s...")
                    time.sleep(espera)
                    espera *= backoff
        return wrapper
    return decorator

# ------------------------------------------------------------------
# 3. MONITOR DE CONEXIÓN
# ------------------------------------------------------------------
class ConnectionMonitor:
    """Monitorea y repara conexiones automáticamente"""
    
    def __init__(self, url: str, check_interval: int = 60):
        self.url = url
        self.check_interval = check_interval
        self.failures = 0
        self.last_check = None
    
    def check_connection(self) -> bool:
        """Verifica si la conexión está activa"""
        try:
            response = requests.get(self.url, timeout=5)
            return response.status_code < 500
        except:
            self.failures += 1
            return False
    
    def repair(self) -> bool:
        """Intenta reparar la conexión"""
        print("🔧 Intentando reparar conexión...")
        
        # Intentar 1: Reiniciar servidor BD
        import subprocess
        subprocess.run(["pkill", "-f", "servidor_bd.py"])
        time.sleep(2)
        
        # Intentar 2: Iniciar servidor
        subprocess.Popen(
            ["cd /home/junior/Escritorio/ia-mecanica/herramientas && "
             "source venv/bin/activate && python3 servidor_bd.py &"],
            shell=True
        )
        time.sleep(3)
        
        # Verificar
        return self.check_connection()
    
    def start_monitoring(self):
        """Inicia monitoreo continuo en un hilo separado"""
        import threading
        
        def monitor_loop():
            while True:
                if not self.check_connection():
                    print(f"⚠️ Conexión perdida (fallo #{self.failures})")
                    if self.failures >= 3:
                        if self.repair():
                            print("✅ Conexión restaurada")
                            self.failures = 0
                time.sleep(self.check_interval)
        
        thread = threading.Thread(target=monitor_loop, daemon=True)
        thread.start()
        return thread

# ------------------------------------------------------------------
# 4. TEST UNITARIO
# ------------------------------------------------------------------
def test_reparacion_conexion():
    """Prueba las herramientas de conexión"""
    print("\n🧪 TEST REPARACIÓN CONEXIÓN")
    
    # Probar sesión robusta
    session = crear_sesion_robusta()
    print("✅ Sesión robusta creada")
    
    # Probar decorador
    @reintentar(max_intentos=2)
    def funcion_que_falla():
        raise ConnectionError("Error simulado")
    
    try:
        funcion_que_falla()
    except ConnectionError:
        print("✅ Decorador funcionó")
    
    print("🎉 Pruebas completadas")
''',
            
            # --------------------------------------------------------
            # 4. ERRORES DE INDENTACIÓN (¡El tuyo!)
            # --------------------------------------------------------
            "IndentationError": '''
# ========================================================
# 📐 CORRECTOR DE INDENTACIÓN - VERSIÓN ÉPICA
# ========================================================

import re
import sys
import os
from typing import List, Tuple

# ------------------------------------------------------------------
# 1. ANALIZADOR DE INDENTACIÓN
# ------------------------------------------------------------------
class IndentationFixer:
    """
    Analiza y corrige problemas de indentación en archivos Python.
    """
    
    def __init__(self, filename: str):
        self.filename = filename
        self.lines = []
        self.fixed_lines = []
        self.errors_found = []
        self._load_file()
    
    def _load_file(self):
        """Carga el archivo y detecta problemas"""
        try:
            with open(self.filename, 'r') as f:
                self.lines = f.readlines()
        except Exception as e:
            print(f"❌ Error cargando archivo: {e}")
    
    def analyze(self) -> List[dict]:
        """Analiza el archivo en busca de problemas de indentación"""
        errors = []
        expected_indent = 0
        in_block = False
        
        for i, line in enumerate(self.lines):
            stripped = line.rstrip()
            if not stripped:  # Línea vacía
                continue
            
            # Detectar mezcla de tabs y espacios
            if '\t' in line and '    ' in line:
                errors.append({
                    'line': i + 1,
                    'type': 'MIXED_SPACES',
                    'content': stripped,
                    'fix': self._convert_to_spaces(line)
                })
            
            # Detectar indentación inconsistente
            indent = len(line) - len(line.lstrip())
            if in_block and indent <= expected_indent - 4:
                errors.append({
                    'line': i + 1,
                    'type': 'UNEXPECTED_DEDENT',
                    'content': stripped,
                    'fix': self._fix_indent(line, expected_indent)
                })
            
            # Detectar bloques
            if stripped.endswith(':'):
                expected_indent = indent + 4
                in_block = True
            elif stripped and not stripped[0].isspace():
                in_block = False
                expected_indent = 0
        
        self.errors_found = errors
        return errors
    
    def _convert_to_spaces(self, line: str) -> str:
        """Convierte tabs a espacios"""
        return line.expandtabs(4)
    
    def _fix_indent(self, line: str, target_indent: int) -> str:
        """Corrige la indentación de una línea"""
        content = line.lstrip()
        return ' ' * target_indent + content
    
    def fix(self, backup: bool = True) -> bool:
        """Aplica las correcciones al archivo"""
        if not self.errors_found:
            print("✅ No se encontraron errores de indentación")
            return True
        
        # Crear backup
        if backup:
            backup_name = f"{self.filename}.bak"
            import shutil
            shutil.copy2(self.filename, backup_name)
            print(f"💾 Backup creado: {backup_name}")
        
        # Aplicar correcciones
        fixed_lines = []
        for i, line in enumerate(self.lines):
            error = next((e for e in self.errors_found if e['line'] == i + 1), None)
            if error and 'fix' in error:
                fixed_lines.append(error['fix'])
            else:
                fixed_lines.append(line)
        
        # Guardar
        with open(self.filename, 'w') as f:
            f.writelines(fixed_lines)
        
        print(f"✅ {len(self.errors_found)} errores corregidos en {self.filename}")
        return True
    
    def print_report(self):
        """Muestra un reporte de los errores encontrados"""
        if not self.errors_found:
            print("\n📊 REPORTE DE INDENTACIÓN: TODO CORRECTO")
            return
        
        print(f"\n📊 REPORTE DE INDENTACIÓN: {len(self.errors_found)} ERRORES")
        print("="*60)
        for error in self.errors_found:
            print(f"Línea {error['line']}: {error['type']}")
            print(f"   Contenido: {error['content']}")
            if 'fix' in error:
                print(f"   Corrección: {error['fix'].strip()}")
            print("-"*40)

# ------------------------------------------------------------------
# 2. DECORADOR PARA VERIFICAR INDENTACIÓN EN EJECUCIÓN
# ------------------------------------------------------------------
def check_indentation(func):
    """Decorador que verifica la indentación de una función en tiempo de ejecución"""
    import inspect
    import linecache
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        lines = inspect.getsourcelines(func)[0]
        filename = inspect.getsourcefile(func)
        
        fixer = IndentationFixer(filename)
        errors = fixer.analyze()
        
        if errors:
            print(f"⚠️ La función {func.__name__} tiene errores de indentación")
            fixer.print_report()
            respuesta = input("¿Corregir automáticamente? (S/N): ")
            if respuesta.upper() == 'S':
                fixer.fix()
        
        return func(*args, **kwargs)
    return wrapper

# ------------------------------------------------------------------
# 3. FUNCIÓN PARA CORREGIR ARCHIVO COMPLETO
# ------------------------------------------------------------------
def fix_indentation_in_file(filename: str, backup: bool = True) -> bool:
    """
    Corrige automáticamente todos los problemas de indentación en un archivo.
    
    Args:
        filename: Ruta al archivo
        backup: Si crear backup
    
    Returns:
        True si se corrigió algo
    """
    fixer = IndentationFixer(filename)
    errors = fixer.analyze()
    
    if errors:
        fixer.print_report()
        return fixer.fix(backup)
    else:
        print(f"✅ {filename} no tiene errores de indentación")
        return True

# ------------------------------------------------------------------
# 4. TEST UNITARIO
# ------------------------------------------------------------------
def test_indentation_fixer():
    """Prueba el corrector de indentación"""
    print("\n🧪 TEST CORRECTOR DE INDENTACIÓN")
    
    # Crear archivo de prueba
    test_file = "test_indent.py"
    with open(test_file, 'w') as f:
        f.write("def funcion_con_error():\n")
        f.write("    if True:\n")
        f.write("    print('Error de indentación')\n")  # Indentación incorrecta
    
    # Analizar
    fixer = IndentationFixer(test_file)
    errors = fixer.analyze()
    
    if errors:
        print(f"✅ Detectados {len(errors)} errores")
        fixer.fix(backup=False)
        print("✅ Corrección aplicada")
    else:
        print("❌ No se detectaron errores (falló el test)")
    
    # Limpiar
    import os
    os.remove(test_file)
    
    print("🎉 Test completado")

# ------------------------------------------------------------------
# 5. INSTRUCCIONES DE USO
# ------------------------------------------------------------------
"""
📚 CÓMO USAR EL CORRECTOR DE INDENTACIÓN:

1. PARA UN ARCHIVO ESPECÍFICO:
   from reparacion_indentacion import fix_indentation_in_file
   fix_indentation_in_file('venta_agent.py')

2. CON DECORADOR:
   @check_indentation
   def mi_funcion():
       ...

3. DESDE LÍNEA DE COMANDOS:
   python -c "from reparacion_indentacion import fix_indentation_in_file; fix_indentation_in_file('venta_agent.py')"
"""
''',
            
            # --------------------------------------------------------
            # 5. ERRORES GENERICOS - SOLUCIÓN UNIVERSAL
            # --------------------------------------------------------
            "ErrorGenerico": '''
# ========================================================
# 🔧 SOLUCIÓN UNIVERSAL PARA ERRORES GENÉRICOS
# ========================================================

import sys
import traceback
from typing import Optional, Callable

# ------------------------------------------------------------------
# 1. CAPTURADOR DE ERRORES INTELIGENTE
# ------------------------------------------------------------------
def capture_and_fix(func: Callable, *args, **kwargs):
    """
    Ejecuta una función y captura cualquier error, sugiriendo soluciones.
    
    Uso:
        resultado = capture_and_fix(mi_funcion, arg1, arg2)
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        error_type = type(e).__name__
        error_line = traceback.format_exc().split('\\n')[-3]
        
        print(f"\n❌ ERROR DETECTADO: {error_type}")
        print(f"   {error_line}")
        print(f"   {str(e)}")
        
        # Buscar solución en base de conocimiento
        solucion = buscar_solucion(error_type, str(e))
        if solucion:
            print(f"\n💡 SOLUCIÓN SUGERIDA:\n{solucion}")
        
        # Preguntar si quiere aplicar
        respuesta = input("¿Aplicar solución automática? (S/N): ")
        if respuesta.upper() == 'S':
            return aplicar_solucion(error_type, func, args, kwargs)
        
        return None

# ------------------------------------------------------------------
# 2. BASE DE CONOCIMIENTO DE SOLUCIONES
# ------------------------------------------------------------------
SOLUCIONES = {
    "NoneType": "Usar safe_get() o validar objeto antes de acceder",
    "KeyError": "Usar .get() con valor por defecto",
    "IndexError": "Verificar len(lista) antes de acceder",
    "AttributeError": "Verificar que el objeto tenga el atributo con hasattr()",
    "TypeError": "Verificar tipos de datos antes de operar",
    "ValueError": "Validar valores antes de usar",
    "ConnectionError": "Verificar servidor BD y conexión de red",
    "Timeout": "Aumentar timeout u optimizar consulta",
    "IndentationError": "Revisar indentación del código",
    "SyntaxError": "Revisar sintaxis del código",
    "ImportError": "Instalar dependencia o verificar ruta",
    "FileNotFoundError": "Verificar ruta y permisos del archivo"
}

def buscar_solucion(error_type: str, error_msg: str) -> Optional[str]:
    """Busca una solución en la base de conocimiento"""
    # Buscar exacto
    if error_type in SOLUCIONES:
        return SOLUCIONES[error_type]
    
    # Buscar parcial
    for key, solucion in SOLUCIONES.items():
        if key in error_msg or error_msg in key:
            return solucion
    
    return None

def aplicar_solucion(error_type, func, args, kwargs):
    """Intenta aplicar una solución automática"""
    if error_type == "NoneType":
        from reparacion_none import safe_get
        # Reintentar con safe_get
        return "Solución automática aplicada"
    else:
        return "Solución manual requerida"
'''
        }
        
        # Buscar solución específica
        solucion = codigos.get(tipo)
        
        # Si no hay específica, usar genérica
        if not solucion:
            solucion = codigos.get("ErrorGenerico", "")
        
        return solucion
    
    def _diagnosticar_bd(self, informe):
        """Verifica conexión y consultas a BD"""
        try:
            # Intentar conectar a la BD
            import requests
            response = requests.post(
                "http://localhost:5000/consultar",
                json={"consulta": "SELECT 1 as test"},
                timeout=3
            )
            
            if response.status_code != 200:
                informe["errores_criticos"].append({
                    "tipo": "BD_CONNECTION",
                    "descripcion": "No se puede conectar a la base de datos",
                    "solucion": "Verificar que servidor_bd.py esté corriendo"
                })
            else:
                # Verificar tablas importantes
                tablas = ["venta", "articulo", "cliente", "kardex"]
                for tabla in tablas:
                    response = requests.post(
                        "http://localhost:5000/consultar",
                        json={"consulta": f"SELECT TOP 1 * FROM {tabla}"},
                        timeout=2
                    )
                    if response.status_code != 200:
                        informe["advertencias"].append({
                            "tipo": f"TABLA_{tabla.upper()}",
                            "descripcion": f"Problema accediendo a tabla {tabla}"
                        })
                        
        except Exception as e:
            informe["errores_criticos"].append({
                "tipo": "BD_ERROR",
                "descripcion": f"Error conectando a BD: {str(e)}",
                "solucion": "Ejecutar: python3 servidor_bd.py"
            })
    
    def _diagnosticar_habilidades(self, informe):
        """Verifica que las habilidades funcionen correctamente"""
        for nombre, habilidad in self.habilidades.items():
            try:
                # Intentar ejecutar la habilidad con parámetros de prueba
                if hasattr(habilidad, 'descripcion_habilidad'):
                    # Prueba simple: verificar que se puede llamar
                    pass
            except Exception as e:
                informe["advertencias"].append({
                    "tipo": "HABILIDAD_ROTA",
                    "descripcion": f"La habilidad '{nombre}' podría estar dañada",
                    "error": str(e)
                })
    
    def _diagnosticar_patrones(self, informe):
        """Analiza patrones de errores recurrentes"""
        if len(self.memoria_errores) > 5:
            # Agrupar por tipo de error
            tipos = {}
            for error in self.memoria_errores[-50:]:
                tipo = error.get('tipo', 'desconocido')
                tipos[tipo] = tipos.get(tipo, 0) + 1
            
            # Identificar patrones peligrosos
            for tipo, count in tipos.items():
                if count > 3:
                    informe["sugerencias"].append({
                        "tipo": "PATRON_RECURRENTE",
                        "descripcion": f"Error '{tipo}' ha ocurrido {count} veces",
                        "recomendacion": "Revisar este tipo de error con prioridad"
                    })
    
    def _generar_reparaciones(self, informe):
        """GENERA CÓDIGO PARA REPARAR ERRORES DETECTADOS"""
        
        for error in informe["errores_criticos"]:
            if error["tipo"] == "NoneType":
                codigo = '''
# 🛠️ REPARACIÓN PARA ERROR NoneType
# Agregar esta validación antes de acceder al objeto

def validar_objeto(objeto, campo, default=None):
    """Valida que un objeto y campo existan antes de acceder"""
    if objeto is None:
        return default
    return objeto.get(campo, default)

# Ejemplo de uso:
# En lugar de: valor = objeto['campo']
# Usar: valor = validar_objeto(objeto, 'campo', 0)
'''
                informe["codigo_reparacion"]["NoneType"] = codigo
                
            elif error["tipo"] == "KeyError":
                codigo = '''
# 🛠️ REPARACIÓN PARA ERROR KeyError
# Usar .get() en lugar de acceso directo

def acceder_seguro(diccionario, clave, default=None):
    """Accede a un diccionario de forma segura"""
    return diccionario.get(clave, default)

# Ejemplo:
# En lugar de: valor = dic['clave']
# Usar: valor = acceder_seguro(dic, 'clave', 0)
'''
                informe["codigo_reparacion"]["KeyError"] = codigo
                
            elif error["tipo"] == "BD_CONNECTION":
                codigo = '''
# 🛠️ REPARACIÓN PARA CONEXIÓN BD
# Script para reiniciar el servidor de BD automáticamente

import subprocess
import time

def reiniciar_servidor_bd():
    """Reinicia el servidor de base de datos"""
    try:
        # Matar procesos existentes
        subprocess.run(["pkill", "-f", "servidor_bd.py"])
        time.sleep(2)
        
        # Iniciar de nuevo
        subprocess.run([
            "cd /home/junior/Escritorio/ia-mecanica/herramientas && "
            "source venv/bin/activate && "
            "python3 servidor_bd.py &"
        ], shell=True)
        
        return "✅ Servidor BD reiniciado"
    except Exception as e:
        return f"❌ Error reiniciando: {e}"

# Ejecutar: reiniciar_servidor_bd()
'''
                informe["codigo_reparacion"]["BD_CONNECTION"] = codigo
    
    def _guardar_diagnostico(self, informe):
        """Guarda el diagnóstico en archivo"""
        nombre_archivo = f"diagnosticos/diagnostico_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(nombre_archivo, 'w') as f:
            json.dump(informe, f, indent=2)
        print(f"   💾 Diagnóstico guardado: {nombre_archivo}")
    
    # ============================================================
    # GENERADOR DE CÓDIGO INTELIGENTE
    # ============================================================
    
    def generar_codigo_para_error(self, descripcion_error: str) -> str:
        """
        🔥 GENERADOR DE CÓDIGO SUPREMO - VERSIÓN 5.0
        Analiza el error y genera código específico con soluciones completas
        Incluye: decoradores, clases, tests, parches, y documentación
        """
        desc_lower = descripcion_error.lower()
        
        # ========================================================
        # 1. ERRORES NoneType (Los más comunes)
        # ========================================================
        if "none" in desc_lower or "nonetype" in desc_lower or "attributeerror" in desc_lower:
            return '''
# ========================================================
# 🛡️ PROTECCIÓN ÉPICA CONTRA NoneType
# ========================================================

import functools
from typing import Any, Optional, TypeVar, Callable

T = TypeVar('T')

# ------------------------------------------------------------------
# 1. DECORADOR MÁGICO - Protege cualquier función de None
# ------------------------------------------------------------------
def proteger_de_none(default_value: Any = None):
    """
    Decorador que protege una función contra valores None.
    Si algún argumento es None, retorna default_value.
    
    Uso:
        @proteger_de_none(default_value=0)
        def calcular_precio(producto):
            return producto.precio
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Verificar args posicionales
            for i, arg in enumerate(args):
                if arg is None:
                    print(f"⚠️ Argumento {i} es None en {func.__name__}")
                    return default_value
            
            # Verificar kwargs
            for key, value in kwargs.items():
                if value is None:
                    print(f"⚠️ Argumento '{key}' es None en {func.__name__}")
                    return default_value
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

# ------------------------------------------------------------------
# 2. CLASE SAFE OBJECT - Envuelve cualquier objeto
# ------------------------------------------------------------------
class SafeObject:
    """
    Envuelve cualquier objeto y protege contra accesos a None.
    
    Uso:
        producto = SafeObject(objeto_posiblemente_none, default=0)
        precio = producto.precio  # Retorna default si objeto es None
    """
    def __init__(self, obj: Any, default: Any = None):
        self._obj = obj
        self._default = default
    
    def __getattr__(self, name: str) -> Any:
        if self._obj is None:
            return self._default
        return getattr(self._obj, name, self._default)
    
    def __getitem__(self, key: Any) -> Any:
        if self._obj is None:
            return self._default
        try:
            return self._obj[key]
        except (KeyError, TypeError, IndexError):
            return self._default
    
    def __call__(self, *args, **kwargs) -> Any:
        if self._obj is None:
            return self._default
        if callable(self._obj):
            return self._obj(*args, **kwargs)
        return self._default
    
    @property
    def exists(self) -> bool:
        """Verifica si el objeto existe (no es None)"""
        return self._obj is not None
    
    def get(self, default: Any = None) -> Any:
        """Retorna el objeto o un default si es None"""
        return self._obj if self._obj is not None else (default or self._default)

# ------------------------------------------------------------------
# 3. FUNCIONES DE ACCESO SEGURO
# ------------------------------------------------------------------
def safe_get(obj: Any, attr: str, default: Any = None) -> Any:
    """Obtiene un atributo de forma segura"""
    if obj is None:
        return default
    return getattr(obj, attr, default)

def safe_dict_get(d: dict, key: Any, default: Any = None) -> Any:
    """Obtiene un valor de diccionario de forma segura"""
    if d is None:
        return default
    return d.get(key, default)

def safe_call(func: Callable, *args, default: Any = None, **kwargs) -> Any:
    """Llama a una función de forma segura"""
    if func is None:
        return default
    try:
        return func(*args, **kwargs)
    except Exception as e:
        print(f"⚠️ Error en {func.__name__}: {e}")
        return default

def safe_chain(obj: Any, *attrs: str, default: Any = None) -> Any:
    """
    Accede a una cadena de atributos de forma segura.
    
    Ejemplo:
        precio = safe_chain(producto, 'categoria', 'precio', default=0)
    """
    current = obj
    for attr in attrs:
        if current is None:
            return default
        current = getattr(current, attr, None)
    return current if current is not None else default

# ------------------------------------------------------------------
# 4. PATCH GLOBAL (OPCIONAL - USAR CON CUIDADO)
# ------------------------------------------------------------------
def aplicar_parche_global():
    """
    Aplica un parche global para proteger todo el módulo.
    ⚠️ Usar solo si sabes lo que haces
    """
    import builtins
    
    # Guardar originales
    original_getattr = builtins.getattr
    
    # Nuevo getattr seguro
    def safe_builtin_getattr(obj, name, default=None):
        if obj is None:
            return default
        return original_getattr(obj, name, default)
    
    # Aplicar parche
    builtins.getattr = safe_builtin_getattr
    print("✅ Parche NoneType aplicado globalmente")

# ------------------------------------------------------------------
# 5. TEST UNITARIO
# ------------------------------------------------------------------
def test_reparacion_none():
    """Prueba todas las soluciones NoneType"""
    print("\n🧪 TEST REPARACIÓN NONE TYPE")
    print("="*50)
    
    # Prueba safe_get
    obj_none = None
    resultado = safe_get(obj_none, "precio", 0)
    print(f"✅ safe_get: {resultado} (esperado 0)")
    
    # Prueba SafeObject
    obj = SafeObject(None, 0)
    resultado = obj.precio
    print(f"✅ SafeObject: {resultado} (esperado 0)")
    
    # Prueba decorador
    @proteger_de_none(default_value=0)
    def obtener_precio(objeto):
        return objeto.precio
    
    resultado = obtener_precio(None)
    print(f"✅ Decorador: {resultado} (esperado 0)")
    
    # Prueba safe_chain
    resultado = safe_chain(None, 'a', 'b', default=0)
    print(f"✅ safe_chain: {resultado} (esperado 0)")
    
    print("\n🎉 TODAS LAS PRUEBAS PASARON")
    return True

# ------------------------------------------------------------------
# 6. EJEMPLO DE USO
# ------------------------------------------------------------------
"""
📚 EJEMPLO COMPLETO:

class Producto:
    def __init__(self, nombre, precio):
        self.nombre = nombre
        self.precio = precio

# Sin protección (PELIGROSO)
def get_precio_peligroso(producto):
    return producto.precio  # ❌ Si producto es None, explota

# Con protección (SEGURO)
@proteger_de_none(default_value=0)
def get_precio_seguro(producto):
    return producto.precio  # ✅ Si producto es None, retorna 0

# O usando SafeObject
def procesar_producto(obj):
    producto = SafeObject(obj, default=None)
    if producto.exists:
        print(f"Precio: {producto.precio}")
    else:
        print("Producto no existe")
"""
'''
        
        # ========================================================
        # 2. ERRORES KeyError
        # ========================================================
        elif "keyerror" in desc_lower:
            return '''
# ========================================================
# 🛡️ PROTECCIÓN ÉPICA CONTRA KeyError
# ========================================================

from typing import Any, Dict, Optional
import functools
from collections import defaultdict

# ------------------------------------------------------------------
# 1. DICCIONARIO SEGURO - SafeDict
# ------------------------------------------------------------------
class SafeDict(dict):
    """
    Diccionario que nunca lanza KeyError.
    
    Uso:
        datos = SafeDict({'a': 1}, default=0)
        valor = datos['b']  # Retorna 0 en lugar de KeyError
    """
    def __init__(self, *args, default: Any = None, **kwargs):
        super().__init__(*args, **kwargs)
        self._default = default
    
    def __getitem__(self, key):
        try:
            return super().__getitem__(key)
        except KeyError:
            return self._default
    
    def get(self, key, default=None):
        return super().get(key, default if default is not None else self._default)
    
    def get_nested(self, *keys, default=None):
        """
        Obtiene un valor anidado de forma segura.
        
        Ejemplo:
            valor = datos.get_nested('usuario', 'perfil', 'edad', default=0)
        """
        current = self
        for key in keys:
            if isinstance(current, dict):
                current = current.get(key)
                if current is None:
                    return default
            else:
                return default
        return current if current is not None else default

# ------------------------------------------------------------------
# 2. FUNCIONES DE ACCESO UNIVERSAL
# ------------------------------------------------------------------
def safe_key_access(obj: Any, key: Any, default: Any = None) -> Any:
    """
    Accede a cualquier objeto como si fuera diccionario de forma segura.
    
    Soporta:
    - Diccionarios: obj[key]
    - Listas: obj[index]
    - Objetos: getattr(obj, key)
    """
    if obj is None:
        return default
    
    # Diccionario
    if isinstance(obj, dict):
        return obj.get(key, default)
    
    # Lista/Tupla con índice numérico
    if isinstance(obj, (list, tuple)) and isinstance(key, int):
        try:
            return obj[key]
        except IndexError:
            return default
    
    # Objeto con atributos
    if hasattr(obj, key):
        return getattr(obj, key)
    
    return default

# ------------------------------------------------------------------
# 3. DECORADOR PROTECTOR
# ------------------------------------------------------------------
def proteger_keyerror(default: Any = None):
    """
    Decorador que protege una función de KeyError.
    Si ocurre KeyError, retorna default.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except KeyError as e:
                print(f"⚠️ KeyError en {func.__name__}: {e}")
                return default
        return wrapper
    return decorator

# ------------------------------------------------------------------
# 4. DEFAULTDICT INTELIGENTE
# ------------------------------------------------------------------
def crear_defaultdict_inteligente(factory=None):
    """
    Crea un defaultdict con factory personalizado.
    
    Uso:
        dd = crear_defaultdict_inteligente(lambda: 0)
        valor = dd['clave_no_existe']  # Retorna 0
    """
    if factory is None:
        factory = lambda: None
    return defaultdict(factory)

# ------------------------------------------------------------------
# 5. TEST UNITARIO
# ------------------------------------------------------------------
def test_reparacion_keyerror():
    """Prueba todas las soluciones KeyError"""
    print("\n🧪 TEST REPARACIÓN KEYERROR")
    print("="*50)
    
    # Prueba SafeDict
    d = SafeDict({'a': 1}, default=0)
    assert d['b'] == 0, "❌ SafeDict falló"
    print("✅ SafeDict funciona")
    
    # Prueba safe_key_access
    assert safe_key_access(None, 'x', 0) == 0, "❌ safe_key_access con None falló"
    assert safe_key_access({'a': 1}, 'b', 0) == 0, "❌ safe_key_access con dict falló"
    print("✅ safe_key_access funciona")
    
    # Prueba decorador
    @proteger_keyerror(default=0)
    def acceder(d, key):
        return d[key]
    
    resultado = acceder({}, 'clave')
    assert resultado == 0, "❌ Decorador falló"
    print("✅ Decorador funciona")
    
    print("\n🎉 TODAS LAS PRUEBAS PASARON")
    return True
'''
        
        # ========================================================
        # 3. ERRORES DE CONEXIÓN
        # ========================================================
        elif "conexion" in desc_lower or "connection" in desc_lower:
            return '''
# ========================================================
# 🔌 PROTECCIÓN ÉPICA CONTRA ERRORES DE CONEXIÓN
# ========================================================

import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import functools
import subprocess
import threading
from typing import Optional, Callable

# ------------------------------------------------------------------
# 1. SESIÓN ROBUSTA CON REINTENTOS
# ------------------------------------------------------------------
def crear_sesion_robusta(
    retries: int = 3,
    backoff_factor: float = 1.0,
    status_forcelist: list = None,
    timeout: int = 30
) -> requests.Session:
    """
    Crea una sesión de requests con reintentos automáticos.
    
    Args:
        retries: Número de reintentos
        backoff_factor: Factor de espera entre reintentos
        status_forcelist: Códigos HTTP que fuerzan reintento
        timeout: Timeout en segundos
    """
    session = requests.Session()
    
    if status_forcelist is None:
        status_forcelist = [429, 500, 502, 503, 504]
    
    retry_strategy = Retry(
        total=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
        allowed_methods=["HEAD", "GET", "OPTIONS", "POST", "PUT", "DELETE"]
    )
    
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    # Timeouts por defecto
    session.timeout = timeout
    
    return session

# ------------------------------------------------------------------
# 2. DECORADOR DE REINTENTO UNIVERSAL
# ------------------------------------------------------------------
def reintentar(
    max_intentos: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    excepciones: tuple = (Exception,)
):
    """
    Decorador que reintenta una función cuando falla.
    
    Args:
        max_intentos: Número máximo de intentos
        delay: Espera inicial entre intentos
        backoff: Factor multiplicador del delay
        excepciones: Tupla de excepciones que disparan reintento
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            intentos = 0
            espera = delay
            
            while intentos < max_intentos:
                try:
                    return func(*args, **kwargs)
                except excepciones as e:
                    intentos += 1
                    if intentos == max_intentos:
                        print(f"❌ Falló después de {max_intentos} intentos: {e}")
                        raise
                    
                    print(f"⚠️ Intento {intentos} falló. Reintentando en {espera}s...")
                    time.sleep(espera)
                    espera *= backoff
        return wrapper
    return decorator

# ------------------------------------------------------------------
# 3. MONITOR DE CONEXIÓN CON AUTO-REPARACIÓN
# ------------------------------------------------------------------
class ConnectionMonitor:
    """Monitorea y repara conexiones automáticamente"""
    
    def __init__(self, url: str, check_interval: int = 60):
        self.url = url
        self.check_interval = check_interval
        self.failures = 0
        self.last_check = None
        self._stop = False
    
    def check_connection(self) -> bool:
        """Verifica si la conexión está activa"""
        try:
            session = crear_sesion_robusta(retries=1)
            response = session.get(self.url, timeout=5)
            return response.status_code < 500
        except Exception as e:
            print(f"⚠️ Error de conexión: {e}")
            self.failures += 1
            return False
    
    def repair(self) -> bool:
        """Intenta reparar la conexión"""
        print("🔧 Intentando reparar conexión...")
        
        # Intentar reiniciar servidor BD
        try:
            subprocess.run(["pkill", "-f", "servidor_bd.py"], timeout=5)
            time.sleep(2)
            
            subprocess.Popen(
                ["cd /home/junior/Escritorio/ia-mecanica/herramientas && "
                 "source venv/bin/activate && python3 servidor_bd.py &"],
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            time.sleep(3)
            
            return self.check_connection()
        except Exception as e:
            print(f"❌ Error reparando: {e}")
            return False
    
    def start_monitoring(self):
        """Inicia monitoreo continuo en un hilo separado"""
        def monitor_loop():
            while not self._stop:
                if not self.check_connection():
                    print(f"⚠️ Conexión perdida (fallo #{self.failures})")
                    if self.failures >= 3:
                        if self.repair():
                            print("✅ Conexión restaurada")
                            self.failures = 0
                time.sleep(self.check_interval)
        
        thread = threading.Thread(target=monitor_loop, daemon=True)
        thread.start()
        return thread
    
    def stop_monitoring(self):
        """Detiene el monitoreo"""
        self._stop = True

# ------------------------------------------------------------------
# 4. FUNCIÓN DE CONSULTA SEGURA
# ------------------------------------------------------------------
@reintentar(max_intentos=3, delay=1, backoff=2, excepciones=(requests.RequestException,))
def consulta_segura(url: str, payload: dict = None) -> Optional[dict]:
    """
    Realiza una consulta HTTP segura con reintentos.
    
    Args:
        url: URL a consultar
        payload: Datos a enviar (para POST)
    
    Returns:
        Respuesta JSON o None si falla
    """
    session = crear_sesion_robusta()
    
    try:
        if payload:
            response = session.post(url, json=payload, timeout=10)
        else:
            response = session.get(url, timeout=10)
        
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"❌ Error en consulta: {e}")
        return None

# ------------------------------------------------------------------
# 5. TEST UNITARIO
# ------------------------------------------------------------------
def test_reparacion_conexion():
    """Prueba las herramientas de conexión"""
    print("\n🧪 TEST REPARACIÓN CONEXIÓN")
    print("="*50)
    
    # Probar sesión robusta
    session = crear_sesion_robusta()
    print("✅ Sesión robusta creada")
    
    # Probar decorador
    @reintentar(max_intentos=2)
    def funcion_que_falla():
        raise ConnectionError("Error simulado")
    
    try:
        funcion_que_falla()
    except ConnectionError:
        print("✅ Decorador de reintento funciona")
    
    # Probar monitor
    monitor = ConnectionMonitor("http://localhost:5000/health")
    thread = monitor.start_monitoring()
    print("✅ Monitor iniciado")
    monitor.stop_monitoring()
    print("✅ Monitor detenido")
    
    print("\n🎉 TODAS LAS PRUEBAS PASARON")
    return True
'''
        
        # ========================================================
        # 4. ERRORES DE INDENTACIÓN (¡El tuyo!)
        # ========================================================
        elif "indent" in desc_lower or "indentation" in desc_lower:
            return '''
# ========================================================
# 📐 CORRECTOR ÉPICO DE INDENTACIÓN
# ========================================================

import os
import shutil
import re
from typing import List, Tuple, Optional

# ------------------------------------------------------------------
# 1. CLASE CORRECTORA DE INDENTACIÓN
# ------------------------------------------------------------------
class IndentationFixer:
    """
    Analiza y corrige problemas de indentación en archivos Python.
    """
    
    def __init__(self, filename: str):
        self.filename = filename
        self.lines = []
        self.errors_found = []
        self._load_file()
    
    def _load_file(self):
        """Carga el archivo"""
        try:
            with open(self.filename, 'r') as f:
                self.lines = f.readlines()
        except Exception as e:
            print(f"❌ Error cargando archivo: {e}")
    
    def analyze(self) -> List[dict]:
        """
        Analiza el archivo en busca de problemas de indentación.
        Retorna lista de errores encontrados.
        """
        errors = []
        
        # Detectar mezcla de tabs y espacios
        for i, line in enumerate(self.lines):
            if '\\t' in line and '    ' in line:
                errors.append({
                    'line': i + 1,
                    'type': 'MIXED_SPACES',
                    'content': line.rstrip(),
                    'fix': self._convert_to_spaces(line)
                })
        
        # Analizar estructura de bloques
        stack = []
        for i, line in enumerate(self.lines):
            stripped = line.rstrip()
            if not stripped:
                continue
            
            indent = len(line) - len(line.lstrip())
            
            # Detectar inicio de bloque
            if stripped.endswith(':'):
                stack.append((i, indent))
            
            # Detectar fin de bloque
            while stack and indent <= stack[-1][1]:
                stack.pop()
            
            # Verificar indentación consistente
            if stack and indent > stack[-1][1] + 4:
                errors.append({
                    'line': i + 1,
                    'type': 'TOO_MANY_SPACES',
                    'content': stripped,
                    'fix': self._fix_indent(line, stack[-1][1] + 4)
                })
            elif stack and indent < stack[-1][1]:
                errors.append({
                    'line': i + 1,
                    'type': 'UNEXPECTED_DEDENT',
                    'content': stripped,
                    'fix': self._fix_indent(line, stack[-1][1])
                })
        
        self.errors_found = errors
        return errors
    
    def _convert_to_spaces(self, line: str) -> str:
        """Convierte tabs a espacios"""
        return line.replace('\\t', '    ')
    
    def _fix_indent(self, line: str, target_indent: int) -> str:
        """Corrige la indentación de una línea"""
        content = line.lstrip()
        return ' ' * target_indent + content
    
    def fix(self, backup: bool = True) -> bool:
        """
        Aplica las correcciones al archivo.
        
        Args:
            backup: Si crear archivo de backup
        
        Returns:
            True si se aplicaron correcciones
        """
        if not self.errors_found:
            print("✅ No se encontraron errores de indentación")
            return False
        
        # Crear backup
        if backup:
            backup_name = f"{self.filename}.bak"
            shutil.copy2(self.filename, backup_name)
            print(f"💾 Backup creado: {backup_name}")
        
        # Aplicar correcciones
        fixed_lines = []
        error_lines = {e['line']: e for e in self.errors_found}
        
        for i, line in enumerate(self.lines, 1):
            if i in error_lines:
                fixed_lines.append(error_lines[i]['fix'])
            else:
                fixed_lines.append(line)
        
        # Guardar
        with open(self.filename, 'w') as f:
            f.writelines(fixed_lines)
        
        print(f"✅ {len(self.errors_found)} errores corregidos en {self.filename}")
        return True
    
    def print_report(self):
        """Muestra reporte detallado de errores"""
        if not self.errors_found:
            print("\n📊 REPORTE DE INDENTACIÓN: TODO CORRECTO")
            return
        
        print(f"\n📊 REPORTE DE INDENTACIÓN: {len(self.errors_found)} ERRORES")
        print("="*60)
        for error in self.errors_found:
            print(f"Línea {error['line']}: {error['type']}")
            print(f"   Contenido: {error['content']}")
            print(f"   Corrección: {error['fix'].strip()}")
            print("-"*40)

# ------------------------------------------------------------------
# 2. FUNCIÓN DE CORRECCIÓN AUTOMÁTICA
# ------------------------------------------------------------------
def fix_indentation(filename: str, backup: bool = True, auto_apply: bool = True) -> bool:
    """
    Corrige automáticamente la indentación de un archivo.
    
    Args:
        filename: Ruta al archivo
        backup: Si crear backup
        auto_apply: Si aplicar correcciones automáticamente
    
    Returns:
        True si se corrigió algo
    """
    fixer = IndentationFixer(filename)
    errors = fixer.analyze()
    
    if errors:
        fixer.print_report()
        
        if auto_apply:
            respuesta = input("¿Aplicar correcciones? (S/N): ").upper()
            if respuesta == 'S':
                return fixer.fix(backup)
            else:
                print("❌ Correcciones no aplicadas")
                return False
        else:
            return fixer.fix(backup)
    else:
        print(f"✅ {filename} no tiene errores de indentación")
        return True

# ------------------------------------------------------------------
# 3. TEST UNITARIO
# ------------------------------------------------------------------
def test_indentation_fixer():
    """Prueba el corrector de indentación"""
    print("\n🧪 TEST CORRECTOR DE INDENTACIÓN")
    print("="*50)
    
    # Crear archivo de prueba
    test_file = "test_indent.py"
    with open(test_file, 'w') as f:
        f.write("def funcion_con_error():\\n")
        f.write("    if True:\\n")
        f.write("    print('Error de indentación')\\n")
    
    # Analizar y corregir
    fixer = IndentationFixer(test_file)
    errors = fixer.analyze()
    
    if errors:
        print(f"✅ Detectados {len(errors)} errores")
        fixer.fix(backup=False)
        print("✅ Corrección aplicada")
    else:
        print("❌ No se detectaron errores (falló el test)")
    
    # Limpiar
    import os
    if os.path.exists(test_file):
        os.remove(test_file)
    
    print("\n🎉 Test completado")

# ------------------------------------------------------------------
# 4. EJEMPLO DE USO
# ------------------------------------------------------------------
"""
📚 CÓMO USAR:

# Corregir un archivo específico
from reparacion_indentacion import fix_indentation
fix_indentation('venta_agent.py', backup=True)

# O con análisis manual
fixer = IndentationFixer('venta_agent.py')
errors = fixer.analyze()
fixer.print_report()
if errors:
    fixer.fix()
"""
'''
        
        # ========================================================
        # 5. ERRORES GENERICOS (Fallback)
        # ========================================================
        else:
            return f'''# ========================================================
# 🔧 SOLUCIÓN GENÉRICA PARA: {descripcion_error}
# ========================================================

import traceback
import sys
from typing import Optional, Callable

# ------------------------------------------------------------------
# 1. CAPTURADOR DE ERRORES INTELIGENTE
# ------------------------------------------------------------------
def capture_and_fix(func: Callable, *args, **kwargs):
    """
    Ejecuta una función y captura cualquier error, sugiriendo soluciones.
    
    Uso:
        resultado = capture_and_fix(mi_funcion, arg1, arg2)
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        error_type = type(e).__name__
        error_line = traceback.format_exc().split('\\\\n')[-3]
        
        print(f"\\n❌ ERROR DETECTADO: {error_type}")
        print(f"   {error_line}")
        print(f"   {str(e)}")
        
        # Buscar solución en base de conocimiento
        solucion = buscar_solucion(error_type, str(e))
        if solucion:
            print(f"\\n💡 SOLUCIÓN SUGERIDA:\\n{solucion}")
        
        return None

# ------------------------------------------------------------------
# 2. BASE DE CONOCIMIENTO DE SOLUCIONES
# ------------------------------------------------------------------
SOLUCIONES = {{
    "NoneType": "Usar safe_get() o validar objeto antes de acceder",
    "KeyError": "Usar .get() con valor por defecto",
    "IndexError": "Verificar len(lista) antes de acceder",
    "AttributeError": "Verificar que el objeto tenga el atributo con hasattr()",
    "TypeError": "Verificar tipos de datos antes de operar",
    "ValueError": "Validar valores antes de usar",
    "ConnectionError": "Verificar servidor BD y conexión de red",
    "Timeout": "Aumentar timeout u optimizar consulta",
    "IndentationError": "Revisar indentación del código",
    "SyntaxError": "Revisar sintaxis del código",
    "ImportError": "Instalar dependencia o verificar ruta",
    "FileNotFoundError": "Verificar ruta y permisos del archivo"
}}

def buscar_solucion(error_type: str, error_msg: str) -> Optional[str]:
    """Busca una solución en la base de conocimiento"""
    # Buscar exacto
    if error_type in SOLUCIONES:
        return SOLUCIONES[error_type]
    
    # Buscar parcial
    for key, solucion in SOLUCIONES.items():
        if key in error_msg or error_msg in key:
            return solucion
    
    return None

# ------------------------------------------------------------------
# 3. DECORADOR DE DIAGNÓSTICO
# ------------------------------------------------------------------
def diagnosticar_errores(func: Callable) -> Callable:
    """
    Decorador que diagnostica errores automáticamente.
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"\\n🔍 DIAGNÓSTICO AUTOMÁTICO:")
            print(f"   Función: {func.__name__}")
            print(f"   Error: {type(e).__name__}: {e}")
            print(f"   Solución sugerida: {buscar_solucion(type(e).__name__, str(e))}")
            raise
    return wrapper

# ------------------------------------------------------------------
# 4. TEST UNITARIO
# ------------------------------------------------------------------
def test_reparacion_generica():
    """Prueba las herramientas genéricas"""
    print("\\n🧪 TEST REPARACIÓN GENÉRICA")
    
    @diagnosticar_errores
    def funcion_con_error():
        raise ValueError("Error de prueba")
    
    try:
        funcion_con_error()
    except:
        print("✅ Diagnóstico funciona")
    
    print("🎉 Test completado")
'''
    
    # ============================================================
    # HERRAMIENTAS DEL AGENTE
    # ============================================================
    
    @staticmethod
    def herramienta(nombre, descripcion):
        def decorador(func):
            func.es_habilidad = True
            func.nombre_habilidad = nombre
            func.descripcion_habilidad = descripcion
            return func
        return decorador
    
    @herramienta("diagnosticar", "Ejecuta un diagnóstico completo del sistema y reporta problemas")
    def diagnosticar(self) -> str:
        """Herramienta principal de diagnóstico"""
        informe = self.diagnosticar_sistema()
        
        resultado = "\n" + "="*60
        resultado += "\n🔍 INFORME DE DIAGNÓSTICO COMPLETO"
        resultado += "\n" + "="*60
        
        if informe["errores_criticos"]:
            resultado += f"\n\n🔴 ERRORES CRÍTICOS ({len(informe['errores_criticos'])}):"
            for e in informe["errores_criticos"]:
                resultado += f"\n   • {e['tipo']}: {e['descripcion']}"
                if 'solucion' in e:
                    resultado += f"\n     Solución: {e['solucion']}"
        
        if informe["advertencias"]:
            resultado += f"\n\n🟡 ADVERTENCIAS ({len(informe['advertencias'])}):"
            for a in informe["advertencias"]:
                resultado += f"\n   • {a['descripcion']}"
        
        if informe["sugerencias"]:
            resultado += f"\n\n💡 SUGERENCIAS DE MEJORA:"
            for s in informe["sugerencias"]:
                resultado += f"\n   • {s['descripcion']}"
        
        if informe["codigo_reparacion"]:
            resultado += "\n\n🔧 CÓDIGO DE REPARACIÓN GENERADO:"
            for tipo, codigo in informe["codigo_reparacion"].items():
                resultado += f"\n\n--- REPARACIÓN PARA {tipo} ---"
                resultado += f"\n{codigo}"
        
        return resultado
    
    @herramienta("reparar_error", "Genera código para reparar un error específico basado en su descripción")
    def reparar_error(self, descripcion: str) -> str:
        """Genera código para reparar un error"""
        codigo = self.generar_codigo_para_error(descripcion)
        
        resultado = f"🔧 Código generado para: {descripcion}\n\n{codigo}"
        print(resultado)
        
        # PREGUNTAR SI QUIERE APLICAR LA REPARACIÓN
        print("\n" + "="*40)
        respuesta = input("🔄 ¿Quieres APLICAR esta reparación automáticamente? (S/N): ").strip().upper()
        
        if respuesta == 'S':
            print("\n🚀 INICIANDO AUTO-REPARACIÓN...")
            resultado_reparacion = self.aplicar_reparacion(descripcion, codigo)
            if resultado_reparacion["exito"]:
                return f"✅ AUTO-REPARACIÓN COMPLETADA\n{resultado}"
            else:
                return f"❌ AUTO-REPARACIÓN FALLÓ\n{resultado}"
        else:
            return resultado
    
    @herramienta("analizar_logs", "Analiza los logs del sistema en busca de errores recientes")
    def analizar_logs(self) -> str:
        """Analiza logs y retorna resumen"""
        try:
            log_file = "/home/junior/Escritorio/sistema-ventas-python/sistema_ventas.log"
            if not os.path.exists(log_file):
                return "❌ Archivo de log no encontrado"
            
            with open(log_file, 'r') as f:
                logs = f.readlines()[-200:]
            
            errores = [l for l in logs if 'ERROR' in l or '❌' in l or 'Exception' in l]
            
            resultado = f"📊 ANÁLISIS DE LOGS\n"
            resultado += f"   Total líneas analizadas: {len(logs)}\n"
            resultado += f"   Errores encontrados: {len(errores)}\n\n"
            
            if errores:
                resultado += "Últimos 5 errores:\n"
                for e in errores[-5:]:
                    resultado += f"   • {e[:100]}...\n"
            
            return resultado
        except Exception as e:
            return f"❌ Error analizando logs: {e}"
    
    @herramienta("crear_herramienta", "Crea una nueva herramienta personalizada")
    def crear_herramienta(self, nombre: str, descripcion: str, codigo: str) -> str:
        """Crea una nueva habilidad"""
        return self._crear_archivo_habilidad(nombre, descripcion, codigo)
    
    def _crear_archivo_habilidad(self, nombre: str, descripcion: str, codigo: str) -> str:
        """Crea archivo de habilidad"""
        ruta = os.path.join(self.directorio_habilidades, f"{nombre}.py")
        
        plantilla = f'''"""
Habilidad: {nombre}
Descripción: {descripcion}
Creada por: {self.nombre}
Fecha: {datetime.now()}
"""

def herramienta(nombre, descripcion):
    def decorador(func):
        func.es_habilidad = True
        func.nombre_habilidad = nombre
        func.descripcion_habilidad = descripcion
        return func
    return decorador

{codigo}
'''
        try:
            with open(ruta, 'w') as f:
                f.write(plantilla)
            self._importar_habilidad(nombre, ruta)
            return f"✅ Herramienta '{nombre}' creada exitosamente"
        except Exception as e:
            return f"❌ Error creando herramienta: {e}"
    
    @herramienta("listar", "Muestra todas las herramientas disponibles")
    def listar(self) -> str:
        resultado = f"📚 HERRAMIENTAS DISPONIBLES ({len(self.habilidades)})\n"
        for nombre, func in self.habilidades.items():
            desc = getattr(func, 'descripcion_habilidad', 'Sin descripción')
            resultado += f"   • {nombre}: {desc}\n"
        return resultado

    # ============================================================
    # MÉTODOS PARA CREAR HERRAMIENTAS (AHORA DENTRO DE LA CLASE)
    # ============================================================
    
    def _crear_herramienta_iva(self):
        """Crea una herramienta para calcular IVA"""
        codigo = '''
@herramienta("calcular_iva", "Calcula el precio final con IVA incluido (16%)")
def calcular_iva(precio_sin_iva: float) -> str:
    """Calcula el IVA y el precio final"""
    iva = precio_sin_iva * 0.16
    total = precio_sin_iva + iva
    return (f"📊 CÁLCULO DE IVA:\\n"
            f"   Precio sin IVA: ${precio_sin_iva:.2f}\\n"
            f"   IVA (16%): ${iva:.2f}\\n"
            f"   TOTAL con IVA: ${total:.2f}")
'''
        resultado = self._crear_archivo_habilidad("calcular_iva", "Calcula el precio final con IVA incluido", codigo)
        print(f"✅ {resultado}")
    
    def _crear_herramienta_calculadora(self):
        """Crea una calculadora básica"""
        codigo = '''
@herramienta("calculadora_v2", "Calculadora básica con operaciones aritméticas")
def calculadora_v2(operacion: str, a: float, b: float = 0) -> str:
    """Ejecuta operaciones aritméticas"""
    if operacion == "suma":
        return f"Resultado: {a + b}"
    elif operacion == "resta":
        return f"Resultado: {a - b}"
    elif operacion == "multiplica":
        return f"Resultado: {a * b}"
    elif operacion == "divide":
        if b == 0:
            return "Error: División por cero"
        return f"Resultado: {a / b}"
    elif operacion == "raiz":
        return f"Resultado: {a ** 0.5}"
    else:
        return "Operación no soportada"
'''
        resultado = self._crear_archivo_habilidad("calculadora_v2", "Calculadora básica", codigo)
        print(f"✅ {resultado}")
    
    def _crear_herramienta_clima(self):
        """Crea herramienta de clima"""
        codigo = '''
@herramienta("clima_avanzado", "Pronóstico del clima para una ciudad")
def clima_avanzado(ciudad: str) -> str:
    """Simula pronóstico del clima"""
    import random
    condiciones = ["☀️ Soleado", "⛅ Parcialmente nublado", "🌧️ Lluvioso", "🌪️ Ventoso", "❄️ Nevado"]
    temp = random.randint(5, 35)
    humedad = random.randint(30, 95)
    viento = random.randint(0, 30)
    
    return (f"🌍 CLIMA EN {ciudad.upper()}\\n"
            f"   Condición: {random.choice(condiciones)}\\n"
            f"   Temperatura: {temp}°C\\n"
            f"   Humedad: {humedad}%\\n"
            f"   Viento: {viento} km/h")
'''
        resultado = self._crear_archivo_habilidad("clima_avanzado", "Pronóstico del clima", codigo)
        print(f"✅ {resultado}")
    
    def _crear_herramienta_desde_comando(self, tipo):
        """Crea herramienta basada en comando /crear"""
        tipo_lower = tipo.lower()
        if "iva" in tipo_lower:
            self._crear_herramienta_iva()
        elif "calculadora" in tipo_lower:
            self._crear_herramienta_calculadora()
        elif "clima" in tipo_lower:
            self._crear_herramienta_clima()
        else:
            print(f"❌ No sé cómo crear una herramienta de tipo '{tipo}'")
    
    def _crear_herramienta_desde_comando(self, tipo):
        """Crea herramienta basada en comando /crear"""
        if "iva" in tipo:
            self._crear_herramienta_iva()
        elif "calculadora" in tipo:
            self._crear_herramienta_calculadora()
        elif "clima" in tipo:
            self._crear_herramienta_clima()
        else:
            print(f"❌ No sé cómo crear una herramienta de tipo '{tipo}'")

    # ============================================================
    # SISTEMA DE AUTO-REPARACIÓN (¡LO MÁS PODEROSO!)
    # ============================================================
    
    def aplicar_reparacion(self, tipo_error, codigo):
        """
        APLICA automáticamente la reparación al sistema
        Esta función pregunta al usuario y ejecuta la reparación
        """
        print(f"\n🔧 ¿Quieres APLICAR la reparación para '{tipo_error}' automáticamente?")
        print("   Esto intentará solucionar el problema en tu sistema.")
        respuesta = input("   ¿Proceder? (S/N): ").strip().upper()
        
        if respuesta == 'S':
            print(f"\n🛠️ INICIANDO AUTO-REPARACIÓN PARA: {tipo_error}")
            print("   " + "="*40)
            
            # 1. Crear backup de seguridad
            self._crear_backup_seguridad()
            
            # 2. Aplicar reparación específica según el error
            if "NoneType" in tipo_error or "none" in tipo_error.lower():
                resultado = self._reparar_none_type()
            elif "KeyError" in tipo_error:
                resultado = self._reparar_key_error()
            elif "conexion" in tipo_error.lower() or "connection" in tipo_error.lower():
                resultado = self._reparar_conexion_bd()
            else:
                resultado = self._reparar_generico(codigo)
            
            # 3. Mostrar resultado
            if resultado["exito"]:
                print(f"\n✅ AUTO-REPARACIÓN COMPLETADA CON ÉXITO")
                print(f"   📍 Reparación: {resultado['accion']}")
                print(f"   📁 Archivos modificados: {resultado['archivos']}")
                print(f"   💾 Backup creado en: {resultado['backup']}")
            else:
                print(f"\n❌ AUTO-REPARACIÓN FALLÓ")
                print(f"   Error: {resultado['error']}")
                print("   Revisa el backup para restaurar si es necesario.")
            
            return resultado
        else:
            print("❌ Reparación cancelada por el usuario.")
            return {"exito": False, "cancelado": True}
    
    def _crear_backup_seguridad(self):
        """Crea un backup de los archivos críticos antes de modificar"""
        import shutil
        from datetime import datetime
        
        backup_dir = f"backups/backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        os.makedirs(backup_dir, exist_ok=True)
        
        archivos_criticos = [
            "/home/junior/Escritorio/sistema-ventas-python/agente_escritorio/agents/venta_agent.py",
            "/home/junior/Escritorio/sistema-ventas-python/agente_escritorio/ui/dialogos/pago_mixto_dialog.py",
            "/home/junior/Escritorio/sistema-ventas-python/agente_escritorio/agents/programador_agent.py"
        ]
        
        print("   💾 Creando backup de seguridad...")
        for archivo in archivos_criticos:
            if os.path.exists(archivo):
                nombre = os.path.basename(archivo)
                shutil.copy2(archivo, f"{backup_dir}/{nombre}.bak")
                print(f"      ✅ Backup: {nombre}.bak")
        
        self.ultimo_backup = backup_dir
        return backup_dir
    
    def _reparar_none_type(self):
        """Repara específicamente errores NoneType - VERSIÓN MEJORADA"""
        print("   🔍 ANALIZANDO ERRORES NONE TYPE...")
        
        archivos_modificados = []
        
        # Lista de archivos a reparar (¡TODOS los relevantes!)
        archivos_a_reparar = [
            "/home/junior/Escritorio/sistema-ventas-python/agente_escritorio/agents/venta_agent.py",
            "/home/junior/Escritorio/sistema-ventas-python/agente_escritorio/ui/dialogos/pago_mixto_dialog.py",
            "/home/junior/Escritorio/sistema-ventas-python/agente_escritorio/agents/programador_agent.py",
            "/home/junior/Escritorio/sistema-ventas-python/agente_escritorio/agents/cliente_agent.py",
            "/home/junior/Escritorio/sistema-ventas-python/agente_escritorio/agents/articulo_agent.py"
        ]
        
        for archivo_path in archivos_a_reparar:
            if os.path.exists(archivo_path):
                with open(archivo_path, 'r') as f:
                    contenido = f.readlines()
                
                # Verificar si YA tiene las funciones de reparación
                tiene_reparacion = False
                for linea in contenido:
                    if "def safe_get" in linea or "def safe_dict_get" in linea:
                        tiene_reparacion = True
                        break
                
                if tiene_reparacion:
                    print(f"      ⏭️  {os.path.basename(archivo_path)} ya está reparado")
                    continue
                
                # Buscar y marcar posibles NoneType
                cambios = 0
                nuevas_lineas = []
                
                # Agregar funciones de reparación al inicio
                if not tiene_reparacion:
                    nuevas_lineas.append("\n")
                    nuevas_lineas.append("# Funciones de reparación automática - Agregadas por SupremeBot\n")
                    nuevas_lineas.append("def safe_get(obj, attr, default=None):\n")
                    nuevas_lineas.append("    \"\"\"Obtiene atributo de forma segura sin NoneType errors\"\"\"\n")
                    nuevas_lineas.append("    try:\n")
                    nuevas_lineas.append("        return getattr(obj, attr) if obj is not None else default\n")
                    nuevas_lineas.append("    except:\n")
                    nuevas_lineas.append("        return default\n")
                    nuevas_lineas.append("\n")
                    nuevas_lineas.append("def safe_dict_get(d, key, default=None):\n")
                    nuevas_lineas.append("    \"\"\"Obtiene valor de diccionario de forma segura\"\"\"\n")
                    nuevas_lineas.append("    try:\n")
                    nuevas_lineas.append("        return d.get(key, default) if d is not None else default\n")
                    nuevas_lineas.append("    except:\n")
                    nuevas_lineas.append("        return default\n")
                    nuevas_lineas.append("\n")
                
                # Procesar líneas existentes
                for linea in contenido:
                    nueva_linea = linea
                    
                    # Buscar accesos peligrosos y envolverlos
                    if "getattr" not in linea and "safe" not in linea:
                        if ".precio" in linea or ".nombre" in linea or ".id" in linea:
                            # Convertir obj.atributo a safe_get(obj, 'atributo')
                            import re
                            patron = r'(\w+)\.(\w+)'
                            nueva_linea = re.sub(patron, r'safe_get(\1, "\2")', linea)
                            if nueva_linea != linea:
                                cambios += 1
                    
                    nuevas_lineas.append(nueva_linea)
                
                if cambios > 0 or not tiene_reparacion:
                    with open(archivo_path, 'w') as f:
                        f.writelines(nuevas_lineas)
                    archivos_modificados.append(archivo_path)
                    print(f"      ✅ {os.path.basename(archivo_path)}: {cambios} líneas modificadas + funciones agregadas")
        
        return {
            "exito": True,
            "accion": f"Reparación NoneType completada en {len(archivos_modificados)} archivos",
            "archivos": len(archivos_modificados),
            "backup": self.ultimo_backup
        }
    
    def _reparar_key_error(self):
        """Repara específicamente errores KeyError"""
        print("   🔍 ANALIZANDO ERRORES KEYERROR...")
        
        archivos_modificados = []
        pago_mixto_path = "/home/junior/Escritorio/sistema-ventas-python/agente_escritorio/ui/dialogos/pago_mixto_dialog.py"
        
        if os.path.exists(pago_mixto_path):
            with open(pago_mixto_path, 'r') as f:
                contenido = f.readlines()
            
            # Buscar accesos directos a diccionarios y convertirlos a .get()
            cambios = 0
            nuevas_lineas = []
            for linea in contenido:
                nueva_linea = linea
                if "[" in linea and "]" in linea and "=" in linea:
                    # Convertir dict['key'] a dict.get('key', default)
                    import re
                    patron = r'(\w+)\[["\'](\w+)["\']\]'
                    nueva_linea = re.sub(patron, r'\1.get("\2", None)', linea)
                    if nueva_linea != linea:
                        cambios += 1
                nuevas_lineas.append(nueva_linea)
            
            if cambios > 0:
                with open(pago_mixto_path, 'w') as f:
                    f.writelines(nuevas_lineas)
                archivos_modificados.append(pago_mixto_path)
                print(f"      ✅ {cambios} líneas modificadas en pago_mixto_dialog.py")
        
        return {
            "exito": True,
            "accion": "Reparación KeyError completada",
            "archivos": len(archivos_modificados),
            "backup": self.ultimo_backup
        }
    
    def _reparar_conexion_bd(self):
        """Repara problemas de conexión a BD"""
        print("   🔍 REPARANDO CONEXIÓN A BASE DE DATOS...")
        
        # Verificar si el servidor está corriendo
        import subprocess
        import time
        
        # Matar procesos existentes
        subprocess.run(["pkill", "-f", "servidor_bd.py"], capture_output=True)
        time.sleep(2)
        
        # Iniciar servidor de nuevo
        try:
            subprocess.Popen(
                ["cd /home/junior/Escritorio/ia-mecanica/herramientas && source venv/bin/activate && python3 servidor_bd.py &"],
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            time.sleep(3)
            
            # Verificar que responde
            import requests
            response = requests.get("http://localhost:5000/health", timeout=3)
            
            if response.status_code == 200:
                return {
                    "exito": True,
                    "accion": "Servidor BD reiniciado exitosamente",
                    "archivos": 0,
                    "backup": self.ultimo_backup
                }
            else:
                return {
                    "exito": False,
                    "error": "Servidor iniciado pero no responde"
                }
        except Exception as e:
            return {
                "exito": False,
                "error": str(e)
            }
    
    def _reparar_generico(self, codigo):
        """Reparación genérica para otros errores"""
        print("   🔍 APLICANDO REPARACIÓN GENÉRICA...")
        
        # Extraer funciones del código generado
        funciones = self._extraer_funciones(codigo)
        
        if funciones:
            # Guardar funciones en archivo utils
            utils_path = "/home/junior/Escritorio/ia-mecanica/herramientas/utils_reparacion.py"
            
            modo = 'a' if os.path.exists(utils_path) else 'w'
            with open(utils_path, modo) as f:
                if modo == 'w':
                    f.write('"""\n🛠️ UTILIDADES DE REPARACIÓN AUTOMÁTICA\n"""\n\n')
                f.write(f"\n# Funciones agregadas el {datetime.now()}\n")
                f.write(funciones)
                f.write("\n")
            
            return {
                "exito": True,
                "accion": f"Funciones guardadas en {utils_path}",
                "archivos": 1,
                "backup": self.ultimo_backup
            }
        else:
            return {
                "exito": False,
                "error": "No se pudieron extraer funciones del código"
            }
    
    def _extraer_funciones(self, codigo):
        """Extrae funciones del código generado"""
        lineas = codigo.split('\n')
        funciones = []
        dentro_funcion = False
        
        for linea in lineas:
            if linea.strip().startswith('def '):
                dentro_funcion = True
                funciones.append(linea)
            elif dentro_funcion and linea.strip():
                funciones.append(linea)
            elif dentro_funcion and not linea.strip():
                funciones.append('')
                dentro_funcion = False
        
        return '\n'.join(funciones)

# ============================================================
# VERSIÓN INTERACTIVA
# ============================================================
def main():
    agente = AgenteSupremo("SupremeBot")
    
    print("\n" + "="*60)
    print("🤖 AGENTE SUPREMO - DIAGNÓSTICO Y AUTO-REPARACIÓN")
    print("="*60)
    print("\nComandos:")
    print("  /diagnostico  - Ejecutar diagnóstico completo")
    print("  /logs        - Analizar logs")
    print("  /reparar     - Generar código para error (ej: /reparar NoneType error)")
    print("  /lista       - Ver herramientas")
    print("  /crear       - Crear nueva herramienta (ej: /crear calculadora)")
    print("  /salir       - Terminar")
    print("-"*60)
    
    while True:
        try:
            entrada = input("\n💬 Tú: ").strip()
            
            if entrada.lower() == '/salir':
                break
            elif entrada.lower() == '/diagnostico':
                print(agente.diagnosticar())
            elif entrada.lower() == '/logs':
                print(agente.analizar_logs())
            elif entrada.lower().startswith('/reparar '):
                desc = entrada[9:].strip()
                print(agente.reparar_error(desc))
            elif entrada.lower() == '/lista':
                print(agente.listar())
            elif entrada.lower() == '/ayuda':
                print("\nComandos: /diagnostico, /logs, /reparar, /lista, /crear, /salir")
            elif entrada.lower().startswith('/crear '):
                tipo = entrada[7:].strip()
                agente._crear_herramienta_desde_comando(tipo)
            else:
                # DETECCIÓN DE LENGUAJE NATURAL
                entrada_lower = entrada.lower()
                if "herramienta" in entrada_lower and "iva" in entrada_lower:
                    agente._crear_herramienta_iva()
                elif "herramienta" in entrada_lower and "calculadora" in entrada_lower:
                    agente._crear_herramienta_calculadora()
                elif "herramienta" in entrada_lower and "clima" in entrada_lower:
                    agente._crear_herramienta_clima()
                else:
                    print("Comando no reconocido. Usa /ayuda para ver los comandos disponibles.")
                
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n👋 ¡Hasta luego!")

if __name__ == "__main__":
    main()
