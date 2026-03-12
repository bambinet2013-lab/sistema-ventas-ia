#!/usr/bin/env python3
"""
📱 INTEGRACIÓN MÓVIL PARA ALERTAS EN TIEMPO REAL
Recibe notificaciones en WhatsApp y Telegram
Código de nivel empresarial - Muy pocos lo tienen
"""

import requests
import json
from datetime import datetime
import time
import os

class NotificadorMovil:
    def __init__(self):
        self.ultima_alerta_file = "ultima_alerta.txt"
        self.config_file = "config_movil.json"
        self.config = self.cargar_config()
        
    def cargar_config(self):
        """Carga configuración de APIs (debes configurar tus tokens)"""
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except:
            # Configuración por defecto (debes editarla)
            config = {
                "telegram": {
                    "enabled": False,
                    "bot_token": "TU_BOT_TOKEN_AQUI",
                    "chat_id": "TU_CHAT_ID_AQUI"
                },
                "whatsapp": {
                    "enabled": False,
                    "api_url": "https://api.whatsapp.com/send",
                    "phone_number": "TU_NUMERO_AQUI"
                },
                "webhook": {
                    "enabled": False,
                    "url": "https://tu-servidor.com/webhook"
                }
            }
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            print("📁 Archivo de configuración creado. Edítalo con tus datos.")
            return config
    
    def enviar_telegram(self, mensaje):
        """Envía mensaje por Telegram"""
        if not self.config['telegram']['enabled']:
            return False
        
        try:
            url = f"https://api.telegram.org/bot{self.config['telegram']['bot_token']}/sendMessage"
            data = {
                "chat_id": self.config['telegram']['chat_id'],
                "text": mensaje,
                "parse_mode": "HTML"
            }
            response = requests.post(url, data=data, timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def enviar_webhook(self, mensaje):
        """Envía a webhook personalizado"""
        if not self.config['webhook']['enabled']:
            return False
        
        try:
            data = {
                "timestamp": datetime.now().isoformat(),
                "mensaje": mensaje,
                "tipo": "alerta_sistema"
            }
            response = requests.post(
                self.config['webhook']['url'],
                json=data,
                timeout=3
            )
            return response.status_code == 200
        except:
            return False
    
    def leer_ultimas_alertas(self):
        """Lee las últimas alertas del archivo"""
        try:
            with open("alertas_detectadas.json", 'r') as f:
                alertas = json.load(f)
            return alertas[-3:]  # Últimas 3 alertas
        except:
            return []
    
    def obtener_ultimo_envio(self):
        """Obtiene timestamp del último envío"""
        try:
            with open(self.ultima_alerta_file, 'r') as f:
                return f.read().strip()
        except:
            return "2000-01-01T00:00:00"
    
    def guardar_ultimo_envio(self, timestamp):
        with open(self.ultima_alerta_file, 'w') as f:
            f.write(timestamp)
    
    def formatear_mensaje(self, alerta):
        """Formatea alerta para enviar por mensaje"""
        nivel = alerta.get('nivel', '🔔')
        titulo = alerta.get('titulo', 'Alerta')
        mensaje = alerta.get('mensaje', '')
        timestamp = alerta.get('timestamp', '')
        
        return f"""
{nivel} *{titulo}*
📅 {timestamp}
📝 {mensaje}

--
Sistema de Monitoreo Automático
        """.strip()
    
    def monitorear_y_notificar(self):
        """Monitorea alertas y envía notificaciones"""
        print("📱 Iniciando monitoreo para notificaciones móviles...")
        print("   (Configura tus tokens en config_movil.json)")
        
        ultimo_envio = self.obtener_ultimo_envio()
        
        while True:
            try:
                alertas = self.leer_ultimas_alertas()
                
                for alerta in alertas:
                    if alerta['timestamp'] > ultimo_envio:
                        mensaje = self.formatear_mensaje(alerta)
                        
                        # Enviar por Telegram
                        if self.enviar_telegram(mensaje):
                            print(f"✅ Telegram: {alerta['titulo']}")
                        
                        # Enviar por webhook
                        if self.enviar_webhook(mensaje):
                            print(f"✅ Webhook: {alerta['titulo']}")
                        
                        ultimo_envio = alerta['timestamp']
                
                self.guardar_ultimo_envio(ultimo_envio)
                time.sleep(30)  # Revisar cada 30 segundos
                
            except KeyboardInterrupt:
                print("\n👋 Monitoreo detenido")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                time.sleep(60)

def configurar():
    """Asistente de configuración interactivo"""
    print("\n" + "="*60)
    print("📱 CONFIGURACIÓN DE NOTIFICACIONES MÓVILES")
    print("="*60)
    
    config = {}
    
    # Telegram
    print("\n🤖 Configurar Telegram (opcional)")
    usar_telegram = input("¿Quieres usar Telegram? (s/N): ").lower() == 's'
    if usar_telegram:
        config['telegram'] = {
            "enabled": True,
            "bot_token": input("Bot Token: ").strip(),
            "chat_id": input("Chat ID: ").strip()
        }
    
    # Webhook
    print("\n🔗 Configurar Webhook (opcional)")
    usar_webhook = input("¿Quieres usar webhook? (s/N): ").lower() == 's'
    if usar_webhook:
        config['webhook'] = {
            "enabled": True,
            "url": input("URL del webhook: ").strip()
        }
    
    with open("config_movil.json", 'w') as f:
        json.dump(config, f, indent=2)
    
    print("\n✅ Configuración guardada en config_movil.json")

def main():
    print("📱 INTEGRACIÓN MÓVIL PARA ALERTAS")
    print("="*60)
    
    notificador = NotificadorMovil()
    
    while True:
        print("\nOpciones:")
        print("1. Iniciar monitoreo y enviar notificaciones")
        print("2. Configurar Telegram/Webhook")
        print("3. Probar envío manual")
        print("4. Salir")
        
        opcion = input("\nSelecciona: ").strip()
        
        if opcion == '1':
            notificador.monitorear_y_notificar()
        elif opcion == '2':
            configurar()
            notificador = NotificadorMovil()  # Recargar configuración
        elif opcion == '3':
            alertas = notificador.leer_ultimas_alertas()
            if alertas:
                mensaje = notificador.formatear_mensaje(alertas[-1])
                print(f"\n📤 Enviando:\n{mensaje}\n")
                
                if notificador.enviar_telegram(mensaje):
                    print("✅ Telegram: OK")
                if notificador.enviar_webhook(mensaje):
                    print("✅ Webhook: OK")
            else:
                print("❌ No hay alertas para probar")
        elif opcion == '4':
            break

if __name__ == "__main__":
    main()
