#!/bin/bash
# git_guardar_proyecto.sh
# Script para guardar todo el proyecto en GitHub antes de la Fase 0

echo "=================================================="
echo "🚀 GUARDANDO PROYECTO EN GITHUB - PRE-FASE 0"
echo "=================================================="
echo ""

# 1. Verificar el estado actual
echo "📊 Estado actual de los archivos:"
git status
echo ""

# 2. Agregar todos los archivos (respetando .gitignore)
echo "📦 Agregando archivos al staging area..."
git add .
echo "✅ Archivos agregados"
echo ""

# 3. Crear el commit con mensaje descriptivo
FECHA=$(date +"%Y-%m-%d %H:%M")
MENSAJE="🚀 PRE-FASE 0: Proyecto estable antes de iniciar integración con Cashea

✅ Sistema base funcionando:
   • Módulo de ventas con carrito inteligente
   • Gestión de clientes y artículos
   • Control de inventario vía kardex
   • Interfaz gráfica mejorada (Tkinter)
   • Sistema de permisos y roles
   • Integración con tasas de cambio USD/BS

📅 Fecha: $FECHA
👤 Autor: $(git config user.name)"

echo "📝 Creando commit:"
echo "$MENSAJE"
echo ""

git commit -m "$MENSAJE"

# 4. Verificar resultado del commit
if [ $? -eq 0 ]; then
    echo "✅ Commit creado exitosamente"
else
    echo "❌ Error al crear el commit"
    exit 1
fi
echo ""

# 5. Mostrar los últimos commits
echo "📋 Últimos commits:"
git log --oneline -5
echo ""

# 6. Preguntar si quiere hacer push
echo "=================================================="
echo "🌐 ¿Deseas subir los cambios a GitHub remoto?"
echo "=================================================="
echo "1. Sí, hacer push ahora"
echo "2. No, solo dejar el commit local"
echo "0. Cancelar"
echo ""

read -p "🔹 Seleccione una opción: " PUSH_OPCION

if [ "$PUSH_OPCION" == "1" ]; then
    echo ""
    echo "📤 Subiendo cambios a GitHub..."
    git push origin main || git push origin master
    
    if [ $? -eq 0 ]; then
        echo "✅ Cambios subidos exitosamente a GitHub"
    else
        echo "❌ Error al subir a GitHub"
        echo "   Verifica tu conexión y permisos"
    fi
elif [ "$PUSH_OPCION" == "2" ]; then
    echo ""
    echo "✅ Commit guardado localmente. Puedes hacer push después con:"
    echo "   git push origin main"
else
    echo ""
    echo "❌ Operación cancelada"
fi

echo ""
echo "=================================================="
echo "🎉 PROCESO COMPLETADO"
echo "=================================================="
