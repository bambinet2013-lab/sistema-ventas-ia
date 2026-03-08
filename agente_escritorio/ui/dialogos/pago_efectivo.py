"""
Diálogo para procesar pago en efectivo con cálculo de vuelto.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from loguru import logger

class PagoEfectivoDialog:
    def __init__(self, parent, total_bs, total_usd, tasa_cambio, config_empresa, totales_fiscales=None):
        """
        Args:
            parent: Ventana padre.
            total_bs: Total a pagar en bolívares.
            total_usd: Total a pagar en dólares.
            tasa_cambio: Tasa de cambio USD/BS.
            config_empresa: Diccionario con configuración.
            totales_fiscales: Diccionario con desglose (subtotal, exento, base_gravada, iva, total)
        """
        self.parent = parent
        self.total_bs = total_bs
        self.total_usd = total_usd
        self.tasa_cambio = tasa_cambio
        self.config = config_empresa
        self.totales_fiscales = totales_fiscales  # ← NUEVO PARÁMETRO
        
        self.resultado = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Pago en Efectivo")
        self.dialog.geometry("550x550")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.resizable(False, False)
        
        self.setup_ui()
        self.dialog.bind('<Escape>', lambda e: self.dialog.destroy())
        self.dialog.bind('<Return>', lambda e: self.procesar())
        
    def setup_ui(self):
        # Título
        tk.Label(self.dialog, text="💰 PAGO EN EFECTIVO", 
                font=('Helvetica', 14, 'bold')).pack(pady=10)
        
        # Frame para totales
        total_frame = tk.LabelFrame(self.dialog, text="Total a Pagar", padx=10, pady=5)
        total_frame.pack(fill='x', padx=20, pady=5)
        
        # Calcular el total correcto con IVA
        total_correcto_bs = self.total_bs  # Esto viene de main_window_inteligente.py
        # Pero necesitamos asegurarnos de que sea el correcto
        
        tk.Label(total_frame, text=f"Total Bs.: {total_correcto_bs:.2f} Bs.", 
                font=('Helvetica', 12)).pack(anchor='w')
        tk.Label(total_frame, text=f"Total USD: ${self.total_usd:.2f}", 
                font=('Helvetica', 12)).pack(anchor='w')
        tk.Label(total_frame, text=f"Tasa: 1 USD = {self.tasa_cambio:.2f} Bs.", 
                font=('Helvetica', 10)).pack(anchor='w')
        
        # Desglose fiscal en Bs.
        if self.totales_fiscales:
            fiscal_frame = tk.LabelFrame(self.dialog, text="Desglose Fiscal (Bs.)", padx=10, pady=5)
            fiscal_frame.pack(fill='x', padx=20, pady=5)
            
            tasa = self.tasa_cambio
            exento_bs = self.totales_fiscales['exento'] * tasa
            base_bs = self.totales_fiscales['base_gravada_usd'] * tasa
            iva_bs = self.totales_fiscales['iva_usd'] * tasa
            total_bs = self.totales_fiscales['total_con_iva'] * tasa  # ESTE ES EL CORRECTO
            
            tk.Label(fiscal_frame, 
                    text=f"Exento: Bs.{exento_bs:.0f}".replace('.', ','),
                    font=('Helvetica', 9)).pack(anchor='w')
            tk.Label(fiscal_frame,
                    text=f"Base G: Bs.{base_bs:.0f}".replace('.', ','),
                    font=('Helvetica', 9)).pack(anchor='w')
            tk.Label(fiscal_frame,
                    text=f"IVA (16%): Bs.{iva_bs:.0f}".replace('.', ','),
                    font=('Helvetica', 9)).pack(anchor='w')
            tk.Label(fiscal_frame,
                    text=f"TOTAL: Bs.{total_bs:.0f}".replace('.', ','),
                    font=('Helvetica', 9, 'bold')).pack(anchor='w')
        
        # Opción de moneda de pago (si está activo USD)
        if self.config.get('efectivo_usd_activo', False):
            moneda_frame = tk.LabelFrame(self.dialog, text="Moneda de Pago", padx=10, pady=5)
            moneda_frame.pack(fill='x', padx=20, pady=5)
            
            self.moneda_var = tk.StringVar(value="BS")
            tk.Radiobutton(moneda_frame, text="Bolívares (Bs.)", variable=self.moneda_var, 
                          value="BS", command=self.actualizar_label).pack(anchor='w')
            tk.Radiobutton(moneda_frame, text="Dólares (USD)", variable=self.moneda_var, 
                          value="USD", command=self.actualizar_label).pack(anchor='w')
        else:
            self.moneda_var = tk.StringVar(value="BS")
        
        # Frame para ingreso de pago
        pago_frame = tk.LabelFrame(self.dialog, text="Pago", padx=10, pady=5)
        pago_frame.pack(fill='x', padx=20, pady=5)
        
        self.label_recibido = tk.Label(pago_frame, text="Monto recibido (Bs.):", font=('Helvetica', 10))
        self.label_recibido.pack(anchor='w')
        
        self.entry_recibido = tk.Entry(pago_frame, font=('Helvetica', 12), width=20)
        self.entry_recibido.pack(pady=5)
        self.entry_recibido.focus()
        self.entry_recibido.bind('<KeyRelease>', self.calcular_vuelto)
        
        # Label para vuelto
        vuelto_frame = tk.Frame(pago_frame)
        vuelto_frame.pack(fill='x', pady=5)
        
        tk.Label(vuelto_frame, text="Vuelto:", font=('Helvetica', 12, 'bold')).pack(side='left')
        self.label_vuelto = tk.Label(vuelto_frame, text="0.00 Bs.", font=('Helvetica', 12, 'bold'), fg='green')
        self.label_vuelto.pack(side='left', padx=10)
        
        # Botones
        btn_frame = tk.Frame(self.dialog)
        btn_frame.pack(pady=20)
        
        tk.Button(btn_frame, text="Procesar Pago", command=self.procesar,
                 bg='#27ae60', fg='white', font=('Helvetica', 12), width=15).pack(side='left', padx=5)
        
        tk.Button(btn_frame, text="Cancelar", command=self.dialog.destroy,
                 bg='#e74c3c', fg='white', font=('Helvetica', 12), width=15).pack(side='left', padx=5)
    
    def actualizar_label(self):
        """Actualiza la etiqueta según la moneda seleccionada."""
        if self.moneda_var.get() == "BS":
            self.label_recibido.config(text="Monto recibido (Bs.):")
        else:
            self.label_recibido.config(text="Monto recibido (USD):")
        self.calcular_vuelto()
    
    def calcular_vuelto(self, event=None):
        """Calcula el vuelto en ambas monedas en tiempo real."""
        try:
            texto = self.entry_recibido.get()
            if not texto:
                self.label_vuelto.config(text="0.00 USD / 0.00 Bs.")
                return
            
            monto_recibido = float(texto)
            tasa = self.tasa_cambio
            
            if self.moneda_var.get() == "BS":
                # Pago en Bolívares
                total_bs = self.total_bs
                vuelto_bs = monto_recibido - total_bs
                
                if vuelto_bs < 0:
                    self.label_vuelto.config(
                        text=f"❌ FALTAN: {abs(vuelto_bs):.2f} Bs.", 
                        fg='red'
                    )
                else:
                    # Convertir vuelto a USD para referencia
                    vuelto_usd = vuelto_bs / tasa
                    self.label_vuelto.config(
                        text=f"✅ VUELTO: {vuelto_bs:.2f} Bs. (${vuelto_usd:.2f})", 
                        fg='green'
                    )
            else:
                # Pago en Dólares
                total_usd = self.total_usd
                vuelto_usd = monto_recibido - total_usd
                
                if vuelto_usd < 0:
                    self.label_vuelto.config(
                        text=f"❌ FALTAN: ${abs(vuelto_usd):.2f}", 
                        fg='red'
                    )
                else:
                    # Convertir vuelto a Bolívares
                    vuelto_bs = vuelto_usd * tasa
                    self.label_vuelto.config(
                        text=f"✅ VUELTO: ${vuelto_usd:.2f} (Bs.{vuelto_bs:.2f})", 
                        fg='green'
                    )
                    
        except ValueError:
            self.label_vuelto.config(text="❌ Error", fg='red')
    
    def procesar(self):
        """Procesa el pago guardando información de ambas monedas."""
        try:
            texto = self.entry_recibido.get()
            if not texto:
                messagebox.showerror("Error", "Debe ingresar un monto")
                return
            
            monto_recibido = float(texto)
            moneda = self.moneda_var.get()
            tasa = self.tasa_cambio
            
            if moneda == "BS":
                # Validar pago en Bolívares
                if monto_recibido < self.total_bs:
                    messagebox.showerror("Error", 
                        f"Monto insuficiente.\n"
                        f"Total: {self.total_bs:.2f} Bs.\n"
                        f"Recibido: {monto_recibido:.2f} Bs.")
                    return
                
                vuelto_bs = monto_recibido - self.total_bs
                vuelto_usd = vuelto_bs / tasa
                
                self.resultado = {
                    'moneda': 'BS',
                    'monto_recibido': monto_recibido,
                    'total_pagado': self.total_bs,
                    'vuelto': vuelto_bs,
                    'vuelto_usd': vuelto_usd
                }
                logger.info(f"💰 Pago en Bs. - Vuelto: {vuelto_bs:.2f} Bs. (${vuelto_usd:.2f})")
                
            else:
                # Validar pago en Dólares
                if monto_recibido < self.total_usd:
                    messagebox.showerror("Error", 
                        f"Monto insuficiente.\n"
                        f"Total: ${self.total_usd:.2f}\n"
                        f"Recibido: ${monto_recibido:.2f}")
                    return
                
                vuelto_usd = monto_recibido - self.total_usd
                vuelto_bs = vuelto_usd * tasa
                
                self.resultado = {
                    'moneda': 'USD',
                    'monto_recibido': monto_recibido,
                    'total_pagado': self.total_usd,
                    'vuelto': vuelto_usd,
                    'vuelto_bs': vuelto_bs
                }
                logger.info(f"💰 Pago en USD - Vuelto: ${vuelto_usd:.2f} (Bs.{vuelto_bs:.2f})")
            
            self.dialog.destroy()
            
        except ValueError:
            messagebox.showerror("Error", "Monto inválido")
    
    def show(self):
        """Muestra el diálogo y espera el resultado."""
        self.dialog.wait_window()
        return self.resultado
