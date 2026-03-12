#!/usr/bin/env python3
"""
🚀 SISTEMA MEGA INTEGRADO - MECÁNICO DE VENTAS SUPREMO
Combina: Monitoreo + ML Predictivo + Memoria + Prioridad + Notificaciones
Versión: 2.0 - Corregida y optimizada
"""

import json
import time
import threading
import requests
import numpy as np
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import os
import sys
from queue import Queue
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# CONFIGURACIÓN GLOBAL
# ============================================================
API_BD = "http://localhost:5000/consultar"
CHECK_INTERVAL = 60  # segundos
LOG_FILE = "/home/junior/Escritorio/sistema-ventas-python/sistema_ventas.log"

class SistemaMega:
    def __init__(self):
        print("🚀 INICIALIZANDO SISTEMA MEGA MECÁNICO...")
        
        # Colas para comunicación entre módulos
        self.cola_alertas = Queue()
        self.cola_acciones = Queue()
        
        # Estado del sistema
        self.running = True
        self.estadisticas = {
            "inicio": datetime.now().isoformat(),
            "alertas_procesadas": 0,
            "predicciones_realizadas": 0,
            "conversaciones_memoria": 0
        }
        
        # Inicializar todos los subsistemas
        self.inicializar_subsistemas()
        
        print("✅ SISTEMA MEGA INICIALIZADO")
        print("="*60)
    
    def inicializar_subsistemas(self):
        """Inicializa todos los componentes del sistema"""
        
        # ========================================================
        # SUBSISTEMA 1: MONITOR DE ERRORES
        # ========================================================
        self.alertas_historial = self.cargar_json("alertas_detectadas.json", [])
        
        # ========================================================
        # SUBSISTEMA 2: MEMORIA Y CHATBOT
        # ========================================================
        self.memoria = self.cargar_json("memoria_chatbot.json", {
            "conversaciones": [],
            "preguntas_frecuentes": {},
            "contextos": {}
        })
        
        # ========================================================
        # SUBSISTEMA 3: CONOCIMIENTO APRENDIDO
        # ========================================================
        self.conocimiento = self.cargar_json("conocimiento_aprendido.json", {
            "patrones": [],
            "soluciones_exitosas": {},
            "estadisticas": {"total_alertas": 0, "alertas_resueltas": 0}
        })
        
        # ========================================================
        # SUBSISTEMA 4: MODELO PREDICTIVO (ML)
        # ========================================================
        self.modelo_ml = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
        self.scaler = StandardScaler()
        self.ml_entrenado = False
        
        # ========================================================
        # SUBSISTEMA 5: PRIORIDAD DINÁMICA
        # ========================================================
        self.prioridades = self.cargar_json("alertas_priorizadas.json", [])
        
        # ========================================================
        # SUBSISTEMA 6: CONFIGURACIÓN MÓVIL
        # ========================================================
        self.config_movil = self.cargar_json("config_movil.json", {
            "telegram": {"enabled": False, "bot_token": "", "chat_id": ""},
            "webhook": {"enabled": False, "url": ""}
        })
        
        print("   ✅ Subsistemas cargados")
    
    def cargar_json(self, archivo, default):
        try:
            with open(archivo, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return default
        except json.JSONDecodeError:
            print(f"⚠️ Error leyendo {archivo}, usando valores por defecto")
            return default
    
    def guardar_json(self, archivo, datos):
        try:
            with open(archivo, 'w') as f:
                json.dump(datos, f, indent=2)
        except Exception as e:
            print(f"❌ Error guardando {archivo}: {e}")
    
    def consultar_bd(self, query):
        try:
            response = requests.post(
                API_BD, 
                json={"consulta": query}, 
                timeout=5,
                headers={"Content-Type": "application/json"}
            )
            return response.json()
        except requests.exceptions.ConnectionError:
            return None
        except Exception as e:
            print(f"⚠️ Error consultando BD: {e}")
            return None
    
    # ============================================================
    # SUBSISTEMA 1: MONITOR DE ERRORES MEJORADO
    # ============================================================
    def monitorear(self):
        """Bucle principal de monitoreo"""
        print("   🔍 Módulo de monitoreo iniciado")
        
        while self.running:
            try:
                # Verificar ventas recientes
                self.verificar_ventas()
                
                # Verificar pagos pendientes
                self.verificar_pagos()
                
                # Verificar logs
                self.verificar_logs()
                
                # Verificar stock
                self.verificar_stock()
                
                time.sleep(CHECK_INTERVAL)
                
            except Exception as e:
                print(f"   ❌ Error en monitor: {e}")
                time.sleep(CHECK_INTERVAL)
    
    def verificar_ventas(self):
        query = """
        SELECT COUNT(*) as ventas_recientes 
        FROM venta 
        WHERE fecha_hora >= DATEADD(minute, -5, GETDATE())
        """
        resultado = self.consultar_bd(query)
        if resultado and resultado.get('success') and resultado.get('resultados'):
            try:
                ventas = int(resultado['resultados'][0]['ventas_recientes'])
                if ventas == 0:
                    self.crear_alerta(
                        "SIN VENTAS EN 5 MINUTOS",
                        "No se han registrado ventas en los últimos 5 minutos",
                        "🔴"
                    )
            except (ValueError, KeyError, TypeError):
                pass
    
    def verificar_pagos(self):
        query = """
        SELECT COUNT(*) as pendientes
        FROM venta_pago_detalle
        WHERE estado_pago = 'PENDIENTE'
        """
        resultado = self.consultar_bd(query)
        if resultado and resultado.get('success') and resultado.get('resultados'):
            try:
                pendientes = int(resultado['resultados'][0]['pendientes'])
                if pendientes > 0:
                    self.crear_alerta(
                        f"{pendientes} PAGOS PENDIENTES",
                        f"Hay {pendientes} pagos sin confirmar",
                        "⚠️"
                    )
            except (ValueError, KeyError, TypeError):
                pass
    
    def verificar_logs(self):
        try:
            with open(LOG_FILE, 'r') as f:
                logs = f.readlines()[-50:]
            
            errores = [l for l in logs if 'ERROR' in l or '❌' in l or 'Exception' in l]
            if errores:
                self.crear_alerta(
                    f"{len(errores)} ERRORES EN LOGS",
                    f"Último: {errores[-1][:100]}",
                    "🔴"
                )
        except FileNotFoundError:
            pass
        except Exception as e:
            print(f"⚠️ Error leyendo logs: {e}")
    
    def verificar_stock(self):
        query = """
        SELECT a.nombre, SUM(k.cantidad) as stock
        FROM articulo a
        JOIN kardex k ON a.idarticulo = k.idarticulo
        GROUP BY a.nombre
        HAVING SUM(k.cantidad) < 5
        """
        resultado = self.consultar_bd(query)
        if resultado and resultado.get('success') and resultado.get('resultados'):
            productos = resultado['resultados']
            if productos:
                self.crear_alerta(
                    f"{len(productos)} PRODUCTOS STOCK BAJO",
                    f"Primeros: {productos[0]['nombre'][:30]}...",
                    "⚠️"
                )
    
    def crear_alerta(self, titulo, mensaje, nivel):
        alerta = {
            "timestamp": datetime.now().isoformat(),
            "titulo": titulo,
            "mensaje": mensaje,
            "nivel": nivel,
            "id": len(self.alertas_historial) + 1
        }
        
        self.alertas_historial.append(alerta)
        # Mantener solo últimas 100 alertas
        if len(self.alertas_historial) > 100:
            self.alertas_historial = self.alertas_historial[-100:]
        
        self.guardar_json("alertas_detectadas.json", self.alertas_historial)
        self.estadisticas['alertas_procesadas'] += 1
        
        # Poner en cola para otros módulos
        self.cola_alertas.put(alerta)
        
        # Activar subsistemas
        self.calcular_prioridad(alerta)
        self.aprender_de_alerta(alerta)
        self.notificar_movil(alerta)
    
    # ============================================================
    # SUBSISTEMA 2: CHATBOT CON MEMORIA
    # ============================================================
    def chatbot_memoria(self, usuario, mensaje):
        """Procesa mensajes de usuario con memoria contextual"""
        
        # Buscar en preguntas frecuentes
        pregunta_norm = mensaje.lower().strip()
        if pregunta_norm in self.memoria.get("preguntas_frecuentes", {}):
            data = self.memoria["preguntas_frecuentes"][pregunta_norm]
            respuesta = f"[RECORDADO] {data['respuesta']}"
            data['veces_preguntada'] = data.get('veces_preguntada', 1) + 1
        else:
            # Respuesta por defecto (aquí conectarías con LLM)
            respuesta = f"Procesando: {mensaje}"
            
            # Aprender para futuro
            if "preguntas_frecuentes" not in self.memoria:
                self.memoria["preguntas_frecuentes"] = {}
            
            self.memoria["preguntas_frecuentes"][pregunta_norm] = {
                "respuesta": respuesta,
                "veces_preguntada": 1,
                "ultima_vez": datetime.now().isoformat()
            }
        
        # Guardar conversación
        if "conversaciones" not in self.memoria:
            self.memoria["conversaciones"] = []
        
        self.memoria["conversaciones"].append({
            "usuario": usuario,
            "fecha": datetime.now().isoformat(),
            "mensaje": mensaje,
            "respuesta": respuesta
        })
        
        # Mantener solo últimas 100 conversaciones
        if len(self.memoria["conversaciones"]) > 100:
            self.memoria["conversaciones"] = self.memoria["conversaciones"][-100:]
        
        self.estadisticas['conversaciones_memoria'] = len(self.memoria["conversaciones"])
        self.guardar_json("memoria_chatbot.json", self.memoria)
        return respuesta
    
    # ============================================================
    # SUBSISTEMA 3: APRENDIZAJE AUTOMÁTICO
    # ============================================================
    def aprender_de_alerta(self, alerta):
        """Aprende patrones de alertas repetitivas"""
        titulo_limpio = alerta['titulo'].replace('🔴', '').replace('⚠️', '').strip()
        
        # Buscar patrón existente
        patron_existente = None
        for p in self.conocimiento.get('patrones', []):
            if p.get('error', '') == titulo_limpio:
                patron_existente = p
                break
        
        if patron_existente:
            patron_existente['frecuencia'] = patron_existente.get('frecuencia', 0) + 1
            patron_existente['ultima_vez'] = alerta['timestamp']
        else:
            if 'patrones' not in self.conocimiento:
                self.conocimiento['patrones'] = []
            
            self.conocimiento['patrones'].append({
                "error": titulo_limpio,
                "frecuencia": 1,
                "ultima_vez": alerta['timestamp'],
                "nivel": alerta['nivel'],
                "aprendido": datetime.now().isoformat()
            })
        
        self.guardar_json("conocimiento_aprendido.json", self.conocimiento)
    
    # ============================================================
    # SUBSISTEMA 4: ML PREDICTIVO
    # ============================================================
    def entrenar_modelo_ml(self):
        """Entrena el modelo con datos históricos"""
        print("   🧠 Entrenando modelo ML...")
        
        query = """
        SELECT TOP 100
            v.monto_divisa,
            CASE WHEN v.igtf_aplicado = 1 THEN 1 ELSE 0 END as igtf_aplicado,
            ISNULL(v.comision_banco, 0) as comision_banco,
            COUNT(vpd.idpago) as num_pagos,
            CASE WHEN v.estado = 'REGISTRADO' THEN 1 ELSE 0 END as exitosa
        FROM venta v
        LEFT JOIN venta_pago_detalle vpd ON v.idventa = vpd.idventa
        GROUP BY v.idventa, v.monto_divisa, v.igtf_aplicado, 
                 v.comision_banco, v.estado
        """
        
        datos = self.consultar_bd(query)
        if not datos or not datos.get('resultados'):
            print("   ⚠️ No hay datos para entrenar ML")
            return False
        
        X, y = [], []
        for d in datos['resultados']:
            try:
                X.append([
                    float(d.get('monto_divisa', 0)),
                    int(d.get('igtf_aplicado', 0)),
                    float(d.get('comision_banco', 0)),
                    int(d.get('num_pagos', 1))
                ])
                y.append(int(d.get('exitosa', 1)))
            except (ValueError, TypeError) as e:
                continue
        
        if len(X) < 10:
            print("   ⚠️ Datos insuficientes para ML")
            return False
        
        try:
            X_scaled = self.scaler.fit_transform(X)
            self.modelo_ml.fit(X_scaled, y)
            self.ml_entrenado = True
            print(f"   ✅ ML entrenado con {len(X)} muestras")
            return True
        except Exception as e:
            print(f"   ❌ Error entrenando ML: {e}")
            return False
    
    # ============================================================
    # SUBSISTEMA 5: PRIORIDAD DINÁMICA
    # ============================================================
    def calcular_prioridad(self, alerta):
        """Calcula prioridad de alerta basada en múltiples factores"""
        puntuacion = 0
        
        # Factor 1: Nivel base
        if '🔴' in alerta.get('nivel', ''):
            puntuacion += 40
        elif '⚠️' in alerta.get('nivel', ''):
            puntuacion += 20
        
        # Factor 2: Frecuencia reciente
        mismo_tipo = [a for a in self.alertas_historial[-20:] 
                     if a.get('titulo', '') == alerta.get('titulo', '')]
        if len(mismo_tipo) > 3:
            puntuacion += min(len(mismo_tipo) * 2, 20)
        
        # Factor 3: Palabras clave en mensaje
        mensaje = alerta.get('mensaje', '').lower()
        if 'stock' in mensaje and '0' in mensaje:
            puntuacion += 25
        elif 'pago' in mensaje and 'pendiente' in mensaje:
            puntuacion += 15
        
        # Guardar prioridad
        prioridad = {
            'timestamp': alerta.get('timestamp', datetime.now().isoformat()),
            'titulo': alerta.get('titulo', 'Sin título'),
            'puntuacion': min(puntuacion, 100),
            'nivel': ('🔴 CRÍTICA' if puntuacion > 70 else
                     '🟡 ALTA' if puntuacion > 40 else
                     '🔵 NORMAL' if puntuacion > 20 else '⚪ BAJA')
        }
        
        self.prioridades.append(prioridad)
        # Mantener solo últimas 50 prioridades
        if len(self.prioridades) > 50:
            self.prioridades = self.prioridades[-50:]
        
        self.guardar_json("alertas_priorizadas.json", self.prioridades)
    
    # ============================================================
    # SUBSISTEMA 6: NOTIFICACIONES MÓVILES
    # ============================================================
    def notificar_movil(self, alerta):
        """Envía alerta a Telegram/Webhook si está configurado"""
        
        # Obtener última prioridad
        prioridad = self.prioridades[-1] if self.prioridades else {'nivel': '🔴 CRÍTICA'}
        nivel_prioridad = prioridad.get('nivel', '🔴 CRÍTICA')
        
        # Solo enviar alertas críticas o altas
        if "BAJA" in nivel_prioridad:
            return
        
        mensaje = f"""
{alerta.get('nivel', '🔔')} *{alerta.get('titulo', 'Alerta')}*
📅 {alerta.get('timestamp', datetime.now().isoformat())}
📝 {alerta.get('mensaje', '')}
🏷️ {nivel_prioridad}

-- Sistema MEGA Mecánico
        """.strip()
        
        # Telegram
        if self.config_movil.get('telegram', {}).get('enabled', False):
            try:
                token = self.config_movil['telegram'].get('bot_token', '')
                chat_id = self.config_movil['telegram'].get('chat_id', '')
                if token and chat_id:
                    url = f"https://api.telegram.org/bot{token}/sendMessage"
                    requests.post(url, json={"chat_id": chat_id, "text": mensaje}, timeout=3)
            except Exception as e:
                print(f"⚠️ Error enviando Telegram: {e}")
        
        # Webhook
        if self.config_movil.get('webhook', {}).get('enabled', False):
            try:
                url = self.config_movil['webhook'].get('url', '')
                if url:
                    requests.post(url, json={"alerta": alerta, "prioridad": prioridad}, timeout=3)
            except Exception as e:
                print(f"⚠️ Error enviando webhook: {e}")
    
    # ============================================================
    # DASHBOARD INTEGRADO
    # ============================================================
    def mostrar_dashboard(self):
        """Muestra estado completo del sistema"""
        os.system('clear' if os.name == 'posix' else 'cls')
        print("\n" + "="*80)
        print("🚀 SISTEMA MEGA MECÁNICO DE VENTAS - DASHBOARD")
        print("="*80)
        
        print(f"\n📊 ESTADÍSTICAS GENERALES:")
        print(f"   • Alertas procesadas: {len(self.alertas_historial)}")
        print(f"   • Patrones aprendidos: {len(self.conocimiento.get('patrones', []))}")
        print(f"   • Conversaciones memoria: {len(self.memoria.get('conversaciones', []))}")
        print(f"   • ML entrenado: {'✅' if self.ml_entrenado else '❌'}")
        
        print(f"\n🔴 ÚLTIMAS ALERTAS (priorizadas):")
        for alerta in self.prioridades[-5:]:
            nivel = alerta.get('nivel', '⚪ SIN NIVEL')
            titulo = alerta.get('titulo', 'Sin título')[:50]
            print(f"   {nivel:12} - {titulo}")
        
        print(f"\n🧠 CONOCIMIENTO APRENDIDO:")
        for patron in self.conocimiento.get('patrones', [])[-3:]:
            print(f"   • {patron.get('error', 'Desconocido')} - {patron.get('frecuencia', 0)} veces")
        
        print("\n" + "="*80)
    
    # ============================================================
    # HILOS DE EJECUCIÓN
    # ============================================================
    def iniciar(self):
        """Inicia todos los módulos en paralelo"""
        
        # Entrenar ML al inicio
        self.entrenar_modelo_ml()
        
        # Hilo 1: Monitoreo
        t1 = threading.Thread(target=self.monitorear)
        t1.daemon = True
        t1.start()
        
        # Hilo 2: Dashboard automático
        def dashboard_loop():
            while self.running:
                self.mostrar_dashboard()
                time.sleep(10)
        
        t2 = threading.Thread(target=dashboard_loop)
        t2.daemon = True
        t2.start()
        
        # Hilo 3: Chatbot interactivo
        def chatbot_loop():
            while self.running:
                try:
                    mensaje = input("\n💬 Tú: ").strip()
                    if mensaje.lower() == '/salir':
                        self.running = False
                        break
                    elif mensaje.lower() == '/stats':
                        print(json.dumps(self.estadisticas, indent=2))
                    elif mensaje.lower() == '/alertas':
                        for a in self.alertas_historial[-5:]:
                            print(f"{a.get('nivel', '🔔')} {a.get('titulo', '')}")
                    else:
                        respuesta = self.chatbot_memoria("junior", mensaje)
                        print(f"🤖 MegaBot: {respuesta}")
                except EOFError:
                    time.sleep(1)
                except Exception as e:
                    print(f"⚠️ Error en chatbot: {e}")
        
        t3 = threading.Thread(target=chatbot_loop)
        t3.daemon = True
        t3.start()
        
        print("\n🎯 SISTEMA MEGA CORRIENDO - Presiona Enter para interactuar")
        print("   Comandos: /stats, /alertas, /salir")
        
        # Mantener principal vivo
        try:
            t1.join()
        except KeyboardInterrupt:
            self.running = False
            print("\n👋 Sistema detenido")

def main():
    sistema = SistemaMega()
    sistema.iniciar()

if __name__ == "__main__":
    main()
