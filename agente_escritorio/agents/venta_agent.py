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
        
        # NUEVO: Inicializar agente de Cashea
        from agente_escritorio.agents.cashea_agent import CasheaAgent
        self.cashea_agent = CasheaAgent()
        
        self.carrito = []
        self.cliente_actual = None
        self.es_consumidor_final = True
        self.tasa_cambio = self._obtener_tasa_cambio()
        
        logger.info("✅ VentaAgent inicializado")
        
    def obtener_configuracion_empresa(self, id_empresa=1):
        """Obtiene toda la configuración de una empresa desde la BD"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT modo_operacion, pos_activo, efectivo_usd_activo, redondeo_vuelto, monto_minimo_usd
                FROM configuracion_operacion 
                WHERE id_empresa = ?
            """, (id_empresa,))
            row = cursor.fetchone()
            if row:
                config = {
                    'modo': row[0],
                    'pos_activo': bool(row[1]),
                    'efectivo_usd_activo': bool(row[2]),
                    'redondeo_vuelto': row[3],
                    'monto_minimo_usd': float(row[4]) if row[4] else 0
                }
                logger.info(f"📋 Configuración empresa {id_empresa}: {config}")
                return config
            else:
                # Valores por defecto si no hay registro
                logger.warning(f"⚠️ No hay configuración para empresa {id_empresa}, usando valores por defecto")
                return {
                    'modo': 'hibrido',
                    'pos_activo': False,
                    'efectivo_usd_activo': False,
                    'redondeo_vuelto': 0,
                    'monto_minimo_usd': 0
                }
        except Exception as e:
            logger.error(f"❌ Error obteniendo configuración: {e}")
            return {
                'modo': 'hibrido',
                'pos_activo': False,
                'efectivo_usd_activo': False,
                'redondeo_vuelto': 0,
                'monto_minimo_usd': 0
            }        
 
    def obtener_configuracion_pagos(self, id_empresa=1):
        """Obtiene configuración específica para pagos (comisiones, IGTF)"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT comision_tarjeta, igtf_activo, igtf_porcentaje,
                       igtf_aplica_efectivo_usd, igtf_aplica_tarjeta_usd,
                       igtf_aplica_transferencia_usd
                FROM configuracion_operacion 
                WHERE id_empresa = ?
            """, (id_empresa,))
            row = cursor.fetchone()
            if row:
                return {
                    'comision_tarjeta': float(row[0]) if row[0] else 2.5,
                    'igtf_activo': bool(row[1]),
                    'igtf_porcentaje': float(row[2]) if row[2] else 3.0,
                    'igtf_aplica_efectivo_usd': bool(row[3]),
                    'igtf_aplica_tarjeta_usd': bool(row[4]),
                    'igtf_aplica_transferencia_usd': bool(row[5])
                }
            else:
                return {
                    'comision_tarjeta': 2.5,
                    'igtf_activo': False,
                    'igtf_porcentaje': 3.0,
                    'igtf_aplica_efectivo_usd': True,
                    'igtf_aplica_tarjeta_usd': False,
                    'igtf_aplica_transferencia_usd': False
                }
        except Exception as e:
            logger.error(f"❌ Error obteniendo configuración de pagos: {e}")
            return {
                'comision_tarjeta': 2.5,
                'igtf_activo': False,
                'igtf_porcentaje': 3.0,
                'igtf_aplica_efectivo_usd': True,
                'igtf_aplica_tarjeta_usd': False,
                'igtf_aplica_transferencia_usd': False
            } 
 
    def obtener_modo_operacion(self, id_empresa=1):
        """Obtiene el modo de operación configurado para la empresa"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT modo_operacion, pos_activo FROM configuracion_operacion 
                WHERE id_empresa = ?
            """, (id_empresa,))
            row = cursor.fetchone()
            if row:
                modo = row[0]
                pos_activo = row[1]
                logger.info(f"🎯 Modo de operación: {modo}, POS activo: {pos_activo}")
                return {
                    'modo': modo,
                    'pos_activo': pos_activo
                }
            else:
                logger.warning("⚠️ No hay configuración, usando modo por defecto 'hibrido'")
                return {'modo': 'hibrido', 'pos_activo': False}
        except Exception as e:
            logger.error(f"❌ Error obteniendo modo de operación: {e}")
            return {'modo': 'hibrido', 'pos_activo': False} 
    
    def cashea_activo(self):
        """Retorna True si Cashea está activo y configurado"""
        if hasattr(self, 'cashea_agent'):
            return self.cashea_agent.esta_activo()
        return False    
    
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
        """
        Agrega un producto al carrito con su letra fiscal
        """
        print(f"\n🔍 AGREGAR PRODUCTO - RECIBIDO: {producto}")
        
        if not producto:
            print("❌ Producto vacío")
            return False
        
        # Obtener ID
        idarticulo = producto.get('idarticulo')
        if not idarticulo:
            print("❌ Producto sin ID")
            return False
        
        # Obtener nombre
        nombre = producto.get('nombre')
        if not nombre:
            print("❌ Producto sin nombre")
            return False
        
        # Obtener precio (puede venir como 'precio' o 'precio_venta')
        precio = producto.get('precio') or producto.get('precio_venta') or 0
        if precio <= 0:
            print(f"❌ Precio inválido: {precio}")
            return False
        
        # Obtener stock
        stock_actual = producto.get('stock_actual') or producto.get('stock') or 0
        print(f"📊 Stock actual: {stock_actual}")
        
        # Verificar stock
        if stock_actual < cantidad:
            print(f"⚠️ Stock insuficiente (tiene: {stock_actual}, pide: {cantidad})")
            return False
        
        # 🔥 Obtener letra fiscal del artículo
        letra = self.obtener_letra_fiscal(idarticulo)
        print(f"🏷️ Letra fiscal: {letra}")
        
        # Calcular según tipo de cliente
        if self.es_consumidor_final:
            subtotal = precio * cantidad
            iva = 0
            print(f"🧾 Consumidor Final - Precio: ${precio}, Subtotal: ${subtotal}")
        else:
            # Para empresas, separar base imponible e IVA
            id_impuesto = producto.get('id_impuesto', 2)
            if id_impuesto == 1:
                porcentaje_iva = 0.0
            elif id_impuesto == 2:
                porcentaje_iva = 0.16
            elif id_impuesto == 3:
                porcentaje_iva = 0.08
            elif id_impuesto == 4:
                porcentaje_iva = 0.31
            else:
                porcentaje_iva = 0.16
            
            base = precio / (1 + porcentaje_iva)
            iva = base * porcentaje_iva * cantidad
            subtotal = base * cantidad
            print(f"🏢 Cliente Registrado - Base: ${base:.2f}, IVA: ${iva:.2f}")
        
        item = {
            'idarticulo': idarticulo,
            'nombre': nombre,
            'letra': letra,  # ← NUEVO: Guardar letra fiscal
            'cantidad': cantidad,
            'precio_unitario': precio,
            'subtotal': subtotal,
            'iva': iva,
            'total_linea': subtotal + iva,
            'id_impuesto': producto.get('id_impuesto', 2)
        }
        
        self.carrito.append(item)
        print(f"✅ Producto AGREGADO: {cantidad} x {nombre} ({letra})")
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
    
    def obtener_letra_fiscal(self, idarticulo):
        """
        Obtiene la letra fiscal del artículo desde la base de datos.
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT i.letra_fiscal 
                FROM articulo a
                JOIN impuesto i ON a.id_impuesto = i.id_impuesto
                WHERE a.idarticulo = ?
            """, (idarticulo,))
            row = cursor.fetchone()
            return row[0] if row else 'G'  # Por defecto 'G' (General)
        except Exception as e:
            logger.error(f"❌ Error obteniendo letra fiscal para artículo {idarticulo}: {e}")
            return 'G'

    def calcular_totales_con_impuestos(self):
        """
        Calcula los totales de la venta desglosados fiscalmente.
        - exento: suma de productos con letra 'E'
        - base_gravada_usd: suma de productos gravados (precio con IVA incluido)
        - iva_usd: 16% de la base_gravada_usd
        - total_con_iva: exento + base_gravada_usd + iva_usd
        """
        exento = 0.0
        base_gravada = 0.0
        
        for item in self.carrito:
            precio_unitario = item['precio_unitario']
            cantidad = item['cantidad']
            idarticulo = item['idarticulo']
            letra = item.get('letra', self.obtener_letra_fiscal(idarticulo))
            
            item_total = precio_unitario * cantidad
            
            if letra == 'E':  # Exento
                exento += item_total
            else:  # Gravado (G, R, A)
                base_gravada += item_total
        
        # Calcular IVA sobre la base gravada
        iva = base_gravada * 0.16
        
        # Total con IVA
        total = exento + base_gravada + iva
        
        resultado = {
            'exento': round(exento, 2),
            'base_gravada_usd': round(base_gravada, 2),
            'iva_usd': round(iva, 2),
            'total_con_iva': round(total, 2)
        }
        
        logger.info(f"🧮 Cálculo fiscal: {resultado}")
        return resultado
    
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
    
    def procesar_venta(self, tipo_pago='EFECTIVO', datos_cashea=None, pago_info=None):
        """
        Procesa la venta aplicando IGTF y comisiones según configuración.
        """
        if not self.carrito:
            return {'success': False, 'error': 'Carrito vacío'}
        
        # Obtener configuración del modo de operación y pagos
        config = self.obtener_modo_operacion()
        modo = config['modo']
        
        config_pagos = self.obtener_configuracion_pagos(1)
        
        # Para consumidor final, el cliente puede ser None
        if not self.es_consumidor_final and not self.cliente_actual:
            return {'success': False, 'error': 'No hay cliente seleccionado'}
        
        try:
            cursor = self.conn.cursor()
            
            # Obtener totales fiscales base
            totales_base = self.calcular_totales_con_impuestos()
            tasa = self.tasa_cambio
            
            # Determinar si aplica IGTF
            igtf_aplicado = False
            igtf_monto = 0
            igtf_porcentaje = config_pagos['igtf_porcentaje']
            
            if config_pagos['igtf_activo'] and tipo_pago in ['EFECTIVO_USD', 'TARJETA_USD', 'TRANSFERENCIA_USD']:
                if tipo_pago == 'EFECTIVO_USD' and config_pagos['igtf_aplica_efectivo_usd']:
                    igtf_aplicado = True
                elif tipo_pago == 'TARJETA_USD' and config_pagos['igtf_aplica_tarjeta_usd']:
                    igtf_aplicado = True
                elif tipo_pago == 'TRANSFERENCIA_USD' and config_pagos['igtf_aplica_transferencia_usd']:
                    igtf_aplicado = True
            
            # Calcular montos finales con IGTF si aplica
            total_venta_usd = totales_base['total_con_iva']
            if igtf_aplicado:
                igtf_monto = total_venta_usd * (igtf_porcentaje / 100)
                total_venta_usd += igtf_monto
            
            # Calcular comisión bancaria (si aplica)
            comision_monto = 0
            if tipo_pago in ['TARJETA', 'TARJETA_USD', 'TARJETA_MANUAL']:
                comision_porcentaje = config_pagos['comision_tarjeta']
                comision_monto = total_venta_usd * (comision_porcentaje / 100)
            
            neto_negocio = total_venta_usd - comision_monto
            
            # Convertir a Bs. para auditoría
            total_bs = total_venta_usd * tasa
            neto_bs = neto_negocio * tasa
            
            fecha = datetime.now()
            serie = 'A001'
            numero = self._generar_numero_comprobante()
            
            # Preparar datos de Cashea
            cashea_ref = None
            cashea_ini = None
            cashea_cuotas = None
            cashea_com = None
            
            if datos_cashea:
                cashea_ref = datos_cashea.get('referencia')
                cashea_ini = datos_cashea.get('inicial')
                cashea_cuotas = datos_cashea.get('cuotas')
                cashea_com = datos_cashea.get('comision', self.cashea_agent.config.get('comision', 3.0) if hasattr(self, 'cashea_agent') else None)
            
            # Preparar datos de pago
            moneda_original = 'BS'
            monto_original_usd = None
            
            if pago_info:
                moneda_original = pago_info.get('moneda', 'BS')
                if moneda_original == 'USD':
                    monto_original_usd = pago_info.get('monto_recibido')
            
            # Calcular subtotal en Bs. (exento + base gravada convertido)
            subtotal_bs = (totales_base['exento'] + totales_base['base_gravada_usd']) * tasa
            
            # Insertar venta
            cursor.execute("""
                INSERT INTO venta 
                (idcliente, idtrabajador, fecha, tipo_comprobante, serie, 
                 numero_comprobante, igv, estado, fecha_hora, moneda, 
                 tasa_cambio, monto_bs, monto_divisa, tipo_pago,
                 subtotal_bs, exento_bs, base_gravada_bs, iva_bs,
                 moneda_original, monto_original_usd,
                 igtf_aplicado, igtf_monto, igtf_porcentaje,
                 comision_banco, neto_negocio,
                 cashea_referencia, cashea_inicial, cashea_cuotas, cashea_comision)
                OUTPUT INSERTED.idventa
                VALUES (?, ?, ?, 'BOLETA', ?, ?, ?, 'REGISTRADO', ?, 'USD', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                self.cliente_actual,
                self.usuario.idtrabajador,
                fecha.date(),
                serie,
                numero,
                totales_base['iva_usd'],
                fecha,
                tasa,
                total_bs,
                total_venta_usd,
                tipo_pago,
                subtotal_bs,
                totales_base['exento'] * tasa,
                totales_base['base_gravada_usd'] * tasa,
                totales_base['iva_usd'] * tasa,
                moneda_original,
                monto_original_usd,
                1 if igtf_aplicado else 0,
                igtf_monto * tasa if igtf_aplicado else None,
                igtf_porcentaje if igtf_aplicado else None,
                comision_monto,
                neto_negocio,
                cashea_ref,
                cashea_ini,
                cashea_cuotas,
                cashea_com
            ))
            
            row = cursor.fetchone()
            idventa = row[0]
            
            for item in self.carrito:
                cursor.execute("""
                    INSERT INTO detalle_venta 
                    (idventa, idarticulo, cantidad, precio_venta)
                    VALUES (?, ?, ?, ?)
                """, (idventa, item['idarticulo'], item['cantidad'], item['precio_unitario']))
                
                self._actualizar_stock(item['idarticulo'], item['cantidad'], idventa)
            
            self.conn.commit()
            self.carrito = []
            
            logger.success(f"✅ Venta #{idventa} procesada - Total: ${total_venta_usd:.2f} (Bs.{total_bs:.2f}) - {tipo_pago}")
            if igtf_aplicado:
                logger.info(f"   📊 IGTF {igtf_porcentaje}%: ${igtf_monto:.2f}")
            if comision_monto > 0:
                logger.info(f"   💳 Comisión: ${comision_monto:.2f}, Neto negocio: ${neto_negocio:.2f}")
            
            return {
                'success': True,
                'idventa': idventa,
                'totales': {
                    'usd': total_venta_usd,
                    'bs': total_bs,
                    'igtf': igtf_monto,
                    'comision': comision_monto,
                    'neto': neto_negocio
                }
            }
            
        except Exception as e:
            self.conn.rollback()
            logger.error(f"❌ Error procesando venta: {e}")
            return {'success': False, 'error': str(e)}
    
    def _actualizar_stock(self, idarticulo, cantidad, idventa):
        """Actualiza el stock en kardex por venta"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT TOP 1 stock_nuevo FROM kardex 
            WHERE idarticulo = ? 
            ORDER BY fecha_movimiento DESC
        """, (idarticulo,))
        
        row = cursor.fetchone()
        stock_anterior = row[0] if row else 0
        stock_nuevo = stock_anterior - cantidad
        
        cursor.execute("""
            INSERT INTO kardex 
            (idarticulo, fecha_movimiento, tipo_movimiento, documento_referencia,
             cantidad, precio_unitario, valor_total, stock_anterior, stock_nuevo)
            VALUES (?, GETDATE(), 'VENTA', ?, ?, 
                    (SELECT precio_venta FROM articulo WHERE idarticulo = ?),
                    ? * (SELECT precio_venta FROM articulo WHERE idarticulo = ?),
                    ?, ?)
        """, (
            idarticulo,
            f"VENTA-{idventa}",
            cantidad,
            idarticulo,
            cantidad,
            idarticulo,
            stock_anterior,
            stock_nuevo
        ))    
    
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
