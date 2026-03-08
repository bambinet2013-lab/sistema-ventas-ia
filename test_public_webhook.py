#!/usr/bin/env python3
"""
Script para probar el webhook público
"""
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

public_url = os.getenv('PUBLIC_URL', 'http://localhost:8000')
webhook_url = f"{public_url}/webhook/cashea"

print(f"🔍 Probando webhook en: {webhook_url}")
print(f"Usando PUBLIC_URL: {public_url}")

# Test 1: Ping
print("\n📡 Test 1: Enviando ping...")
try:
    response = requests.post(
        webhook_url,
        json={"event": "ping"},
        headers={"X-Event-Type": "ping"},
        timeout=5
    )
    print(f"   Respuesta: {response.status_code}")
    print(f"   {response.json()}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 2: Notificación real
print("\n💰 Test 2: Simulando pago aprobado...")
datos_prueba = {
    "referencia": f"PUBLIC-TEST-{os.urandom(4).hex()}",
    "monto_total": 250.00,
    "inicial": 100.00,
    "cuotas": 3,
    "cliente": "Cliente Público",
    "estado": "aprobado"
}

try:
    response = requests.post(
        webhook_url,
        json=datos_prueba,
        headers={"X-Event-Type": "payment.approved"},
        timeout=5
    )
    print(f"   Respuesta: {response.status_code}")
    print(f"   {response.json()}")
except Exception as e:
    print(f"   ❌ Error: {e}")
