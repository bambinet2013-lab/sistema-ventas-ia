#!/usr/bin/env python3
"""
Interfaz web para el asistente de base de datos
Ejecutar: python3 app_web.py
"""

from flask import Flask, render_template_string, request, jsonify
import subprocess
import json

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>🤖 Mecánico de Ventas</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 1000px; margin: 0 auto; padding: 20px; background: #f5f5f5; }
        .container { background: white; border-radius: 10px; padding: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #333; border-bottom: 3px solid #4CAF50; padding-bottom: 10px; }
        textarea { width: 100%; height: 60px; padding: 10px; font-size: 16px; border: 2px solid #ddd; border-radius: 5px; }
        button { background: #4CAF50; color: white; padding: 12px 30px; border: none; border-radius: 5px; font-size: 16px; cursor: pointer; }
        button:hover { background: #45a049; }
        .resultado { margin-top: 20px; padding: 15px; background: #f9f9f9; border-radius: 5px; border-left: 4px solid #4CAF50; }
        .ejemplos { margin-top: 20px; padding: 10px; background: #e8f4fd; border-radius: 5px; }
        .ejemplo-item { cursor: pointer; color: #2196F3; margin: 5px 0; }
        .ejemplo-item:hover { text-decoration: underline; }
        pre { background: #1e1e1e; color: #d4d4d4; padding: 10px; border-radius: 5px; overflow-x: auto; }
        .loading { display: none; text-align: center; margin: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 Asistente Mecánico de Ventas</h1>
        <p>Haz preguntas en español sobre tu sistema de ventas</p>
        
        <div class="ejemplos">
            <h3>📝 Ejemplos de preguntas:</h3>
            <div class="ejemplo-item" onclick="usarEjemplo('productos con bajo stock')">📦 productos con bajo stock</div>
            <div class="ejemplo-item" onclick="usarEjemplo('productos más vendidos')">🏆 productos más vendidos</div>
            <div class="ejemplo-item" onclick="usarEjemplo('mejores clientes')">👥 mejores clientes</div>
            <div class="ejemplo-item" onclick="usarEjemplo('últimas ventas')">💰 últimas ventas</div>
            <div class="ejemplo-item" onclick="usarEjemplo('ventas por mes')">📅 ventas por mes</div>
            <div class="ejemplo-item" onclick="usarEjemplo('productos por categoria')">📋 productos por categoría</div>
        </div>
        
        <textarea id="pregunta" placeholder="Escribe tu pregunta aquí..."></textarea>
        <br><br>
        <button onclick="consultar()">🔍 Consultar</button>
        
        <div id="loading" class="loading">⏳ Procesando...</div>
        <div id="resultado" class="resultado"></div>
    </div>
    
    <script>
        function usarEjemplo(texto) {
            document.getElementById('pregunta').value = texto;
        }
        
        async function consultar() {
            const pregunta = document.getElementById('pregunta').value;
            if (!pregunta) {
                alert('Escribe una pregunta');
                return;
            }
            
            document.getElementById('loading').style.display = 'block';
            document.getElementById('resultado').innerHTML = '';
            
            try {
                const response = await fetch('/consultar', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({pregunta: pregunta})
                });
                
                const data = await response.json();
                
                if (data.error) {
                    document.getElementById('resultado').innerHTML = `<pre style="color: red;">❌ ${data.error}</pre>`;
                } else {
                    document.getElementById('resultado').innerHTML = `<pre>${data.resultado}</pre>`;
                }
            } catch (error) {
                document.getElementById('resultado').innerHTML = `<pre style="color: red;">❌ Error: ${error}</pre>`;
            } finally {
                document.getElementById('loading').style.display = 'none';
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/consultar', methods=['POST'])
def consultar():
    data = request.json
    pregunta = data.get('pregunta', '')
    
    try:
        # Ejecutar el asistente
        resultado = subprocess.run(
            ['python3', 'asistente_bd.py', pregunta],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        return jsonify({'resultado': resultado.stdout})
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    print("🚀 Servidor web iniciado en http://localhost:5001")
    app.run(host='0.0.0.0', port=5001, debug=False)
