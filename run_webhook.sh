#!/bin/bash
# Script para iniciar el servidor webhook de Cashea

echo "=================================================="
echo "🚀 INICIANDO SERVIDOR WEBHOOK CASHEA"
echo "=================================================="
echo ""

# Activar entorno virtual
source venv/bin/activate

# Iniciar servidor
cd ~/Escritorio/sistema-ventas-python
uvicorn api.webhook_cashea:app --reload --host 0.0.0.0 --port 8000
