#!/bin/bash
echo "🚀 INICIANDO SISTEMA MEGA MECÁNICO"

# Ir al directorio
cd /home/junior/Escritorio/ia-mecanica/herramientas

# Activar entorno virtual
source venv/bin/activate

# Iniciar servidor BD si no está corriendo
python3 servidor_bd.py > /dev/null 2>&1 &
echo "✅ Servidor BD iniciado"

# Iniciar sistema mega
python3 sistema_mega.py
