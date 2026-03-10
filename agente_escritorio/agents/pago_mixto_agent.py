"""
Agente para procesar pagos mixtos (múltiples métodos)
"""
from loguru import logger
from typing import List, Dict, Optional
from models.cuenta_empresa import CuentaEmpresaRepo

class PagoMixtoAgent:
    """Gestiona pagos con múltiples métodos"""
    
    def __init__(self, conn, venta_agent, cuenta_repo=None):
        self.conn = conn
        self.venta_agent = venta_agent
        self.cuenta_repo = cuenta_repo or CuentaEmpresaRepo(conn)
        
        self.pagos = []  # Lista de pagos acumulados
        self.total_pendiente_usd = 0
        self.total_venta_usd = 0
        self.tasa_cambio = venta_agent.tasa_cambio
        
        logger.info("✅ PagoMixtoAgent inicializado")
    
    def iniciar_pago_mixto(self, total_venta_usd: float):
        """Inicia un nuevo pago mixto"""
        self.pagos = []
        self.total_venta_usd = total_venta_usd
        self.total_pendiente_usd = total_venta_usd
        logger.info(f"💰 Iniciando pago mixto - Total: ${total_venta_usd:.2f}")
        return {
            'total': total_venta_usd,
            'pendiente': total_venta_usd,
            'pagos': []
        }
    
    def agregar_pago(self, metodo: str, monto: float, moneda: str = 'USD', 
                     referencia: str = None, idcuenta_destino: int = None,
                     telefono_cliente: str = None) -> Dict:
        """
        Agrega un pago parcial
        Args:
            metodo: 'EFECTIVO_BS', 'EFECTIVO_USD', 'TARJETA_BS', 
                   'TARJETA_USD', 'PAGO_MOVIL', 'TRANSFERENCIA'
            monto: Cantidad pagada en la moneda especificada
            moneda: 'BS' o 'USD'
            referencia: Número de referencia (para Pago Móvil/Transferencia)
            idcuenta_destino: ID de la cuenta que recibe el pago
            telefono_cliente: Teléfono del cliente (para Pago Móvil)
        """
        # Convertir monto a USD si es necesario
        if moneda == 'BS':
            monto_usd = monto / self.tasa_cambio
        else:
            monto_usd = monto
        
        # Validar que no exceda el pendiente
        if monto_usd > self.total_pendiente_usd + 0.01:  # tolerancia
            return {
                'success': False,
                'error': f"El monto ${monto_usd:.2f} excede el pendiente ${self.total_pendiente_usd:.2f}"
            }
        
        # Obtener configuración de pagos
        config_pagos = self.venta_agent.obtener_configuracion_pagos()
        
        # Calcular IGTF si aplica
        igtf_aplica = False
        igtf_monto = 0
        if metodo == 'TARJETA_USD' and config_pagos.get('igtf_activo') and config_pagos.get('igtf_aplica_tarjeta_usd'):
            igtf_aplica = True
            igtf_porcentaje = config_pagos.get('igtf_porcentaje', 3.0)
            igtf_monto = monto_usd * (igtf_porcentaje / 100)
        
        # Calcular comisión si aplica
        comision_monto = 0
        if 'TARJETA' in metodo:
            if metodo == 'TARJETA_USD' and config_pagos['comision_usd']['activo']:
                comision_porcentaje = config_pagos['comision_usd']['porcentaje']
            elif metodo == 'TARJETA_BS' and config_pagos['comision_bs']['activo']:
                comision_porcentaje = config_pagos['comision_bs']['porcentaje']
            else:
                comision_porcentaje = config_pagos.get('comision_tarjeta', 2.5)
            
            comision_monto = (monto_usd + igtf_monto) * (comision_porcentaje / 100)
        
        # Crear registro de pago
        pago = {
            'metodo': metodo,
            'monto_usd': monto_usd,
            'monto_con_igtf': monto_usd + igtf_monto,
            'moneda_original': moneda,
            'monto_original': monto,
            'igtf_aplicado': igtf_aplica,
            'igtf_monto': igtf_monto,
            'comision_monto': comision_monto,
            'neto': monto_usd + igtf_monto - comision_monto,
            'referencia': referencia,
            'idcuenta_destino': idcuenta_destino,
            'telefono_cliente': telefono_cliente
        }
        
        self.pagos.append(pago)
        self.total_pendiente_usd -= monto_usd
        
        logger.info(f"✅ Pago agregado: {metodo} ${monto_usd:.2f}")
        return {
            'success': True,
            'pendiente': self.total_pendiente_usd,
            'pago': pago
        }
    
    def puede_confirmar(self) -> bool:
        """Verifica si el total está cubierto"""
        return abs(self.total_pendiente_usd) < 0.01
    
    def confirmar_pagos(self) -> Dict:
        """Confirma todos los pagos y procesa la venta"""
        if not self.puede_confirmar():
            return {
                'success': False,
                'error': f"Faltan ${self.total_pendiente_usd:.2f} por pagar"
            }
        
        try:
            cursor = self.conn.cursor()
            idventa = None
            
            # Procesar cada pago
            for pago in self.pagos:
                # Calcular monto en Bs. para guardar en BD
                monto_bs = pago['monto_usd'] * self.tasa_cambio
                
                if idventa is None:
                    # Primer pago - crear la venta
                    resultado = self.venta_agent.procesar_venta(
                        tipo_pago=pago['metodo'],
                        pago_info={
                            'moneda': pago['moneda_original'],
                            'monto_recibido': pago['monto_original']
                        }
                    )
                    if not resultado['success']:
                        return resultado
                    idventa = resultado['idventa']
                
                # Guardar detalle del pago
                cursor.execute("""
                    INSERT INTO venta_pago_detalle 
                    (idventa, metodo_pago, monto_bs, moneda_original, 
                     monto_original_usd, idcuenta_destino, referencia_cliente,
                     telefono_cliente, igtf_aplicado, igtf_monto, 
                     comision_banco, neto_parcial)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    idventa,
                    pago['metodo'],
                    monto_bs,
                    pago['moneda_original'],
                    pago['monto_original'] if pago['moneda_original'] == 'USD' else None,
                    pago['idcuenta_destino'],
                    pago['referencia'],
                    pago['telefono_cliente'],
                    1 if pago['igtf_aplicado'] else 0,
                    pago['igtf_monto'] * self.tasa_cambio if pago['igtf_aplicado'] else None,
                    pago['comision_monto'] * self.tasa_cambio,
                    pago['neto'] * self.tasa_cambio
                ))
            
            self.conn.commit()
            logger.success(f"✅ Venta mixta #{idventa} procesada con {len(self.pagos)} pagos")
            
            return {
                'success': True,
                'idventa': idventa,
                'total_pagos': len(self.pagos),
                'totales': {
                    'usd': self.total_venta_usd,
                    'bs': self.total_venta_usd * self.tasa_cambio
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Error confirmando pagos: {e}")
            self.conn.rollback()
            return {'success': False, 'error': str(e)}
    
    def cancelar(self):
        """Cancela el pago mixto"""
        self.pagos = []
        self.total_pendiente_usd = 0
        logger.info("❌ Pago mixto cancelado")
