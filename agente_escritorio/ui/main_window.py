"""
Ventana principal del Agente de Escritorio
Interfaz gráfica con Tkinter
"""
import tkinter as tk
from tkinter import ttk, messagebox, font
from datetime import datetime
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from loguru import logger
from agents.venta_agent import VentaAgent
from agents.cliente_agent import ClienteAgent
from agents.articulo_agent import ArticuloAgent

class UsuarioSesion:
    """Clase temporal para simular usuario (después se integra con tu sistema)"""
    def __init__(self):
        self.id = 1
        self.idtrabajador = 1
        self.nombre = "Admin"
        self.rol = "Administrador"

class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Sistema de Ventas - Agente de Escritorio")
        self.root.geometry("1200x700")
        self.root.minsize(1000, 600)
        
        # Configurar estilos
        self.setup_styles()
        
        # Usuario (temporal)
        self.usuario = UsuarioSesion()
        
        # Inicializar agentes
        self.venta_agent = VentaAgent(self.usuario)
        self.cliente_agent = ClienteAgent()
        self.articulo_agent = ArticuloAgent()
        
        # Estado de la venta actual
        self.carrito_items = []
        self.cliente_actual = None
        self.es_consumidor_final = True
        
        # Construir interfaz
        self.setup_ui()
        
        # Inicializar cliente por defecto
        self.cambiar_tipo_cliente()
        
        # Cargar datos iniciales
        self.actualizar_tasas()
        self.actualizar_historial()
        
    def setup_styles(self):
        """Configura los estilos de la interfaz"""
        style = ttk.Style()
        
        # Colores
        self.bg_color = "#f0f0f0"
        self.primary_color = "#2c3e50"
        self.secondary_color = "#3498db"
        self.success_color = "#27ae60"
        self.warning_color = "#e67e22"
        self.danger_color = "#e74c3c"
        
        self.root.configure(bg=self.bg_color)
        
        # Fuentes
        self.font_title = font.Font(family="Helvetica", size=16, weight="bold")
        self.font_normal = font.Font(family="Helvetica", size=10)
        self.font_small = font.Font(family="Helvetica", size=9)
        
    def setup_ui(self):
        """Construye toda la interfaz"""
        
        # ===== BARRA SUPERIOR =====
        top_frame = tk.Frame(self.root, bg=self.primary_color, height=50)
        top_frame.pack(fill='x')
        top_frame.pack_propagate(False)
        
        # Título
        title = tk.Label(top_frame, text="SISTEMA DE VENTAS", 
                        fg='white', bg=self.primary_color,
                        font=('Helvetica', 14, 'bold'))
        title.pack(side='left', padx=20, pady=10)
        
        # Usuario
        user_frame = tk.Frame(top_frame, bg=self.primary_color)
        user_frame.pack(side='right', padx=20)
        
        tk.Label(user_frame, text=f"👤 {self.usuario.nombre}", 
                fg='white', bg=self.primary_color,
                font=self.font_normal).pack(side='left', padx=5)
        
        tk.Label(user_frame, text=f"🔑 {self.usuario.rol}", 
                fg='#f1c40f', bg=self.primary_color,
                font=self.font_normal).pack(side='left', padx=5)
        
        # ===== BARRA DE ESTADO =====
        status_frame = tk.Frame(self.root, bg=self.secondary_color, height=30)
        status_frame.pack(fill='x')
        status_frame.pack_propagate(False)
        
        self.lbl_fecha = tk.Label(status_frame, 
                                 text=f"📅 {datetime.now().strftime('%d/%m/%Y %I:%M %p')}",
                                 fg='white', bg=self.secondary_color,
                                 font=self.font_small)
        self.lbl_fecha.pack(side='left', padx=20, pady=5)
        
        self.lbl_tasa = tk.Label(status_frame, 
                                text="💵 Tasa USD: Bs. 400.00",
                                fg='white', bg=self.secondary_color,
                                font=self.font_small)
        self.lbl_tasa.pack(side='left', padx=20, pady=5)
        
        # ===== PANEL PRINCIPAL =====
        main_panel = tk.PanedWindow(self.root, orient='horizontal', bg=self.bg_color)
        main_panel.pack(fill='both', expand=True, padx=10, pady=10)
        
        # === PANEL IZQUIERDO (Venta) ===
        left_frame = tk.Frame(main_panel, bg='white', relief='groove', bd=2)
        main_panel.add(left_frame, width=700)
        
        # Selección de cliente
        cliente_frame = tk.LabelFrame(left_frame, text=" Cliente ", 
                                     font=self.font_normal, bg='white')
        cliente_frame.pack(fill='x', padx=10, pady=10)
        
        self.tipo_cliente_var = tk.StringVar(value="CF")
        
        cf_radio = tk.Radiobutton(cliente_frame, text="Consumidor Final", 
                                  variable=self.tipo_cliente_var, value="CF",
                                  bg='white', command=self.cambiar_tipo_cliente)
        cf_radio.pack(side='left', padx=10, pady=5)
        
        cliente_radio = tk.Radiobutton(cliente_frame, text="Cliente Registrado", 
                                      variable=self.tipo_cliente_var, value="REG",
                                      bg='white', command=self.cambiar_tipo_cliente)
        cliente_radio.pack(side='left', padx=10, pady=5)
        
        # Búsqueda de cliente (inicialmente deshabilitado)
        self.cliente_busqueda_frame = tk.Frame(cliente_frame, bg='white')
        
        tk.Label(self.cliente_busqueda_frame, text="Documento:", 
                bg='white').pack(side='left', padx=5)
        
        self.entry_documento = tk.Entry(self.cliente_busqueda_frame, width=20)
        self.entry_documento.pack(side='left', padx=5)
        self.entry_documento.bind('<Return>', self.buscar_cliente)
        
        tk.Button(self.cliente_busqueda_frame, text="Buscar", 
                 command=self.buscar_cliente,
                 bg=self.secondary_color, fg='white').pack(side='left', padx=5)
        
        self.lbl_cliente_info = tk.Label(cliente_frame, text="Cliente: CONSUMIDOR FINAL",
                                        bg='white', fg=self.primary_color)
        self.lbl_cliente_info.pack(anchor='w', padx=10, pady=5)
        
        # Búsqueda de productos
        producto_frame = tk.LabelFrame(left_frame, text=" Agregar Producto ", 
                                      font=self.font_normal, bg='white')
        producto_frame.pack(fill='x', padx=10, pady=10)
        
        busqueda_frame = tk.Frame(producto_frame, bg='white')
        busqueda_frame.pack(fill='x', pady=5)
        
        tk.Label(busqueda_frame, text="Código/Nombre:", 
                bg='white').pack(side='left', padx=5)
        
        self.entry_busqueda = tk.Entry(busqueda_frame, width=40)
        self.entry_busqueda.pack(side='left', padx=5)
        self.entry_busqueda.bind('<Return>', self.agregar_producto_event)
        
        tk.Label(busqueda_frame, text="Cant:", bg='white').pack(side='left', padx=5)
        
        self.entry_cantidad = tk.Entry(busqueda_frame, width=5)
        self.entry_cantidad.insert(0, "1")
        self.entry_cantidad.pack(side='left', padx=5)
        
        tk.Button(busqueda_frame, text="Agregar", 
                 command=self.agregar_producto,
                 bg=self.success_color, fg='white').pack(side='left', padx=5)
        
        # Carrito de compras
        carrito_frame = tk.LabelFrame(left_frame, text=" Carrito ", 
                                     font=self.font_normal, bg='white')
        carrito_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Treeview para el carrito
        columns = ('Cant', 'Producto', 'Precio', 'Subtotal')
        self.tree_carrito = ttk.Treeview(carrito_frame, columns=columns, 
                                         show='headings', height=10)
        
        self.tree_carrito.heading('Cant', text='Cant')
        self.tree_carrito.heading('Producto', text='Producto')
        self.tree_carrito.heading('Precio', text='Precio $')
        self.tree_carrito.heading('Subtotal', text='Subtotal $')
        
        self.tree_carrito.column('Cant', width=60)
        self.tree_carrito.column('Producto', width=300)
        self.tree_carrito.column('Precio', width=80)
        self.tree_carrito.column('Subtotal', width=100)
        
        scrollbar = ttk.Scrollbar(carrito_frame, orient='vertical', 
                                  command=self.tree_carrito.yview)
        self.tree_carrito.configure(yscrollcommand=scrollbar.set)
        
        self.tree_carrito.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        self.tree_carrito.bind('<Double-1>', self.quitar_producto_event)
        
        # Totales
        totales_frame = tk.Frame(left_frame, bg='white', relief='ridge', bd=2)
        totales_frame.pack(fill='x', padx=10, pady=10)
        
        totales_inner = tk.Frame(totales_frame, bg='white')
        totales_inner.pack(anchor='e', padx=20, pady=10)
        
        self.lbl_subtotal = tk.Label(totales_inner, text="Subtotal: $0.00",
                                    bg='white', font=self.font_normal)
        self.lbl_subtotal.pack(anchor='e')
        
        self.lbl_iva = tk.Label(totales_inner, text="IVA: $0.00",
                               bg='white', font=self.font_normal)
        self.lbl_iva.pack(anchor='e')
        
        self.lbl_total_usd = tk.Label(totales_inner, text="TOTAL USD: $0.00",
                                     bg='white', font=('Helvetica', 12, 'bold'))
        self.lbl_total_usd.pack(anchor='e', pady=5)
        
        self.lbl_total_bs = tk.Label(totales_inner, text=f"TOTAL Bs: Bs.0.00",
                                    bg='white', font=self.font_normal)
        self.lbl_total_bs.pack(anchor='e')
        
        # Botón procesar
        btn_procesar = tk.Button(left_frame, text="PROCESAR VENTA", 
                                command=self.procesar_venta,
                                bg=self.success_color, fg='white',
                                font=('Helvetica', 12, 'bold'),
                                height=2)
        btn_procesar.pack(fill='x', padx=10, pady=10)
        
        # === PANEL DERECHO (Información) ===
        right_frame = tk.Frame(main_panel, bg='white', relief='groove', bd=2)
        main_panel.add(right_frame, width=400)
        
        # Notebook (pestañas)
        notebook = ttk.Notebook(right_frame)
        notebook.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Pestaña: Historial de ventas
        historial_frame = tk.Frame(notebook, bg='white')
        notebook.add(historial_frame, text='Últimas Ventas')
        
        columns_hist = ('ID', 'Fecha', 'Cliente', 'Total $', 'Total Bs')
        self.tree_historial = ttk.Treeview(historial_frame, columns=columns_hist,
                                           show='headings', height=15)
        
        for col in columns_hist:
            self.tree_historial.heading(col, text=col)
            self.tree_historial.column(col, width=70)
        
        self.tree_historial.column('Cliente', width=120)
        self.tree_historial.column('Total Bs', width=80)
        
        scroll_hist = ttk.Scrollbar(historial_frame, orient='vertical',
                                    command=self.tree_historial.yview)
        self.tree_historial.configure(yscrollcommand=scroll_hist.set)
        
        self.tree_historial.pack(side='left', fill='both', expand=True)
        scroll_hist.pack(side='right', fill='y')
        
        # Pestaña: Stock crítico
        stock_frame = tk.Frame(notebook, bg='white')
        notebook.add(stock_frame, text='Stock Crítico')
        
        self.tree_stock = ttk.Treeview(stock_frame, 
                                       columns=('Producto', 'Stock', 'Mínimo'),
                                       show='headings', height=15)
        
        self.tree_stock.heading('Producto', text='Producto')
        self.tree_stock.heading('Stock', text='Stock')
        self.tree_stock.heading('Mínimo', text='Mínimo')
        
        self.tree_stock.column('Producto', width=200)
        self.tree_stock.column('Stock', width=60)
        self.tree_stock.column('Mínimo', width=60)
        
        scroll_stock = ttk.Scrollbar(stock_frame, orient='vertical',
                                     command=self.tree_stock.yview)
        self.tree_stock.configure(yscrollcommand=scroll_stock.set)
        
        self.tree_stock.pack(side='left', fill='both', expand=True)
        scroll_stock.pack(side='right', fill='y')
        
    def cambiar_tipo_cliente(self):
        """Cambia entre Consumidor Final y Cliente Registrado"""
        self.es_consumidor_final = (self.tipo_cliente_var.get() == "CF")
        
        if self.es_consumidor_final:
            self.cliente_busqueda_frame.pack_forget()
            # Obtener el ID del consumidor final
            self.cliente_actual = self.cliente_agent.obtener_consumidor_final()
            if self.cliente_actual:
                self.lbl_cliente_info.config(text="Cliente: CONSUMIDOR FINAL")
                self.venta_agent.cliente_actual = self.cliente_actual
                self.venta_agent.es_consumidor_final = True
                logger.info(f"✅ Consumidor Final seleccionado (ID: {self.cliente_actual})")
            else:
                self.lbl_cliente_info.config(text="Cliente: ERROR - No existe CF")
                self.cliente_actual = None
        else:
            self.cliente_busqueda_frame.pack(fill='x', pady=5)
            self.lbl_cliente_info.config(text="Cliente: No seleccionado")
            self.cliente_actual = None
            self.venta_agent.cliente_actual = None
            self.venta_agent.es_consumidor_final = False
    
    def buscar_cliente(self, event=None):
        """Busca un cliente por documento"""
        documento = self.entry_documento.get().strip()
        if not documento:
            return
        
        cliente = self.cliente_agent.buscar_por_documento(documento)
        
        if cliente:
            self.cliente_actual = cliente.get('idcliente')
            nombre = f"{cliente.get('nombre')} {cliente.get('apellidos')}"
            self.lbl_cliente_info.config(text=f"Cliente: {nombre}")
            self.venta_agent.cliente_actual = self.cliente_actual
            logger.info(f"✅ Cliente encontrado: {nombre}")
        else:
            messagebox.showerror("Error", "Cliente no encontrado")
            self.entry_documento.focus()
    
    def agregar_producto_event(self, event=None):
        """Wrapper para agregar producto desde evento"""
        self.agregar_producto()
    
    def agregar_producto(self):
        """Agrega un producto al carrito"""
        busqueda = self.entry_busqueda.get().strip()
        if not busqueda:
            messagebox.showwarning("Advertencia", "Ingrese código o nombre")
            return
        
        try:
            cantidad = int(self.entry_cantidad.get())
            if cantidad <= 0:
                raise ValueError
        except:
            messagebox.showwarning("Advertencia", "Cantidad inválida")
            return
        
        # Buscar producto
        producto = self.venta_agent.buscar_producto(busqueda)
        
        if not producto:
            messagebox.showerror("Error", "Producto no encontrado")
            return
        
        # Agregar al carrito
        self.venta_agent.es_consumidor_final = self.es_consumidor_final
        if self.venta_agent.agregar_producto(producto, cantidad):
            self.actualizar_carrito()
            self.entry_busqueda.delete(0, tk.END)
            self.entry_busqueda.focus()
    
    def quitar_producto_event(self, event):
        """Elimina producto del carrito al hacer doble clic"""
        selection = self.tree_carrito.selection()
        if selection:
            idx = self.tree_carrito.index(selection[0])
            self.venta_agent.quitar_producto(idx)
            self.actualizar_carrito()
    
    def actualizar_carrito(self):
        """Actualiza la vista del carrito"""
        # Limpiar tree
        for item in self.tree_carrito.get_children():
            self.tree_carrito.delete(item)
        
        # Agregar productos
        for item in self.venta_agent.carrito:
            self.tree_carrito.insert('', 'end', values=(
                item['cantidad'],
                item['nombre'],
                f"${item['precio_unitario']:.2f}",
                f"${item['subtotal']:.2f}"
            ))
        
        # Actualizar totales
        totales = self.venta_agent.calcular_totales()
        self.lbl_subtotal.config(text=f"Subtotal: ${totales['subtotal_usd']:.2f}")
        self.lbl_iva.config(text=f"IVA: ${totales['iva_usd']:.2f}")
        self.lbl_total_usd.config(text=f"TOTAL USD: ${totales['total_usd']:.2f}")
        self.lbl_total_bs.config(text=f"TOTAL Bs: Bs.{totales['total_bs']:.2f}")
    
    def procesar_venta(self):
        """Procesa la venta actual"""
        if not self.venta_agent.carrito:
            messagebox.showwarning("Advertencia", "No hay productos en el carrito")
            return
        
        if not self.venta_agent.cliente_actual:
            messagebox.showerror("Error", "No hay cliente seleccionado")
            return
        
        totales = self.venta_agent.calcular_totales()
        
        # Ventana de confirmación
        respuesta = messagebox.askyesno(
            "Confirmar Venta",
            f"Total: ${totales['total_usd']:.2f} (Bs. {totales['total_bs']:.2f})\n"
            f"¿Procesar venta?"
        )
        
        if respuesta:
            # Procesar venta
            resultado = self.venta_agent.procesar_venta()
            
            if resultado['success']:
                messagebox.showinfo(
                    "Éxito",
                    f"Venta #{resultado['idventa']} procesada\n"
                    f"Total: ${resultado['totales']['total_usd']:.2f}"
                )
                self.actualizar_carrito()
                self.actualizar_historial()
            else:
                messagebox.showerror("Error", resultado.get('error', 'Error desconocido'))
    
    def actualizar_historial(self):
        """Actualiza el historial de ventas"""
        # Limpiar tree
        for item in self.tree_historial.get_children():
            self.tree_historial.delete(item)
        
        # Obtener historial
        ventas = self.venta_agent.obtener_historial(20)
        
        for venta in ventas:
            self.tree_historial.insert('', 'end', values=(
                venta['idventa'],
                venta['fecha'].strftime('%d/%m/%Y') if venta['fecha'] else '',
                venta['cliente'][:20],
                f"${venta['monto_usd']:.2f}",
                f"Bs.{venta['monto_bs']:.2f}"
            ))
    
    def actualizar_tasas(self):
        """Actualiza la tasa de cambio en la interfaz"""
        self.lbl_tasa.config(text=f"💵 Tasa USD: Bs. {self.venta_agent.tasa_cambio:.2f}")
        self.root.after(60000, self.actualizar_tasas)  # Actualizar cada minuto
    
    def run(self):
        """Inicia la aplicación"""
        self.root.mainloop()
    
    def __del__(self):
        """Limpieza al cerrar"""
        try:
            self.venta_agent.cerrar()
        except:
            pass

if __name__ == "__main__":
    app = MainWindow()
    app.run()
