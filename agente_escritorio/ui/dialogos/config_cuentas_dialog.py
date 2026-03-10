"""
Diálogo para configuración de cuentas bancarias de la empresa (Solo programador)
"""
import tkinter as tk
from tkinter import ttk, messagebox
from loguru import logger
from models.cuenta_empresa import CuentaEmpresa, CuentaEmpresaRepo

class ConfigCuentasDialog:
    def __init__(self, parent, cuenta_repo):
        self.parent = parent
        self.repo = cuenta_repo
        self.conn = cuenta_repo.conn
        
        self.cuenta_actual = None
        self.bancos = []
        
        # Obtener la ventana padre correcta
        ventana_padre = parent.root if hasattr(parent, 'root') else parent
        
        self.dialog = tk.Toplevel(ventana_padre)
        self.dialog.title("⚙️ Configurar Cuentas Empresariales")
        self.dialog.geometry("750x650")
        self.dialog.transient(ventana_padre)
        self.dialog.grab_set()
        
        self.setup_ui()
        self.cargar_bancos()
        self.listar_cuentas()
        
    def setup_ui(self):
        # Título
        tk.Label(self.dialog, text="🏦 CONFIGURACIÓN DE CUENTAS EMPRESARIALES", 
                font=('Helvetica', 14, 'bold')).pack(pady=10)
        
        # Notebook para pestañas
        notebook = ttk.Notebook(self.dialog)
        notebook.pack(fill='both', expand=True, padx=10, pady=5)
        
        # ===== PESTAÑA 1: LISTA DE CUENTAS =====
        frame_lista = ttk.Frame(notebook)
        notebook.add(frame_lista, text='📋 Cuentas Registradas')
        
        # Treeview para cuentas
        columns = ('id', 'banco', 'cuenta', 'tipo', 'moneda', 'telefono', 'visible')
        self.tree = ttk.Treeview(frame_lista, columns=columns, show='headings', height=12)
        
        # Configurar columnas
        self.tree.heading('id', text='ID')
        self.tree.heading('banco', text='Banco')
        self.tree.heading('cuenta', text='N° Cuenta')
        self.tree.heading('tipo', text='Tipo')
        self.tree.heading('moneda', text='Moneda')
        self.tree.heading('telefono', text='Pago Móvil')
        self.tree.heading('visible', text='Visibilidad')
        
        self.tree.column('id', width=40)
        self.tree.column('banco', width=150)
        self.tree.column('cuenta', width=150)
        self.tree.column('tipo', width=80)
        self.tree.column('moneda', width=60)
        self.tree.column('telefono', width=100)
        self.tree.column('visible', width=100)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(frame_lista, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        scrollbar.pack(side='right', fill='y')
        
        self.tree.bind('<<TreeviewSelect>>', self.on_select)
        
        # Botones de acción bajo la lista
        btn_frame = tk.Frame(frame_lista)
        btn_frame.pack(fill='x', pady=10)
        
        tk.Button(btn_frame, text="✏️ Editar", command=self.editar_cuenta,
                 bg='#3498db', fg='white', width=12).pack(side='left', padx=5)
        tk.Button(btn_frame, text="❌ Desactivar", command=self.desactivar_cuenta,
                 bg='#e74c3c', fg='white', width=12).pack(side='left', padx=5)
        tk.Button(btn_frame, text="🔄 Actualizar", command=self.listar_cuentas,
                 bg='#2ecc71', fg='white', width=12).pack(side='left', padx=5)
        
        # ===== PESTAÑA 2: NUEVA CUENTA =====
        frame_nueva = ttk.Frame(notebook)
        notebook.add(frame_nueva, text='➕ Nueva Cuenta')
        
        # Canvas con scroll para formulario largo
        canvas = tk.Canvas(frame_nueva)
        scrollbar_y = ttk.Scrollbar(frame_nueva, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar_y.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar_y.pack(side="right", fill="y")
        
        # Formulario dentro del scrollable_frame
        form = tk.Frame(scrollable_frame)
        form.pack(padx=20, pady=20, fill='both', expand=True)
        
        # Campos del formulario
        tk.Label(form, text="Banco:", font=('Helvetica', 10, 'bold')).grid(row=0, column=0, sticky='w', pady=5)
        self.combo_banco = ttk.Combobox(form, width=40, state='readonly')
        self.combo_banco.grid(row=0, column=1, padx=10, pady=5, columnspan=2)
        
        tk.Label(form, text="Número de cuenta:", font=('Helvetica', 10, 'bold')).grid(row=1, column=0, sticky='w', pady=5)
        self.entry_numero = tk.Entry(form, width=40)
        self.entry_numero.grid(row=1, column=1, padx=10, pady=5, columnspan=2)
        
        tk.Label(form, text="Tipo de cuenta:", font=('Helvetica', 10, 'bold')).grid(row=2, column=0, sticky='w', pady=5)
        self.tipo_var = tk.StringVar(value="CORRIENTE")
        tk.Radiobutton(form, text="Corriente", variable=self.tipo_var, 
                      value="CORRIENTE").grid(row=2, column=1, sticky='w')
        tk.Radiobutton(form, text="Ahorro", variable=self.tipo_var, 
                      value="AHORRO").grid(row=2, column=2, sticky='w')
        
        tk.Label(form, text="Moneda:", font=('Helvetica', 10, 'bold')).grid(row=3, column=0, sticky='w', pady=5)
        self.moneda_var = tk.StringVar(value="VES")
        tk.Radiobutton(form, text="Bolívares (VES)", variable=self.moneda_var, 
                      value="VES").grid(row=3, column=1, sticky='w')
        tk.Radiobutton(form, text="Dólares (USD)", variable=self.moneda_var, 
                      value="USD").grid(row=3, column=2, sticky='w')
        
        tk.Label(form, text="Teléfono Pago Móvil:", font=('Helvetica', 10, 'bold')).grid(row=4, column=0, sticky='w', pady=5)
        self.entry_telefono = tk.Entry(form, width=30)
        self.entry_telefono.grid(row=4, column=1, padx=10, pady=5, columnspan=2)
        
        tk.Label(form, text="Cédula titular:", font=('Helvetica', 10, 'bold')).grid(row=5, column=0, sticky='w', pady=5)
        self.entry_cedula = tk.Entry(form, width=30)
        self.entry_cedula.grid(row=5, column=1, padx=10, pady=5, columnspan=2)
        
        tk.Label(form, text="Visibilidad:", font=('Helvetica', 10, 'bold')).grid(row=6, column=0, sticky='w', pady=5)
        self.visible_var = tk.BooleanVar(value=False)
        tk.Checkbutton(form, text="Solo visible para programador (comando oculto)", 
                      variable=self.visible_var).grid(row=6, column=1, columnspan=2, sticky='w')
        
        # Botón guardar
        tk.Button(form, text="💾 Guardar Cuenta", command=self.guardar_cuenta,
                 bg='#27ae60', fg='white', font=('Helvetica', 11), width=20).grid(row=7, column=0, columnspan=3, pady=30)
        
        # ===== PESTAÑA 3: AYUDA =====
        frame_ayuda = ttk.Frame(notebook)
        notebook.add(frame_ayuda, text='❓ Ayuda')
        
        ayuda_texto = tk.Text(frame_ayuda, wrap='word', padx=10, pady=10, height=15)
        ayuda_texto.pack(fill='both', expand=True, padx=10, pady=10)
        
        ayuda_texto.insert('1.0', """
📌 INSTRUCCIONES PARA CUENTAS EMPRESARIALES

🔹 **PAGO MÓVIL**
   - Debe tener teléfono asociado
   - La cuenta debe estar en VES (Bolívares)
   - El cajero verá: "Banco X - Pago Móvil: 0412-1234567"

🔹 **TRANSFERENCIA**
   - Puede ser en VES o USD
   - Se requiere número de referencia
   - El cajero verá el número de cuenta

🔹 **VISIBILIDAD**
   - "Solo programador": Solo visible con comando oculto
   - "Todos visible": Aparece para el cajero

🔹 **SEGURIDAD**
   - Los cajeros NO pueden modificar cuentas
   - Solo ven los datos necesarios
   - Las cuentas se pueden desactivar (no eliminar)
        """)
        ayuda_texto.config(state='disabled')
        
        # Botón cerrar general
        tk.Button(self.dialog, text="Cerrar", command=self.dialog.destroy,
                 bg='#95a5a6', fg='white', width=20).pack(pady=10)
    
    def cargar_bancos(self):
        """Carga la lista de bancos"""
        try:
            self.bancos = self.repo.listar_bancos()
            self.combo_banco['values'] = [b.nombre for b in self.bancos]
        except Exception as e:
            logger.error(f"Error cargando bancos: {e}")
    
    def listar_cuentas(self):
        """Lista todas las cuentas en el treeview"""
        try:
            # Limpiar tree
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            cuentas = self.repo.listar_cuentas(solo_programador=True)
            
            for c in cuentas:
                visible = "🔒 Programador" if c.solo_programador else "👁️ Todos"
                telefono = c.telefono_asociado if c.telefono_asociado else "-"
                
                self.tree.insert('', 'end', values=(
                    c.idcuenta,
                    c.nombre_banco,
                    c.numero_cuenta,
                    c.tipo_cuenta,
                    c.moneda,
                    telefono,
                    visible
                ))
        except Exception as e:
            logger.error(f"Error listando cuentas: {e}")
            messagebox.showerror("Error", f"No se pudieron cargar las cuentas: {e}")
    
    def on_select(self, event):
        """Evento al seleccionar una cuenta"""
        seleccion = self.tree.selection()
        if seleccion:
            item = self.tree.item(seleccion[0])
            valores = item['values']
            if valores:
                self.cuenta_actual = self.repo.obtener_cuenta(valores[0])
    
    def editar_cuenta(self):
        """Carga la cuenta seleccionada para edición"""
        if not self.cuenta_actual:
            messagebox.showerror("Error", "Seleccione una cuenta")
            return
        
        messagebox.showinfo("Info", "Función de edición disponible en próxima versión.\nPor ahora puede desactivar y crear una nueva.")
    
    def desactivar_cuenta(self):
        """Desactiva la cuenta seleccionada"""
        if not self.cuenta_actual:
            messagebox.showerror("Error", "Seleccione una cuenta")
            return
        
        if messagebox.askyesno("Confirmar", f"¿Desactivar cuenta {self.cuenta_actual.numero_cuenta}?\n\nNo se eliminará, solo quedará inactiva."):
            if self.repo.desactivar_cuenta(self.cuenta_actual.idcuenta):
                messagebox.showinfo("Éxito", "Cuenta desactivada correctamente")
                self.listar_cuentas()
                self.cuenta_actual = None
            else:
                messagebox.showerror("Error", "No se pudo desactivar la cuenta")
    
    def guardar_cuenta(self):
        """Guarda una nueva cuenta"""
        # Validar campos obligatorios
        if not self.combo_banco.get():
            messagebox.showerror("Error", "Seleccione un banco")
            return
        
        if not self.entry_numero.get().strip():
            messagebox.showerror("Error", "Ingrese número de cuenta")
            return
        
        # Validar teléfono si es Pago Móvil (opcional pero con formato)
        telefono = self.entry_telefono.get().strip()
        if telefono and len(telefono) < 7:
            if not messagebox.askyesno("Advertencia", "El teléfono parece muy corto. ¿Guardar de todas formas?"):
                return
        
        # Obtener ID del banco seleccionado
        idx = self.combo_banco.current()
        if idx < 0 or idx >= len(self.bancos):
            messagebox.showerror("Error", "Banco inválido")
            return
        
        idbanco = self.bancos[idx].idbanco
        
        # Crear cuenta
        cuenta = CuentaEmpresa(
            idbanco=idbanco,
            numero_cuenta=self.entry_numero.get().strip(),
            tipo_cuenta=self.tipo_var.get(),
            moneda=self.moneda_var.get(),
            telefono_asociado=telefono or None,
            cedula_titular=self.entry_cedula.get().strip() or None,
            solo_programador=self.visible_var.get()
        )
        
        idcuenta = self.repo.crear_cuenta(cuenta)
        if idcuenta:
            messagebox.showinfo("Éxito", f"Cuenta creada con ID: {idcuenta}")
            # Limpiar campos
            self.entry_numero.delete(0, tk.END)
            self.entry_telefono.delete(0, tk.END)
            self.entry_cedula.delete(0, tk.END)
            self.visible_var.set(False)
            self.combo_banco.set('')
            # Actualizar lista
            self.listar_cuentas()
        else:
            messagebox.showerror("Error", "No se pudo crear la cuenta. Revise los datos.")
    
    def show(self):
        """Muestra el diálogo"""
        self.dialog.wait_window()
