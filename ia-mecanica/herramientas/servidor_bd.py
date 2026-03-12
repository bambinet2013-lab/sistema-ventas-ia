#!/usr/bin/env python3
"""
Servidor para consultas seguras a la base de datos SistemaVentas
Uso: python3 servidor_bd.py
"""

from flask import Flask, request, jsonify
import pyodbc
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

def conectar_bd():
    """Establece conexión con SQL Server"""
    try:
        conn_str = (
            "DRIVER={ODBC Driver 18 for SQL Server};"
            "SERVER=localhost,1433;"
            "DATABASE=SistemaVentas;"
            "UID=sa;"
            "PWD=Santi07.;"
            "TrustServerCertificate=yes;"
        )
        conn = pyodbc.connect(conn_str)
        logger.info("✅ Conexión a BD exitosa")
        return conn
    except Exception as e:
        logger.error(f"❌ Error conectando a BD: {e}")
        return None

@app.route('/health', methods=['GET'])
def health():
    """Endpoint para verificar que el servidor está vivo"""
    return jsonify({'status': 'ok', 'servidor': 'BD Mecánico'})

@app.route('/consultar', methods=['POST'])
def consultar():
    """
    Endpoint para ejecutar consultas SQL (solo SELECT)
    Ejemplo: curl -X POST http://localhost:5000/consultar -H "Content-Type: application/json" -d '{"consulta": "SELECT TOP 3 * FROM venta"}'
    """
    try:
        # Obtener datos de la petición
        datos = request.get_json()
        if not datos:
            return jsonify({'error': 'No se enviaron datos JSON'}), 400
        
        consulta = datos.get('consulta', '').strip()
        logger.info(f"📝 Consulta recibida: {consulta[:100]}...")
        
        # Validar que sea SELECT (seguridad)
        if not consulta.upper().startswith('SELECT'):
            return jsonify({'error': 'Solo consultas SELECT permitidas por seguridad'}), 400
        
        # Conectar a la BD
        conn = conectar_bd()
        if not conn:
            return jsonify({'error': 'No se pudo conectar a la base de datos'}), 500
        
        cursor = conn.cursor()
        cursor.execute(consulta)
        
        # Obtener nombres de columnas
        columnas = [columna[0] for columna in cursor.description]
        
        # Convertir resultados a lista de diccionarios
        resultados = []
        for fila in cursor.fetchall():
            fila_dict = {}
            for i, valor in enumerate(fila):
                fila_dict[columnas[i]] = str(valor) if valor is not None else None
            resultados.append(fila_dict)
        
        conn.close()
        logger.info(f"✅ {len(resultados)} resultados obtenidos")
        
        return jsonify({
            'success': True,
            'resultados': resultados,
            'total': len(resultados),
            'consulta': consulta
        })
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/tablas', methods=['GET'])
def listar_tablas():
    """Lista todas las tablas disponibles (útil para explorar)"""
    try:
        conn = conectar_bd()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT TABLE_NAME 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_TYPE = 'BASE TABLE'
            ORDER BY TABLE_NAME
        """)
        tablas = [row[0] for row in cursor.fetchall()]
        conn.close()
        return jsonify({'tablas': tablas})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    logger.info("🚀 Iniciando servidor de BD en http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)
