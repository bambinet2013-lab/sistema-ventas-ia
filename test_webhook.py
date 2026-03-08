#!/usr/bin/env python3
"""
Script para probar el webhook de Cashea
"""
import requests
import json
from datetime import datetime

# Datos de prueba
datos_prueba = {
    "referencia": f"CASHEA-TEST-{datetime.now().strftime('%y%m%d%H%M%S')}",
    "monto_total": 150.00,
    "inicial": 60.00,
    "cuotas": 3,
    "cliente": "Cliente de Prueba",
    "estado": "aprobado"
}

print("📤 Enviando webhook de prueba...")
print(json.dumps(datos_prueba, indent=2))

try:
    response = requests.post(
        "http://localhost:8000/webhook/cashea",
        json=datos_prueba,
        headers={"X-Event-Type": "payment.approved"}
    )
    
    print(f"\n📥 Respuesta: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    
except Exception as e:
    print(f"❌ Error: {e}")
