#!/bin/bash
echo "🛑 Deteniendo Mecánico de Ventas..."

# Matar procesos de Python
pkill -f servidor_bd.py
pkill -f app_web.py

echo "✅ Servicios detenidos"
