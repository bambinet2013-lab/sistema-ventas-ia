"""
Agente de Ventas - Versión final con estado corregido
"""
import sys
from pathlib import Path
from datetime import datetime
sys.path.append(str(Path(__file__).parent.parent.parent))

from loguru import logger
from core.database import Database
from agents.cliente_agent import ClienteAgent
from agents.articulo_agent import ArticuloAgent

class VentaAgent:
    def __init__(self, usuario):
        self.usuario = usuario
        self.db = Database()
        self.conn = self.db.get_connection()
        
        self.cliente_agent = ClienteAgent()
        self.articulo_agent = ArticuloAgent()
        
        self.carrito = []
        self.cliente_actual = None
        self.es_consumidor_final = True
        self.tasa_cambio = self._obtener_tasa_cambio()
        
        logger.info("✅ VentaAgent inicializado")
    
    def _obtener_tasa_cambio(self):
        try:
            from capa_negocio.tasa_service import TasaService
            tasa_service = TasaService()
            return tasa_service.obtener_tasa_del_dia('USD') or 400.00
        except:
            return 400.00
    
    def iniciar_venta(self, es_consumidor_final=True, cliente_data=None):
        self.carrito = []
        self.es_consumidor_final = es_consumidor_final
        
        if es_consumidor_final:
            self.cliente_actual = self.cliente_agent.obtener_consumidor_final()
            logger.info(f"👤 Venta a CONSUMIDOR FINAL")
        return True
    
    def buscar_producto(self, busqueda):
        # Por código
        producto = self.articulo_agent.buscar_por_codigo(busqueda)
        if producto:
            return producto
        
        # Por nombre
        resultados = self.articulo_agent.buscar_por_nombre(busqueda)
        if resultados:
            return resultados[0]
        
        return None
    
    def agregar_producto(self, producto, cantidad=1):
        print(f"\n🔍 AGREGAR PRODUCTO - RECIBIDO: {producto}")
        
        if not producto:
            print("❌ Producto vacío")
            return False
        
        idarticulo = producto.get('idarticulo')
        if not idarticulo:
            print("❌ Producto sin ID")
            return False
        
        nombre = producto.get('nombre')
        if not nombre:
            print("❌ Producto sin nombre")
            return False
        
        precio = producto.get('precio') or producto.get('precio_venta') or 0
        if precio <= 0:
            print(f"❌ Precio inválido: {precio}")
            return False
        
        stock_actual = producto.get('stock_actual') or producto.get('stock') or 0
        print(f"📊 Stock actual: {stock_actual}")
        
        if stock_actual < cantidad:
            print(f"⚠️ Stock insuficiente (tiene: {stock_actual}, pide: {cantidad})")
            return False
        
        if self.es_consumidor_final:
            subtotal = precio * cantidad
            iva = 0
            print(f"🧾 Consumidor Final - Precio: ${precio}, Subtotal: ${subtotal}")
        else:
            base = precio / 1.16
            iva = base * 0.16 * cantidad
            subtotal = base * cantidad
            print(f"🏢 Cliente Registrado - Base: ${base:.2f}, IVA: ${iva:.2f}")
        
        item = {
            'idarticulo': idarticulo,
            'nombre': nombre,
            'cantidad': cantidad,
            'precio_unitario': precio,
            'subtotal': subtotal,
            'iva': iva,
            'total_linea': subtotal + iva
        }
        
        self.carrito.append(item)
        print(f"✅ Producto AGREGADO: {cantidad} x {nombre}")
        print(f"📦 Carrito ahora tiene {len(self.carrito)} productos")
        print(f"🧾 Item: {item}")
        
        return True
    
    def quitar_producto(self, indice):
        if 0 <= indice < len(self.carrito):
            producto = self.carrito.pop(indice)
            print(f"➖ {producto['nombre']} eliminado del carrito")
            return True
        return False
    
    def calcular_totales(self):
        subtotal = sum(item['subtotal'] for item in self.carrito)
        iva = sum(item['iva'] for item in self.carrito)
        total = subtotal + iva
        
        return {
            'subtotal_usd': round(subtotal, 2),
            'iva_usd': round(iva, 2),
            'total_usd': round(total, 2),
            'tasa_bs': self.tasa_cambio,
            'total_bs': round(total * self.tasa_cambio, 2),
            'items': len(self.carrito)
        }
    
    def _generar_numero_comprobante(self):
        """Genera número de comprobante único de 7 dígitos"""
        from datetime import datetime
        cursor = self.conn.cursor()
        
        fecha = datetime.now().strftime('%y%m%d')
        cursor.execute("""
            SELECT MAX(CAST(numero_comprobante AS INT)) 
            FROM venta 
            WHERE numero_comprobante LIKE ?
        """, (f"{fecha}%",))
        
        row = cursor.fetchone()
        ultimo = row[0] if row[0] else int(f"{fecha}0")
        nuevo = ultimo + 1
        return str(nuevo).zfill(7)
    
    def procesar_venta(self):
        if not self.carrito:
            return {'success': False, 'error': 'Carrito vacío'}
        
        try:
            cursor = self.conn.cursor()
            totales = self.calcular_totales()
            
            fecha = datetime.now()
            serie = 'A001'
            numero = self._generar_numero_comprobante()
            
            cursor.execute("""
                INSERT INTO venta 
                (idcliente, idtrabajador, fecha, tipo_comprobante, serie, 
                 numero_comprobante, igv, estado, fecha_hora, moneda, 
                 tasa_cambio, monto_bs, monto_divisa)
                OUTPUT INSERTED.idventa
                VALUES (?, ?, ?, 'BOLETA', ?, ?, ?, 'REGISTRADO', ?, 'USD', ?, ?, ?)
            """, (
                self.cliente_actual,
                self.usuario.idtrabajador,
                fecha.date(),
                serie,
                numero,
                totales['iva_usd'],
                fecha,
                self.tasa_cambio,
                totales['total_bs'],
                totales['total_usd']
            ))
            
            row = cursor.fetchone()
            idventa = row[0]
            
            for item in self.carrito:
                cursor.execute("""
                    INSERT INTO detalle_venta 
                    (idventa, idarticulo, cantidad, precio_venta)
                    VALUES (?, ?, ?, ?)
                """, (idventa, item['idarticulo'], item['cantidad'], item['precio_unitario']))
            
            self.conn.commit()
            self.carrito = []
            
            logger.success(f"✅ Venta #{idventa} procesada - Total: ${totales['total_usd']:.2f}")
            
            return {'success': True, 'idventa': idventa, 'totales': totales}
            
        except Exception as e:
            self.conn.rollback()
            logger.error(f"❌ Error procesando venta: {e}")
            return {'success': False, 'error': str(e)}
    
    def obtener_historial(self, limite=20):
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT TOP (?) v.idventa, v.fecha, v.monto_divisa, v.monto_bs,
                       ISNULL(c.nombre + ' ' + c.apellidos, 'CONSUMIDOR FINAL') as cliente,
                       COUNT(dv.idarticulo) as productos
                FROM venta v
                LEFT JOIN cliente c ON v.idcliente = c.idcliente
                LEFT JOIN detalle_venta dv ON v.idventa = dv.idventa
                GROUP BY v.idventa, v.fecha, v.monto_divisa, v.monto_bs, c.nombre, c.apellidos
                ORDER BY v.idventa DESC
            """, (limite,))
            
            ventas = []
            for row in cursor.fetchall():
                ventas.append({
                    'idventa': row[0],
                    'fecha': row[1],
                    'monto_usd': float(row[2] or 0),
                    'monto_bs': float(row[3] or 0),
                    'cliente': row[4],
                    'productos': row[5]
                })
            
            return ventas
        except Exception as e:
            logger.error(f"❌ Error obteniendo historial: {e}")
            return []
    
    def cerrar(self):
        try:
            self.cliente_agent.cerrar()
            self.articulo_agent.cerrar()
            self.db.close()
        except:
            pass
