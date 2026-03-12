
# Funciones de reparación automática - Agregadas por SupremeBot
def safe_get(obj, attr, default=None):
    """Obtiene atributo de forma segura sin NoneType errors"""
    try:
        return getattr(obj, attr) if obj is not None else default
    except:
        return default

def safe_dict_get(d, key, default=None):
    """Obtiene valor de diccionario de forma segura"""
    try:
        return d.get(key, default) if d is not None else default
    except:
        return default

"""
Diálogo para procesar pagos mixtos (múltiples métodos)
"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from loguru import logger
from models.cuenta_empresa import CuentaEmpresaRepo

class PagoMixtoDialog:
    def __init__(self, parent, total_usd, total_bs, tasa_cambio, 
                 config_empresa, totales_fiscales=None, venta_agent=None):
        self.parent = parent
        self.total_usd = total_usd
        self.total_bs = total_bs
        self.tasa_cambio = tasa_cambio
        self.config = config_empresa
        self.totales_fiscales = totales_fiscales
        self.venta_agent = venta_agent
        
        self.pagos = []  # Lista de pagos agregados
        self.pendiente_usd = total_usd
        self.resultado = None
        
        # Inicializar repositorio de cuentas
        from core.database import Database
        self.db = Database()
        self.conn = self.db.get_connection()
        self.cuenta_repo = CuentaEmpresaRepo(self.conn)
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("💰 Pago Mixto")
        self.dialog.geometry("750x650")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.resizable(False, False)
        
        self.setup_ui()
        self.actualizar_pendiente()
        
    def setup_ui(self):
        # Título
        tk.Label(self.dialog, text="💳 PAGO MIXTO - MÚLTIPLES MÉTODOS", 
                font=('Helvetica', 14, 'bold')).pack(pady=10)
        
        # Frame de totales
        total_frame = tk.LabelFrame(self.dialog, text="Totales", padx=10, pady=5)
        total_frame.pack(fill='x', padx=20, pady=5)
        
        self.label_total = tk.Label(total_frame, 
                                    text=f"Total: ${self.total_usd:.2f} (Bs.{self.total_bs:.2f})",
                                    font=('Helvetica', 12, 'bold'))
        self.label_total.pack(anchor='w')
        
        # Frame para pendiente (USD y Bs.)
        pendiente_frame = tk.Frame(total_frame)
        pendiente_frame.pack(fill='x', pady=2)
        
        self.label_pendiente_usd = tk.Label(pendiente_frame, 
                                           text=f"Pendiente USD: ${self.pendiente_usd:.2f}",
                                           font=('Helvetica', 11, 'bold'), fg='red')
        self.label_pendiente_usd.pack(side='left', padx=(0, 20))
        
        self.label_pendiente_bs = tk.Label(pendiente_frame, 
                                          text=f"Pendiente Bs.: Bs.{self.pendiente_usd * self.tasa_cambio:.0f}",
                                          font=('Helvetica', 11, 'bold'), fg='red')
        self.label_pendiente_bs.pack(side='left')
        
        # Frame para agregar pagos
        add_frame = tk.LabelFrame(self.dialog, text="Agregar Pago", padx=10, pady=5)
        add_frame.pack(fill='x', padx=20, pady=5)
        
        # Configurar grid para add_frame
        add_frame.columnconfigure(0, weight=1, minsize=100)
        add_frame.columnconfigure(1, weight=3)
        
        # Método de pago (fila 0)
        tk.Label(add_frame, text="Método:", font=('Helvetica', 10)).grid(row=0, column=0, sticky='w', pady=5)
        self.metodo_var = tk.StringVar()
        self.combo_metodo = ttk.Combobox(add_frame, textvariable=self.metodo_var, 
                                         width=30, state='readonly')
        self.combo_metodo['values'] = [
            'EFECTIVO_BS',
            'EFECTIVO_USD',
            'TARJETA_BS',
            'TARJETA_USD',
            'PAGO_MOVIL',
            'TRANSFERENCIA'
        ]
        self.combo_metodo.grid(row=0, column=1, padx=5, pady=5, sticky='w')
        self.combo_metodo.bind('<<ComboboxSelected>>', self.on_metodo_change)
        
        # Monto (fila 1)
        tk.Label(add_frame, text="Monto:", font=('Helvetica', 10)).grid(row=1, column=0, sticky='w', pady=5)
        self.entry_monto = tk.Entry(add_frame, width=15, font=('Helvetica', 10))
        self.entry_monto.grid(row=1, column=1, sticky='w', padx=5, pady=5)
        
        # Moneda (solo visible para efectivo) - fila 2
        self.moneda_var = tk.StringVar(value="USD")
        self.frame_moneda = tk.Frame(add_frame)
        tk.Radiobutton(self.frame_moneda, text="USD", variable=self.moneda_var, 
                      value="USD", command=self.calcular_preview).pack(side='left', padx=2)
        tk.Radiobutton(self.frame_moneda, text="Bs.", variable=self.moneda_var, 
                      value="BS", command=self.calcular_preview).pack(side='left', padx=2)
        
        # Cuenta destino (para Pago Móvil/Transferencia) - fila 3
        self.frame_cuenta = tk.Frame(add_frame)
        tk.Label(self.frame_cuenta, text="Cuenta:", width=12, anchor='w', font=('Helvetica', 10)).pack(side='left')
        self.cuenta_var = tk.StringVar()
        self.combo_cuenta = ttk.Combobox(self.frame_cuenta, textvariable=self.cuenta_var,
                                         width=40, state='readonly')
        self.combo_cuenta.pack(side='left', padx=5)
        
        # Referencia (para Pago Móvil/Transferencia) - fila 4
        self.frame_ref = tk.Frame(add_frame)
        tk.Label(self.frame_ref, text="Referencia:", width=12, anchor='w', font=('Helvetica', 10)).pack(side='left')
        self.entry_ref = tk.Entry(self.frame_ref, width=25, font=('Helvetica', 10))
        self.entry_ref.pack(side='left', padx=5)
        
        # Teléfono cliente (para Pago Móvil) - fila 5
        self.frame_telf = tk.Frame(add_frame)
        tk.Label(self.frame_telf, text="Teléfono:", width=12, anchor='w', font=('Helvetica', 10)).pack(side='left')
        self.entry_telf = tk.Entry(self.frame_telf, width=15, font=('Helvetica', 10))
        self.entry_telf.pack(side='left', padx=5)
        
        # Preview del pago (fila 6)
        self.label_preview = tk.Label(add_frame, text="", font=('Helvetica', 9), fg='blue')
        self.label_preview.grid(row=6, column=0, columnspan=2, pady=5)
        
        # Botón agregar (fila 7)
        tk.Button(add_frame, text="➕ Agregar Pago", command=self.agregar_pago,
                 bg='#3498db', fg='white', font=('Helvetica', 10), width=15).grid(row=7, column=0, columnspan=2, pady=10)
        
        # Frame de pagos agregados - TAMAÑO CONTROLADO
        lista_frame = tk.LabelFrame(self.dialog, text="Pagos Agregados", padx=10, pady=5)
        lista_frame.pack(fill='x', padx=20, pady=5)
        lista_frame.configure(height=150)
        lista_frame.pack_propagate(False)
        
        # Listbox con scrollbar - ALTURA FIJA
        scrollbar = tk.Scrollbar(lista_frame)
        scrollbar.pack(side='right', fill='y')
        
        self.listbox_pagos = tk.Listbox(lista_frame, yscrollcommand=scrollbar.set,
                                        height=5, font=('Courier', 10))
        self.listbox_pagos.pack(fill='both', expand=True)
        scrollbar.config(command=self.listbox_pagos.yview)
        
        # Botón quitar pago
        tk.Button(lista_frame, text="❌ Quitar seleccionado", 
                 command=self.quitar_pago, bg='#e74c3c', fg='white', width=20).pack(pady=5)
        
        # Botón quitar pago
        tk.Button(lista_frame, text="❌ Quitar seleccionado", 
                 command=self.quitar_pago, bg='#e74c3c', fg='white', width=20).pack(pady=5)
        
        # Bind para preview
        self.entry_monto.bind('<KeyRelease>', self.calcular_preview)
        
        # Ocultar frames adicionales inicialmente
        self.frame_moneda.grid_forget()
        self.frame_cuenta.grid_forget()
        self.frame_ref.grid_forget()
        self.frame_telf.grid_forget()
        
        # Cargar cuentas después de crear UI
        self.cargar_cuentas()
        
        # ===== BOTONES FINALES SIEMPRE VISIBLES =====
        # Frame contenedor para botones (FUERA DEL EXPAND)
        btn_outer = tk.Frame(self.dialog, height=80, bg='#f0f0f0')
        btn_outer.pack(side='bottom', fill='x', padx=20, pady=10)
        btn_outer.pack_propagate(False)
        
        # Frame interno para centrar
        btn_frame = tk.Frame(btn_outer, bg='#f0f0f0')
        btn_frame.pack(expand=True)
        
        # Botón Confirmar
        self.btn_confirmar = tk.Button(btn_frame, text="✅ Confirmar Pago Mixto",
                                       command=self.confirmar, state='disabled',
                                       bg='#27ae60', fg='white', 
                                       font=('Helvetica', 11, 'bold'),
                                       width=22, height=2,
                                       relief='raised', bd=3)
        self.btn_confirmar.pack(side='left', padx=10)
        
        # Botón Cancelar
        tk.Button(btn_frame, text="❌ Cancelar", command=self.cancelar,
                 bg='#e74c3c', fg='white', 
                 font=('Helvetica', 11, 'bold'),
                 width=15, height=2,
                 relief='raised', bd=3).pack(side='left', padx=10)
    
    def cargar_cuentas(self, metodo_filtro=None):
        """Carga las cuentas disponibles, opcionalmente filtradas por método"""
        try:
            from models.cuenta_empresa import CuentaEmpresaRepo
            self.cuenta_repo = CuentaEmpresaRepo(self.conn)
            
            if metodo_filtro:
                # Obtener cuentas que soportan este método específico
                cuentas = self.cuenta_repo.obtener_cuentas_por_metodo(
                    metodo_filtro, 
                    solo_activas=True, 
                    solo_visibles=True  # Solo las que ve el cajero
                )
                print(f"🔍 DEBUG - Cuentas para {metodo_filtro}: {len(cuentas)}")
            else:
                # Sin filtro (para compatibilidad)
                cuentas = self.cuenta_repo.listar_cuentas(solo_programador=False)
                print(f"🔍 DEBUG - Todas las cuentas: {len(cuentas)}")
            
            if not cuentas:
                self.combo_cuenta['values'] = ['❌ No hay cuentas disponibles']
                self.combo_cuenta.set('')
                self.cuentas_opciones = []
                return
            
            opciones = []
            for c in cuentas:
                if c.telefono_asociado and c.moneda == 'VES':
                    texto = f"{safe_get(c, "nombre_banco")} - Pago Móvil: {safe_get(c, "telefono_asociado")}"
                else:
                    texto = f"{safe_get(c, "nombre_banco")} - {safe_get(c, "numero_cuenta")} ({safe_get(c, "moneda")})"
                
                safe_get(opciones, "append")((texto, safe_get(c, "idcuenta")))
            
            self.cuentas_opciones = opciones
            self.combo_cuenta['values'] = [op[0] for op in opciones]
            
            if opciones:
                self.combo_cuenta.current(0)
                
        except Exception as e:
            print(f"❌ Error cargando cuentas: {e}")
            logger.error(f"Error cargando cuentas: {e}")
            self.combo_cuenta['values'] = ['❌ Error']
            self.cuentas_opciones = []
    
    def on_metodo_change(self, event=None):
        """Muestra/oculta campos según método seleccionado y filtra cuentas"""
        metodo = self.metodo_var.get()
        
        # Ocultar todos los frames
        self.frame_moneda.grid_forget()
        self.frame_cuenta.grid_forget()
        self.frame_ref.grid_forget()
        self.frame_telf.grid_forget()
        
        # Configurar según el método
        if metodo == 'EFECTIVO_BS':
            self.moneda_var.set('BS')
            self.frame_moneda.grid(row=2, column=0, columnspan=2, pady=5, sticky='w')
            # Cargar cuentas para EFECTIVO_BS (opcional)
            self.cargar_cuentas('EFECTIVO_BS')
            
        elif metodo == 'EFECTIVO_USD':
            self.moneda_var.set('USD')
            self.frame_moneda.grid(row=2, column=0, columnspan=2, pady=5, sticky='w')
            # Cargar cuentas para EFECTIVO_USD (opcional)
            self.cargar_cuentas('EFECTIVO_USD')
            
        elif metodo == 'TARJETA_BS':
            self.moneda_var.set('BS')
            # Cargar cuentas para TARJETA_BS (opcional)
            self.cargar_cuentas('TARJETA_BS')
            
        elif metodo == 'TARJETA_USD':
            self.moneda_var.set('USD')
            # Cargar cuentas para TARJETA_USD (opcional)
            self.cargar_cuentas('TARJETA_USD')
            
        elif metodo == 'PAGO_MOVIL':
            self.moneda_var.set('BS')
            self.frame_cuenta.grid(row=3, column=0, columnspan=2, pady=5, sticky='w')
            self.frame_ref.grid(row=4, column=0, columnspan=2, pady=5, sticky='w')
            self.frame_telf.grid(row=5, column=0, columnspan=2, pady=5, sticky='w')
            # Cargar cuentas para PAGO_MOVIL (obligatorio)
            self.cargar_cuentas('PAGO_MOVIL')
            
        elif metodo == 'TRANSFERENCIA':
            self.moneda_var.set('BS')
            self.frame_cuenta.grid(row=3, column=0, columnspan=2, pady=5, sticky='w')
            self.frame_ref.grid(row=4, column=0, columnspan=2, pady=5, sticky='w')
            # Cargar cuentas para TRANSFERENCIA (obligatorio)
            self.cargar_cuentas('TRANSFERENCIA')
        
        self.calcular_preview()
    
    def calcular_preview(self, event=None):
        """Calcula y muestra preview del pago (IGTF, comisiones)"""
        try:
            texto = self.entry_monto.get()
            if not texto:
                self.label_preview.config(text="")
                return
            
            monto = float(texto)
            metodo = self.metodo_var.get()
            
            # Determinar moneda según el método
            if metodo in ['EFECTIVO_BS', 'TARJETA_BS', 'PAGO_MOVIL', 'TRANSFERENCIA']:
                moneda = 'BS'
            elif metodo in ['EFECTIVO_USD', 'TARJETA_USD']:
                moneda = 'USD'
            else:
                moneda = 'USD'  # Por defecto            
            
            # Convertir a USD si es necesario
            if moneda == 'BS':
                monto_usd = monto / self.tasa_cambio
            else:
                monto_usd = monto
            
            # Obtener config de pagos
            config_pagos = self.venta_agent.obtener_configuracion_pagos() if self.venta_agent else {}
            
            # Calcular IGTF
            igtf_text = ""
            if metodo == 'TARJETA_USD' and config_pagos.get('igtf_activo') and config_pagos.get('igtf_aplica_tarjeta_usd'):
                igtf = monto_usd * (config_pagos.get('igtf_porcentaje', 3.0) / 100)
                igtf_text = f" + IGTF ${igtf:.2f}"
                monto_usd += igtf
            
            # Calcular comisión
            comision_text = ""
            if 'TARJETA' in metodo:
                if metodo == 'TARJETA_USD' and config_pagos.get('comision_usd', {}).get('activo'):
                    comision_pct = config_pagos['comision_usd']['porcentaje']
                elif metodo == 'TARJETA_BS' and config_pagos.get('comision_bs', {}).get('activo'):
                    comision_pct = config_pagos['comision_bs']['porcentaje']
                else:
                    comision_pct = config_pagos.get('comision_tarjeta', 2.5)
                
                comision = monto_usd * (comision_pct / 100)
                comision_text = f" - Comisión {comision_pct}% (${comision:.2f})"
            
            preview = f"Preview: ${monto_usd:.2f}{igtf_text}{comision_text}"
            self.label_preview.config(text=preview)
            
        except ValueError:
            self.label_preview.config(text="Monto inválido")
    
    def agregar_pago(self):
        """Agrega un pago a la lista"""
        metodo = self.metodo_var.get()
        if not metodo:
            messagebox.showerror("Error", "Seleccione un método de pago")
            return
        
        try:
            monto = float(self.entry_monto.get())
        except ValueError:
            messagebox.showerror("Error", "Monto inválido")
            return
        
        if monto <= 0:
            messagebox.showerror("Error", "El monto debe ser positivo")
            return
        
        # Determinar moneda según el método
        if metodo in ['EFECTIVO_BS', 'TARJETA_BS', 'PAGO_MOVIL', 'TRANSFERENCIA']:
            moneda = 'BS'
        elif metodo in ['EFECTIVO_USD', 'TARJETA_USD']:
            moneda = 'USD'
        else:
            moneda = 'USD'  # Por defecto
        
        # Validar contra pendiente
        if moneda == 'USD':
            monto_usd = monto
        else:
            monto_usd = monto / self.tasa_cambio
        
        if monto_usd > self.pendiente_usd + 0.01:
            messagebox.showerror("Error", 
                f"El monto ${monto_usd:.2f} excede el pendiente ${self.pendiente_usd:.2f}")
            return
        
        # Obtener datos adicionales según método
        referencia = None
        idcuenta_destino = None
        telefono_cliente = None
        
        # ===== NUEVA LÓGICA DE VALIDACIÓN DE CUENTAS =====
        if metodo in ['PAGO_MOVIL', 'TRANSFERENCIA']:
            # Para Pago Móvil y Transferencia: CUENTA OBLIGATORIA
            if not self.combo_cuenta.get() or self.combo_cuenta.get() == '❌ No hay cuentas disponibles':
                messagebox.showerror("Error", f"Seleccione una cuenta destino para {metodo}")
                return
            
            # Obtener ID de cuenta seleccionada
            idx = self.combo_cuenta.current()
            if idx >= 0 and idx < len(self.cuentas_opciones):
                idcuenta_destino = self.cuentas_opciones[idx][1]
            
            referencia = self.entry_ref.get().strip()
            if not referencia:
                messagebox.showerror("Error", "Ingrese número de referencia")
                return
            
            if metodo == 'PAGO_MOVIL':
                telefono_cliente = self.entry_telf.get().strip()
                if not telefono_cliente:
                    messagebox.showerror("Error", "Ingrese teléfono del cliente")
                    return
        
        elif metodo in ['EFECTIVO_BS', 'EFECTIVO_USD', 'TARJETA_BS', 'TARJETA_USD']:
            # Para Efectivo y Tarjeta: CUENTA OPCIONAL
            if self.combo_cuenta.get() and self.combo_cuenta.get() != '❌ No hay cuentas disponibles':
                idx = self.combo_cuenta.current()
                if idx >= 0 and idx < len(self.cuentas_opciones):
                    idcuenta_destino = self.cuentas_opciones[idx][1]
                    # La referencia es opcional para estos métodos
                    referencia = self.entry_ref.get().strip() or None
        
        # Crear registro de pago
        pago = {
            'metodo': metodo,
            'monto': monto,
            'moneda': moneda,
            'monto_usd': monto_usd,
            'referencia': referencia,
            'idcuenta_destino': idcuenta_destino,
            'telefono_cliente': telefono_cliente
        }
        
        self.pagos.append(pago)
        self.pendiente_usd -= monto_usd
        
        # Actualizar lista
        self.actualizar_lista()
        self.actualizar_pendiente()
        
        # Limpiar campos
        self.entry_monto.delete(0, tk.END)
        self.entry_ref.delete(0, tk.END)
        self.entry_telf.delete(0, tk.END)
        self.combo_metodo.set('')
        
        # Habilitar confirmar si está completo
        if abs(self.pendiente_usd) < 0.01:
            self.btn_confirmar.config(state='normal')
    
    def quitar_pago(self):
        """Quita el pago seleccionado"""
        seleccion = self.listbox_pagos.curselection()
        if not seleccion:
            return
        
        idx = seleccion[0]
        pago = self.pagos.pop(idx)
        
        # Devolver al pendiente
        self.pendiente_usd += pago['monto_usd']
        
        self.actualizar_lista()
        self.actualizar_pendiente()
        self.btn_confirmar.config(state='disabled')
    
    def actualizar_lista(self):
        """Actualiza la lista de pagos en la UI"""
        self.listbox_pagos.delete(0, tk.END)
        
        for i, pago in enumerate(self.pagos, 1):
            if pago['moneda'] == 'USD':
                texto = f"{i}. {pago['metodo']}: ${pago['monto']:.2f}"
            else:
                texto = f"{i}. {pago['metodo']}: Bs.{pago['monto']:.2f}"
            
            if pago.get('referencia'):
                texto += f" (Ref: {pago['referencia']})"
            
            self.listbox_pagos.insert(tk.END, texto)
    
    def actualizar_pendiente(self):
        """Actualiza los labels de pendiente en USD y Bs."""
        pendiente_bs = self.pendiente_usd * self.tasa_cambio
        
        self.label_pendiente_usd.config(
            text=f"Pendiente USD: ${self.pendiente_usd:.2f}",
            fg='green' if abs(self.pendiente_usd) < 0.01 else 'red'
        )
        
        self.label_pendiente_bs.config(
            text=f"Pendiente Bs.: Bs.{pendiente_bs:.0f}",
            fg='green' if abs(self.pendiente_usd) < 0.01 else 'red'
        )
    
    def confirmar(self):
        """Confirma todos los pagos y procesa la venta"""
        if abs(self.pendiente_usd) > 0.01:
            messagebox.showerror("Error", f"Faltan ${self.pendiente_usd:.2f} por pagar")
            return
        
        self.resultado = {
            'pagos': self.pagos,
            'total_usd': self.total_usd,
            'total_bs': self.total_bs
        }
        
        logger.info(f"✅ Pago mixto confirmado con {len(self.pagos)} métodos")
        self.dialog.destroy()
    
    def cancelar(self):
        """Cancela el pago mixto"""
        self.resultado = None
        self.dialog.destroy()
    
    def show(self):
        """Muestra el diálogo y espera resultado"""
        self.dialog.wait_window()
        return self.resultado
