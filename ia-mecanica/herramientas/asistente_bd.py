#!/usr/bin/env python3
"""
Asistente de Base de Datos en Lenguaje Natural
Uso: python3 asistente_bd.py "tu pregunta en español"
"""

import subprocess
import json
import sys
import requests
from datetime import datetime

# Configuración
API_BD = "http://localhost:5000/consultar"
AGENTE_PROMPT = """
Eres un experto en SQL y en la base de datos SistemaVentas.
Tu tarea es convertir preguntas en lenguaje natural a consultas SQL válidas.

Tablas disponibles:
- venta (idventa, fecha, idcliente, idtrabajador, monto_divisa, monto_bs, tipo_pago, estado)
- detalle_venta (iddetalle, idventa, idarticulo, cantidad, precio_venta)
- articulo (idarticulo, nombre, stock_actual, precio)
- cliente (idcliente, nombre, apellidos)
- venta_pago_detalle (idpago, idventa, metodo_pago, monto_bs, referencia_cliente)

REGLAS IMPORTANTES:
1. Solo genera consultas SELECT
2. Usa TOP en lugar de LIMIT (SQL Server)
3. Las fechas están en formato YYYY-MM-DD
4. Los montos en divisa están en USD

Ejemplos:
P: "¿Cuántas ventas hay?"
R: SELECT COUNT(*) as total FROM venta

P: "Últimas 5 ventas"
R: SELECT TOP 5 * FROM venta ORDER BY idventa DESC

P: "Ventas de ayer"
R: SELECT COUNT(*) FROM venta WHERE fecha = '2026-03-10'

Responde SOLO con la consulta SQL, sin explicaciones adicionales.
"""

def consultar_agente(pregunta):
    """Envía la pregunta al agente y obtiene la consulta SQL"""
    
    # Aquí deberías conectar con tu agente de LibreChat
    # Por ahora, usaremos un enfoque simplificado
    print(f"📝 Procesando: {pregunta}")
    
    # SIMULACIÓN: En un sistema real, aquí llamarías a la API del agente
    # Por ahora, usaremos un mapeo simple para demostración
    respuesta_sql = generar_sql_simple(pregunta)
    
    return respuesta_sql

def obtener_ventas_por_mes():
    return """
    SELECT 
        YEAR(fecha) as año,
        MONTH(fecha) as mes,
        COUNT(*) as total_ventas,
        SUM(monto_divisa) as total_usd
    FROM venta
    GROUP BY YEAR(fecha), MONTH(fecha)
    ORDER BY año DESC, mes DESC
    """

def obtener_productos_por_categoria():
    return """
    SELECT 
        c.nombre as categoria,
        COUNT(a.idarticulo) as total_productos,
        AVG(a.precio_venta) as precio_promedio
    FROM categoria c
    LEFT JOIN articulo a ON c.idcategoria = a.idcategoria
    GROUP BY c.nombre
    ORDER BY total_productos DESC
    """

def obtener_ventas_por_hora():
    return """
    SELECT 
        DATEPART(HOUR, fecha_hora) as hora,
        COUNT(*) as ventas,
        AVG(monto_divisa) as promedio
    FROM venta
    GROUP BY DATEPART(HOUR, fecha_hora)
    ORDER BY hora
    """

def generar_sql_simple(pregunta):
    """Genera SQL para preguntas comunes basado en la estructura real de la BD"""
    p = pregunta.lower()
    
    # Ventas
    if "cuantas ventas" in p or "total de ventas" in p:
        return "SELECT COUNT(*) as total_ventas FROM venta"
    
    elif "ultimas" in p and "ventas" in p:
        if "5" in p:
            return "SELECT TOP 5 * FROM venta ORDER BY idventa DESC"
        else:
            return "SELECT TOP 10 * FROM venta ORDER BY idventa DESC"
    
    elif "ventas de ayer" in p:
        from datetime import datetime, timedelta
        ayer = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        return f"SELECT COUNT(*) as ventas_ayer FROM venta WHERE CAST(fecha AS DATE) = '{ayer}'"
    
    # Productos y stock (CORREGIDO - usa kardex)
    elif "productos" in p and "stock" in p:
        if "bajo" in p:
            return """
            SELECT a.idarticulo, a.nombre, SUM(k.cantidad) as stock_actual
            FROM articulo a
            JOIN kardex k ON a.idarticulo = k.idarticulo
            GROUP BY a.idarticulo, a.nombre
            HAVING SUM(k.cantidad) < 10
            ORDER BY stock_actual
            """
        else:
            return """
            SELECT TOP 10 a.idarticulo, a.nombre, SUM(k.cantidad) as stock_actual
            FROM articulo a
            JOIN kardex k ON a.idarticulo = k.idarticulo
            GROUP BY a.idarticulo, a.nombre
            ORDER BY stock_actual DESC
            """
    
    # Productos más vendidos (mejorado)
    elif any(x in p for x in ["mas vendidos", "más vendidos", "top productos", "productos top", "productos mas vendidos"]):
        return """
        SELECT TOP 10 a.nombre, SUM(dv.cantidad) as total_vendido
        FROM detalle_venta dv
        JOIN articulo a ON dv.idarticulo = a.idarticulo
        GROUP BY a.nombre
        ORDER BY total_vendido DESC
        """
    
    # Clientes con más compras
    elif "mejores clientes" in p or "clientes" in p and "compras" in p:
        return """
        SELECT TOP 10 c.nombre, c.apellidos, COUNT(v.idventa) as num_compras, SUM(v.monto_divisa) as total_gastado
        FROM cliente c
        JOIN venta v ON c.idcliente = v.idcliente
        GROUP BY c.nombre, c.apellidos
        ORDER BY total_gastado DESC
        """
    
    # Pagos por método
    elif "pagos" in p and "metodo" in p:
        return """
        SELECT metodo_pago, COUNT(*) as cantidad, SUM(monto_bs) as total_bs
        FROM venta_pago_detalle
        GROUP BY metodo_pago
        ORDER BY total_bs DESC
        """
    
    # Por defecto, consulta simple de ventas
    return "SELECT TOP 10 * FROM venta ORDER BY idventa DESC"

