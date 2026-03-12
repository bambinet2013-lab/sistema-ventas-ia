#!/bin/bash
echo "🚀 Iniciando Mecánico de Ventas..."

# 1. Iniciar servidor de base de datos (si no está corriendo)
cd /home/junior/Escritorio/ia-mecanica/herramientas
source venv/bin/activate
python3 servidor_bd.py > /dev/null 2>&1 &
echo "✅ Servidor BD iniciado (puerto 5000)"

# 2. Iniciar interfaz web
python3 app_web.py > /dev/null 2>&1 &
echo "✅ Interfaz web iniciada (puerto 5001)"

# 3. Abrir navegador
sleep 2
xdg-open http://localhost:5001

echo ""
echo "📊 Todo listo! Puedes acceder en:"
echo "   - Interfaz web: http://localhost:5001"
echo "   - API BD: http://localhost:5000"
echo ""
echo "Para detener: ./detener_mecanico.sh"
