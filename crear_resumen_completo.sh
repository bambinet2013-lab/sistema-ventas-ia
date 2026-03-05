#!/bin/bash
# crear_resumen_completo.sh
# Este script genera un archivo con todo el código Python y la estructura de BD

echo "📦 GENERANDO RESUMEN COMPLETO DEL PROYECTO"
echo "==========================================="
echo ""

OUTPUT_FILE="resumen_completo_$(date +%Y%m%d_%H%M%S).txt"
echo "📁 Archivo de salida: $OUTPUT_FILE"
echo ""

# 1. ESTRUCTURA DE BASE DE DATOS
echo "=== ESTRUCTURA COMPLETA DE BASE DE DATOS ===" > $OUTPUT_FILE
echo "" >> $OUTPUT_FILE

echo "-- TABLAS Y SUS COLUMNAS" >> $OUTPUT_FILE
sqlcmd -S localhost -U sa -P Santi07. -d SistemaVentas -C -Q "
SELECT 
    TABLE_NAME,
    COLUMN_NAME,
    DATA_TYPE,
    CHARACTER_MAXIMUM_LENGTH,
    IS_NULLABLE
FROM INFORMATION_SCHEMA.COLUMNS
ORDER BY TABLE_NAME, ORDINAL_POSITION;
" >> $OUTPUT_FILE 2>/dev/null

echo "" >> $OUTPUT_FILE
echo "-- RELACIONES (LLAVES FORÁNEAS)" >> $OUTPUT_FILE
sqlcmd -S localhost -U sa -P Santi07. -d SistemaVentas -C -Q "
SELECT 
    fk.name AS FK_NAME,
    OBJECT_NAME(fk.parent_object_id) AS TABLA_ORIGEN,
    COL_NAME(fkc.parent_object_id, fkc.parent_column_id) AS COLUMNA_ORIGEN,
    OBJECT_NAME(fk.referenced_object_id) AS TABLA_DESTINO,
    COL_NAME(fkc.referenced_object_id, fkc.referenced_column_id) AS COLUMNA_DESTINO
FROM sys.foreign_keys fk
JOIN sys.foreign_key_columns fkc ON fk.object_id = fkc.constraint_object_id
ORDER BY TABLA_ORIGEN;
" >> $OUTPUT_FILE 2>/dev/null

echo "" >> $OUTPUT_FILE
echo "-- ÍNDICES Y RESTRICCIONES" >> $OUTPUT_FILE
sqlcmd -S localhost -U sa -P Santi07. -d SistemaVentas -C -Q "
SELECT 
    TABLA = t.name,
    INDICE = i.name,
    TIPO = i.type_desc,
    COLUMNAS = STUFF((
        SELECT ', ' + c.name
        FROM sys.index_columns ic
        JOIN sys.columns c ON ic.object_id = c.object_id AND ic.column_id = c.column_id
        WHERE ic.object_id = i.object_id AND ic.index_id = i.index_id
        ORDER BY ic.key_ordinal
        FOR XML PATH('')
    ), 1, 2, '')
FROM sys.tables t
JOIN sys.indexes i ON t.object_id = i.object_id
WHERE i.name IS NOT NULL
ORDER BY t.name, i.name;
" >> $OUTPUT_FILE 2>/dev/null

# 2. ARCHIVOS PYTHON PRINCIPALES
echo "" >> $OUTPUT_FILE
echo "=== ARCHIVOS PYTHON DEL PROYECTO ===" >> $OUTPUT_FILE
echo "" >> $OUTPUT_FILE

# Lista de archivos importantes a incluir
ARCHIVOS=(
    "main.py"
    "capa_presentacion/menu_principal.py"
    "capa_presentacion/menu_principal_backup.py"
    "capa_negocio/__init__.py"
    "capa_negocio/base_service.py"
    "capa_negocio/cliente_service.py"
    "capa_negocio/articulo_service.py"
    "capa_negocio/venta_service.py"
    "capa_negocio/inventario_service.py"
    "capa_negocio/tasa_service.py"
    "capa_negocio/rol_service.py"
    "capa_negocio/usuario_admin_service.py"
    "capa_negocio/ia_productos_service.py"
    "capa_negocio/validacion_venezuela.py"
    "capa_negocio/utils.py"
    "capa_datos/__init__.py"
    "capa_datos/conexion.py"
    "capa_datos/cliente_repo.py"
    "capa_datos/articulo_repo.py"
    "capa_datos/venta_repo.py"
    "capa_datos/inventario_repo.py"
    "capa_datos/tasa_repo.py"
    "capa_datos/rol_repo.py"
    "capa_datos/usuario_admin_repo.py"
    "capa_datos/aprendizaje_repo.py"
    "capa_datos/auditoria_repo.py"
    "config/seniat_config.py"
    "agente_escritorio/__init__.py"
    "agente_escritorio/main.py"
    "agente_escritorio/run_gui.py"
    "agente_escritorio/run_inteligente.py"
    "agente_escritorio/core/__init__.py"
    "agente_escritorio/core/config.py"
    "agente_escritorio/core/database.py"
    "agente_escritorio/agents/__init__.py"
    "agente_escritorio/agents/cliente_agent.py"
    "agente_escritorio/agents/articulo_agent.py"
    "agente_escritorio/agents/venta_agent.py"
    "agente_escritorio/ui/__init__.py"
    "agente_escritorio/ui/main_window.py"
    "agente_escritorio/ui/main_window_inteligente.py"
)

for archivo in "${ARCHIVOS[@]}"; do
    if [ -f "$archivo" ]; then
        echo "----- $archivo -----" >> $OUTPUT_FILE
        cat "$archivo" >> $OUTPUT_FILE
        echo "" >> $OUTPUT_FILE
        echo "✅ Incluido: $archivo"
    else
        echo "⚠️ No encontrado: $archivo"
    fi
done

# 3. ARCHIVOS DE CONFIGURACIÓN
echo "" >> $OUTPUT_FILE
echo "=== ARCHIVOS DE CONFIGURACIÓN ===" >> $OUTPUT_FILE

if [ -f ".env" ]; then
    echo "----- .env -----" >> $OUTPUT_FILE
    # Ocultar contraseñas reales por seguridad
    sed 's/\(PASSWORD=\).*/\1***HIDDEN***/' .env >> $OUTPUT_FILE
    echo "✅ Incluido: .env"
fi

if [ -f "requirements.txt" ]; then
    echo "----- requirements.txt -----" >> $OUTPUT_FILE
    cat requirements.txt >> $OUTPUT_FILE
    echo "✅ Incluido: requirements.txt"
fi

# 4. ESTRUCTURA DE CARPETAS
echo "" >> $OUTPUT_FILE
echo "=== ESTRUCTURA DE CARPETAS ===" >> $OUTPUT_FILE
tree -L 4 -I '__pycache__|*.pyc|*.pyo|*.db|venv|*.log' >> $OUTPUT_FILE 2>/dev/null || echo "⚠️ tree no instalado, omitiendo..." >> $OUTPUT_FILE

echo ""
echo "✅ RESUMEN GENERADO: $OUTPUT_FILE"
echo "📏 Tamaño: $(du -h $OUTPUT_FILE | cut -f1)"
echo ""
echo "📤 Ahora sube este archivo a Pastebin:"
echo "   cat $OUTPUT_FILE | pastebinit -b pastebin.com -t \"Sistema Ventas - Resumen Completo $(date +%Y%m%d)\" -a \"junior\""
echo ""
echo "   O si no tienes pastebinit, usa el enlace manual:"
echo "   https://pastebin.com/ → pega el contenido del archivo manualmente"
