"""
API Webhook para recibir notificaciones de Cashea
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from fastapi import FastAPI, Request, HTTPException, Header
from fastapi.responses import JSONResponse
import hmac
import hashlib
import json
from datetime import datetime
import threading
import time

from loguru import logger
from agente_escritorio.agents.cashea_agent import CasheaAgent
from capa_datos.conexion import ConexionDB

app = FastAPI(title="Webhook Cashea", description="Endpoint para recibir notificaciones de Cashea")

# Almacén de notificaciones en memoria (para comunicación con la interfaz)
# En producción, esto podría ser una cola Redis o base de datos
notificaciones_pendientes = []
notificaciones_por_referencia = {}

class WebhookHandler:
    """Manejador de webhooks de Cashea"""
    
    def __init__(self):
        self.cashea_agent = CasheaAgent()
        self.conn = None
    
    def _get_connection(self):
        """Obtiene conexión a la base de datos"""
        return ConexionDB().conectar()
    
    def verificar_firma(self, payload: bytes, firma: str, secreto: str) -> bool:
        """
        Verifica la firma del webhook usando HMAC-SHA256
        """
        if not firma:
            logger.warning("Webhook recibido sin firma")
            return False
        
        # Calcular firma esperada
        firma_esperada = hmac.new(
            secreto.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        # Comparación segura para evitar timing attacks
        return hmac.compare_digest(firma, firma_esperada)
    
    def procesar_notificacion(self, datos: dict):
        """
        Procesa la notificación recibida de Cashea
        """
        try:
            # Extraer datos relevantes
            referencia = datos.get('referencia') or datos.get('id')
            estado = datos.get('estado') or datos.get('status')
            monto_total = datos.get('monto_total') or datos.get('amount', 0)
            inicial = datos.get('inicial') or datos.get('down_payment', 0)
            cuotas = datos.get('cuotas') or datos.get('installments', 0)
            cliente = datos.get('cliente') or datos.get('customer', {}).get('name', 'Cliente Cashea')
            
            # Crear objeto de notificación
            notificacion = {
                'fecha': datetime.now().strftime('%d/%m/%Y %H:%M'),
                'referencia': referencia,
                'monto_total': float(monto_total),
                'inicial': float(inicial),
                'cuotas': int(cuotas),
                'cliente': cliente,
                'estado': estado,
                'leida': False,
                'datos_completos': datos
            }
            
            # Guardar en memoria
            global notificaciones_pendientes, notificaciones_por_referencia
            notificaciones_pendientes.append(notificacion)
            if referencia:
                notificaciones_por_referencia[referencia] = notificacion
            
            logger.success(f"✅ Notificación Cashea recibida: {referencia} - ${monto_total}")
            
            # Aquí podrías guardar en BD si lo deseas
            # self.guardar_en_bd(notificacion)
            
            return notificacion
            
        except Exception as e:
            logger.error(f"❌ Error procesando notificación: {e}")
            return None
    
    def guardar_en_bd(self, notificacion):
        """Guarda la notificación en base de datos (opcional)"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO log_webhook_cashea 
                (referencia, monto_total, inicial, cuotas, cliente, estado, fecha, datos_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                notificacion['referencia'],
                notificacion['monto_total'],
                notificacion['inicial'],
                notificacion['cuotas'],
                notificacion['cliente'],
                notificacion['estado'],
                datetime.now(),
                json.dumps(notificacion['datos_completos'])
            ))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Error guardando en BD: {e}")

# Instancia global del manejador
handler = WebhookHandler()

@app.get("/")
async def root():
    """Endpoint de prueba"""
    return {"message": "Webhook Cashea funcionando", "status": "online"}

@app.post("/webhook/cashea")
async def recibir_webhook(
    request: Request,
    x_webhook_signature: str = Header(None, alias="X-Webhook-Signature"),
    x_event_type: str = Header(None, alias="X-Event-Type")
):
    """
    Endpoint principal para recibir webhooks de Cashea
    """
    # Leer body
    body = await request.body()
    
    # Verificar firma si está configurada
    if x_webhook_signature and handler.cashea_agent.config:
        secreto = handler.cashea_agent.config.get('webhook_secret', '')
        if secreto and not handler.verificar_firma(body, x_webhook_signature, secreto):
            logger.warning("⚠️ Firma de webhook inválida")
            raise HTTPException(status_code=401, detail="Firma inválida")
    
    # Parsear JSON
    try:
        datos = await request.json()
    except:
        datos = {}
    
    logger.info(f"📩 Webhook recibido - Tipo: {x_event_type}")
    
    # Procesar según tipo de evento
    if x_event_type == 'ping' or datos.get('event') == 'ping':
        # Evento de prueba
        return {"status": "ok", "message": "Webhook activo"}
    
    elif x_event_type in ['payment.approved', 'transaction.completed'] or datos.get('estado') in ['aprobado', 'completed']:
        # Pago aprobado por el cliente
        notificacion = handler.procesar_notificacion(datos)
        if notificacion:
            return {
                "status": "received",
                "reference": notificacion['referencia'],
                "message": "Notificación procesada correctamente"
            }
        else:
            raise HTTPException(status_code=500, detail="Error procesando notificación")
    
    else:
        # Otros eventos (ignorar o loguear)
        logger.info(f"ℹ️ Evento ignorado: {x_event_type}")
        return {"status": "ignored", "event": x_event_type}

@app.get("/notificaciones/pendientes")
async def obtener_pendientes():
    """
    Endpoint para que la interfaz consulte notificaciones pendientes
    """
    global notificaciones_pendientes
    # Filtrar no leídas
    pendientes = [n for n in notificaciones_pendientes if not n.get('leida', False)]
    return {"notificaciones": pendientes}

@app.post("/notificaciones/marcar/{referencia}")
async def marcar_como_leida(referencia: str):
    """
    Marca una notificación como leída
    """
    global notificaciones_pendientes
    for n in notificaciones_pendientes:
        if n.get('referencia') == referencia:
            n['leida'] = True
            return {"status": "ok", "message": "Notificación marcada como leída"}
    raise HTTPException(status_code=404, detail="Notificación no encontrada")

# Para ejecutar el servidor:
# uvicorn api.webhook_cashea:app --reload --port 8000
