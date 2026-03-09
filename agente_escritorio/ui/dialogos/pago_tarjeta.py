"""
Diálogo para procesar pago con tarjeta con soporte para IGTF.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from loguru import logger

class PagoTarjetaDialog:
    def __init__(self, parent, total_usd, total_bs, tasa_cambio, config_empresa, totales_fiscales=None):
        self.parent = parent
        self.total_usd = total_usd
        self.total_bs = total_bs
        self.tasa_cambio = tasa_cambio
        self.config = config_empresa
        self.totales_fiscales = totales_fiscales
        
        self.resultado = None
        
        # Crear ventana
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Pago con Tarjeta")
        self.dialog.geometry("450x550")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.resizable(False, False)
        
        # Variables
        self.moneda_var = tk.StringVar(value="USD")

        # Crear interfaz
        self.setup_ui()
        
        # Bind para cambios de moneda
        self.moneda_var.trace('w', lambda *args: self.calcular_montos())
        
        # Actualizar UI inicial
        self.calcular_montos()
        
    def setup_ui(self):
        """Crea todos los elementos de la interfaz."""
        # Título
        tk.Label(self.dialog, text="💳 PAGO CON TARJETA", 
                font=('Helvetica', 14, 'bold')).pack(pady=10)
        
        # === MONEDA ===
        moneda_frame = tk.LabelFrame(self.dialog, text="Moneda de Pago", padx=10, pady=5)
        moneda_frame.pack(fill='x', padx=20, pady=5)
        
        tk.Radiobutton(moneda_frame, text="Dólares (USD)", variable=self.moneda_var, 
                      value="USD").pack(anchor='w')
        tk.Radiobutton(moneda_frame, text="Bolívares (Bs.)", variable=self.moneda_var, 
                      value="BS").pack(anchor='w')
  
        # === DETALLE DE PAGO ===
        detalle_frame = tk.LabelFrame(self.dialog, text="Detalle de Pago", padx=10, pady=5)
        detalle_frame.pack(fill='x', padx=20, pady=5)
        
        # Labels que se actualizarán
        self.label_total = tk.Label(detalle_frame, text="", font=('Helvetica', 11))
        self.label_total.pack(anchor='w', pady=2)
        
        self.label_igtf = tk.Label(detalle_frame, text="", font=('Helvetica', 10))
        # No se packea aún
        
        self.label_total_pagar = tk.Label(detalle_frame, text="", font=('Helvetica', 11, 'bold'))
        self.label_total_pagar.pack(anchor='w', pady=5)
        
        self.label_comision = tk.Label(detalle_frame, text="", font=('Helvetica', 10))
        self.label_comision.pack(anchor='w', pady=2)
        
        self.label_neto = tk.Label(detalle_frame, text="", font=('Helvetica', 11, 'bold'))
        self.label_neto.pack(anchor='w', pady=5)
        
        # === REFERENCIA ===
        ref_frame = tk.LabelFrame(self.dialog, text="Referencia (opcional)", padx=10, pady=5)
        ref_frame.pack(fill='x', padx=20, pady=5)
        
        self.entry_referencia = tk.Entry(ref_frame, width=30)
        self.entry_referencia.pack(pady=5)
        
        # === BOTONES (SIEMPRE VISIBLES) ===
        btn_frame = tk.Frame(self.dialog)
        btn_frame.pack(pady=20)
        
        tk.Button(btn_frame, text="Confirmar Pago", command=self.procesar,
                 bg='#27ae60', fg='white', font=('Helvetica', 12), width=15).pack(side='left', padx=5)
        
        tk.Button(btn_frame, text="Cancelar", command=self.dialog.destroy,
                 bg='#e74c3c', fg='white', font=('Helvetica', 12), width=15).pack(side='left', padx=5)
 
    def calcular_montos(self):
        """Calcula los montos aplicando IGTF automáticamente según configuración."""
        moneda = self.moneda_var.get()
        
        # Calcular montos base
        if moneda == 'USD':
            monto_base = self.total_usd
            moneda_simbolo = '$'
        else:
            monto_base = self.total_bs
            moneda_simbolo = 'Bs.'
        
        igtf_porcentaje = self.config.get('igtf_porcentaje', 3.0)
        comision_porcentaje = self.config.get('comision_tarjeta', 2.5)
        
        # 🔥 DECISIÓN AUTOMÁTICA: IGTF aplica si:
        # - La moneda es USD
        # - IGTF está activo
        # - Está configurado para tarjetas USD
        igtf_aplica = (
            moneda == 'USD' and 
            self.config.get('igtf_activo', False) and 
            self.config.get('igtf_aplica_tarjeta_usd', False)
        )
        
        # Aplicar IGTF automáticamente si corresponde
        if igtf_aplica:
            igtf_monto = monto_base * (igtf_porcentaje / 100)
            monto_con_igtf = monto_base + igtf_monto
        else:
            igtf_monto = 0
            monto_con_igtf = monto_base
        
        # Aplicar comisión
        comision_monto = monto_con_igtf * (comision_porcentaje / 100)
        neto = monto_con_igtf - comision_monto
        
        # Guardar para resultado
        self.igtf_monto = igtf_monto
        self.comision_monto = comision_monto
        self.neto = neto
        self.monto_con_igtf = monto_con_igtf
        
        # Actualizar labels
        self.label_total.config(text=f"Total venta: {moneda_simbolo}{monto_base:.2f}")
        
        if igtf_aplica:
            self.label_igtf.config(text=f"+ IGTF ({igtf_porcentaje}%): {moneda_simbolo}{igtf_monto:.2f}")
            self.label_igtf.pack(anchor='w', pady=2)
        else:
            self.label_igtf.pack_forget()
        
        self.label_total_pagar.config(text=f"💰 TOTAL A PAGAR: {moneda_simbolo}{monto_con_igtf:.2f}")
        self.label_comision.config(text=f"- Comisión ({comision_porcentaje}%): {moneda_simbolo}{comision_monto:.2f}")
        self.label_neto.config(text=f"🏦 LÍQUIDO A RECIBIR: {moneda_simbolo}{neto:.2f}")
    
    def procesar(self):
        """Procesa el pago."""
        moneda = self.moneda_var.get()
        
        # Determinar si IGTF aplicó (automático)
        igtf_aplico = (
            moneda == 'USD' and 
            self.config.get('igtf_activo', False) and 
            self.config.get('igtf_aplica_tarjeta_usd', False)
        )
        
        self.resultado = {
            'moneda': moneda,
            'monto_total': self.monto_con_igtf,
            'monto_original_usd': self.monto_con_igtf if moneda == 'USD' else self.monto_con_igtf / self.tasa_cambio,
            'igtf_aplicado': igtf_aplico,
            'igtf_monto': self.igtf_monto if igtf_aplico else 0,
            'igtf_porcentaje': self.config.get('igtf_porcentaje', 3.0),
            'comision_monto': self.comision_monto,
            'neto': self.neto,
            'referencia': self.entry_referencia.get().strip()
        }
        
        logger.info(f"💳 Pago con tarjeta procesado: {self.resultado}")
        self.dialog.destroy()
    
    def show(self):
        """Muestra el diálogo y espera resultado."""
        self.dialog.wait_window()
        return self.resultado
