#!/bin/bash
# pegar_con_indentacion.sh
# Script para pegar código respetando la indentación

echo "📋 PEGAR CÓDIGO CON INDENTACIÓN"
echo "================================"
echo ""
echo "1. Copia el código al portapapeles (Ctrl+C)"
echo "2. Presiona Enter cuando esté listo"
read

# Obtener el contenido del portapapeles
xclip -selection clipboard -o > /tmp/codigo_a_pegar.py

echo ""
echo "✅ Código guardado temporalmente en: /tmp/codigo_a_pegar.py"
echo ""
echo "Contenido capturado:"
echo "-------------------"
cat /tmp/codigo_a_pegar.py
echo "-------------------"
echo ""
echo "¿Quieres abrir este archivo en nano? (s/N)"
read -n 1 respuesta
echo ""

if [[ $respuesta == "s" || $respuesta == "S" ]]; then
    nano /tmp/codigo_a_pegar.py
    echo ""
    echo "👉 Cuando termines de editar, puedes copiar el contenido con:"
    echo "   cat /tmp/codigo_a_pegar.py | xclip -selection clipboard"
else
    echo ""
    echo "Puedes ver el archivo con: cat /tmp/codigo_a_pegar.py"
fi