def ejecutar_sql(consulta):
    """Ejecuta la consulta SQL contra la API"""
    try:
        response = requests.post(
            API_BD,
            json={"consulta": consulta},
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def formatear_resultado(resultado, pregunta):
    """Formatea el resultado de forma MUY legible"""
    if "error" in resultado:
        return f"\n❌ Error: {resultado['error']}\n"
    
    if not resultado.get('success'):
        return f"\n❌ Error en la consulta\n"
    
    datos = resultado.get('resultados', [])
    
    if not datos:
        return "\n📭 No se encontraron resultados.\n"
    
    # Determinar el tipo de consulta para formatear mejor
    p = pregunta.lower()
    
    # Formato para productos con bajo stock
    if "bajo stock" in p or "stock bajo" in p:
        output = "\n📦 **PRODUCTOS CON BAJO STOCK**\n"
        output += "═" * 60 + "\n"
        output += f"{'ID':<8} {'Producto':<35} {'Stock':>10}\n"
        output += "─" * 60 + "\n"
        for item in datos:
            output += f"{item.get('idarticulo', ''):<8} {item.get('nombre', '')[:35]:<35} {item.get('stock_actual', 0):>10}\n"
        output += "─" * 60 + "\n"
        output += f"Total: {len(datos)} productos críticos\n"
        return output
    
    # Formato para productos más vendidos
    elif "mas vendidos" in p or "más vendidos" in p:
        output = "\n🏆 **PRODUCTOS MÁS VENDIDOS**\n"
        output += "═" * 60 + "\n"
        output += f"{'#':<4} {'Producto':<40} {'Cantidad':>12}\n"
        output += "─" * 60 + "\n"
        for i, item in enumerate(datos, 1):
            output += f"{i:<4} {item.get('nombre', '')[:40]:<40} {item.get('total_vendido', 0):>12}\n"
        return output
    
    # Formato para mejores clientes
    elif "mejores clientes" in p or "clientes" in p:
        output = "\n👥 **MEJORES CLIENTES**\n"
        output += "═" * 60 + "\n"
        output += f"{'#':<4} {'Cliente':<30} {'Compras':>10} {'Total $':>12}\n"
        output += "─" * 60 + "\n"
        for i, item in enumerate(datos, 1):
            nombre = f"{item.get('nombre', '')} {item.get('apellidos', '')}".strip()
            output += f"{i:<4} {nombre[:30]:<30} {item.get('num_compras', 0):>10} ${item.get('total_gastado', 0):>11.2f}\n"
        return output
    
    # Formato para ventas recientes
    elif "ultimas ventas" in p or "últimas ventas" in p:
        output = "\n💰 **ÚLTIMAS VENTAS**\n"
        output += "═" * 70 + "\n"
        output += f"{'ID':<6} {'Fecha':<12} {'Cliente':<20} {'Total $':>10} {'Tipo Pago':<15}\n"
        output += "─" * 70 + "\n"
        for item in datos[:10]:  # Mostrar solo 10
            fecha = item.get('fecha', '')[:10] if item.get('fecha') else ''
            output += f"{item.get('idventa', ''):<6} {fecha:<12} {'N/A':<20} ${float(item.get('monto_divisa', 0)):>9.2f} {item.get('tipo_pago', '')[:15]:<15}\n"
        return output
    
    # Formato genérico para otros resultados
    else:
        import pandas as pd
        df = pd.DataFrame(datos)
        output = f"\n📊 **RESULTADOS** ({len(datos)} filas)\n"
        output += "═" * 80 + "\n"
        output += df.to_string(index=False, max_colwidth=30)
        return output

def main():
    if len(sys.argv) < 2:
        print("Uso: python3 asistente_bd.py 'tu pregunta en español'")
        print("\nEjemplos:")
        print("  python3 asistente_bd.py '¿cuántas ventas hay?'")
        print("  python3 asistente_bd.py 'últimas 5 ventas'")
        print("  python3 asistente_bd.py 'productos con bajo stock'")
        return
    
    pregunta = ' '.join(sys.argv[1:])
    
    # Paso 1: Generar SQL
    print("🤖 Consultando al agente...")
    consulta_sql = generar_sql_simple(pregunta)
    print(f"📝 SQL generado: {consulta_sql}")
    
    # Paso 2: Ejecutar SQL
    print("⚡ Ejecutando consulta...")
    resultado = ejecutar_sql(consulta_sql)
    
    # Paso 3: Mostrar resultado
    print("\n" + formatear_resultado(resultado, pregunta))

if __name__ == "__main__":
    main()
