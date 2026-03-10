"""
Ventana principal con búsqueda inteligente - VERSIÓN CORREGIDA
"""
import tkinter as tk
from tkinter import ttk, messagebox, font
from datetime import datetime
import sys
from pathlib import Path

# Ajustar path para encontrar los módulos
current_dir = Path(__file__).parent.absolute()
project_root = current_dir.parent.parent  # /home/junior/Escritorio/sistema-ventas-python
agents_dir = project_root / 'agente_escritorio' / 'agents'

if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(agents_dir) not in sys.path:
    sys.path.insert(0, str(agents_dir))

from loguru import logger

# Ahora importamos directamente desde agents
from agents.venta_agent import VentaAgent
from agents.cliente_agent import ClienteAgent
from agents.articulo_agent import ArticuloAgent

class BusquedaProductoDialog:
    """Diálogo de búsqueda de productos"""
    
    def __init__(self, parent, articulo_agent):
        self.parent = parent
        self.articulo_agent = articulo_agent
        self.resultado = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Buscar Producto")
        self.dialog.geometry("800x500")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.setup_ui()
        self.dialog.bind('<Escape>', lambda e: self.dialog.destroy())
        
    def setup_ui(self):
        # Campo de búsqueda
        search_frame = tk.Frame(self.dialog)
        search_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Label(search_frame, text="Buscar producto:", 
                font=('Helvetica', 11, 'bold')).pack(side='left', padx=5)
        
        self.entry_busqueda = tk.Entry(search_frame, width=50, font=('Helvetica', 11))
        self.entry_busqueda.pack(side='left', padx=5)
        self.entry_busqueda.bind('<KeyRelease>', self.buscar_productos)
        self.entry_busqueda.focus()
        
        # Tabla de resultados
        table_frame = tk.Frame(self.dialog)
        table_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        columns = ('ID', 'Código', 'Producto', 'Precio $', 'Stock')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)
        
        self.tree.heading('ID', text='ID')
        self.tree.heading('Código', text='Código')
        self.tree.heading('Producto', text='Producto')
        self.tree.heading('Precio $', text='Precio $')
        self.tree.heading('Stock', text='Stock')
        
        self.tree.column('ID', width=50)
        self.tree.column('Código', width=100)
        self.tree.column('Producto', width=350)
        self.tree.column('Precio $', width=80)
        self.tree.column('Stock', width=60)
        
        scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        self.tree.bind('<Double-1>', self.seleccionar_producto)
        
        # Botones
        btn_frame = tk.Frame(self.dialog)
        btn_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Button(btn_frame, text="Seleccionar", command=self.seleccionar_producto,
                 bg='#27ae60', fg='white', font=('Helvetica', 10)).pack(side='right', padx=5)
        
        tk.Button(btn_frame, text="Cancelar", command=self.dialog.destroy,
                 bg='#e74c3c', fg='white', font=('Helvetica', 10)).pack(side='right', padx=5)
    
    def buscar_productos(self, event=None):
        termino = self.entry_busqueda.get().strip()
        
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if len(termino) < 2:
            return
        
        print(f"\n🔍 Buscando: '{termino}'")
        resultados = self.articulo_agent.buscar_por_nombre(termino)
        print(f"📦 Resultados: {len(resultados)}")
        
        for prod in resultados[:20]:
            self.tree.insert('', 'end', values=(
                prod.get('idarticulo', ''),
                prod.get('codigo', ''),
                prod.get('nombre', '')[:40],
                f"${prod.get('precio_venta', 0):.2f}",
                prod.get('stock_actual', 0)
            ))
    
    def seleccionar_producto(self, event=None):
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            self.resultado = {
                'idarticulo': item['values'][0],
                'codigo': item['values'][1],
                'nombre': item['values'][2],
                'precio': float(item['values'][3].replace('$', '')),
                'stock': item['values'][4]
            }
            print(f"\n✅ Producto seleccionado: {self.resultado}")
            self.dialog.destroy()
    
    def show(self):
        self.dialog.wait_window()
        return self.resultado


class CantidadDialog:
    """Diálogo para ingresar cantidad"""
    
    def __init__(self, parent, producto, max_stock=999):
        self.resultado = None
        self.producto = producto
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Cantidad")
        self.dialog.geometry("300x200")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Info del producto
        tk.Label(self.dialog, text=f"Producto: {producto['nombre']}",
                font=('Helvetica', 11, 'bold')).pack(pady=10)
        
        tk.Label(self.dialog, text=f"Precio: ${producto['precio']:.2f}",
                font=('Helvetica', 10)).pack()
        
        tk.Label(self.dialog, text=f"Stock disponible: {max_stock}",
                font=('Helvetica', 10)).pack(pady=5)
        
        # Entrada de cantidad
        frame = tk.Frame(self.dialog)
        frame.pack(pady=10)
        
        tk.Label(frame, text="Cantidad:", font=('Helvetica', 10)).pack(side='left', padx=5)
        
        self.entry_cantidad = tk.Entry(frame, width=10, font=('Helvetica', 12))
        self.entry_cantidad.pack(side='left', padx=5)
        self.entry_cantidad.insert(0, "1")
        self.entry_cantidad.select_range(0, 'end')
        self.entry_cantidad.focus()
        self.entry_cantidad.bind('<Return>', self.aceptar)
        
        # Botones
        btn_frame = tk.Frame(self.dialog)
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="Aceptar", command=self.aceptar,
                 bg='#27ae60', fg='white', width=10).pack(side='left', padx=5)
        
        tk.Button(btn_frame, text="Cancelar", command=self.dialog.destroy,
                 bg='#e74c3c', fg='white', width=10).pack(side='left', padx=5)
        
        self.dialog.bind('<Escape>', lambda e: self.dialog.destroy())
    
    def aceptar(self, event=None):
        try:
            cantidad = int(self.entry_cantidad.get())
            if cantidad <= 0:
                raise ValueError
            if cantidad > self.producto['stock']:
                messagebox.showerror("Error", f"Stock insuficiente. Máximo: {self.producto['stock']}")
                return
            self.resultado = cantidad
            print(f"✅ Cantidad seleccionada: {cantidad}")
            self.dialog.destroy()
        except:
            messagebox.showerror("Error", "Cantidad inválida")
    
    def show(self):
        self.dialog.wait_window()
        return self.resultado


class MainWindowInteligente:
    def __init__(self):
        print("\n" + "="*50)
        print("INICIALIZANDO VENTANA PRINCIPAL")
        print("="*50)
        
        self.root = tk.Tk()
        self.root.title("Sistema de Ventas - Agente Inteligente")
        self.root.geometry("1300x750")
        self.root.minsize(1100, 650)
        
        self.setup_styles()
        
        # Usuario temporal
        class Usuario:
            def __init__(self):
                self.id = 1
                self.idtrabajador = 1
                self.nombre = "Admin"
                self.rol = "Administrador"
        
        self.usuario_actual = Usuario()  # ← CAMBIAR a usuario_actual
        print("✅ Usuario creado")
        
        # Inicializar agentes
        self.venta_agent = VentaAgent(self.usuario_actual)
        self.cliente_agent = ClienteAgent()
        self.articulo_agent = ArticuloAgent()
        
        # Inicializar programador agent (para comandos ocultos)
        from agents.programador_agent import ProgramadorAgent
        try:
            self.programador_agent = ProgramadorAgent(usuario_actual=self.usuario_actual, parent=self)
        except PermissionError:
            self.programador_agent = None
            logger.warning("⚠️ No se pudo inicializar ProgramadorAgent - permisos insuficientes")
        
        # Inicializar sistema de notificaciones
        if hasattr(self.venta_agent, 'cashea_agent'):
            self.venta_agent.cashea_agent.crear_endpoint_notificacion()
                    
        # Estado
        self.carrito_items = []
        self.cliente_actual = None
        self.es_consumidor_final = True
        
        print("🖥️ Construyendo interfaz...")
        self.setup_ui()
        self.cambiar_tipo_cliente()
        self.actualizar_tasas()
        self.actualizar_historial()
        print("✅ Interfaz lista\n")
        self.actualizar_opciones_pago() 
        self.actualizar_notificaciones()
        self.setup_programador_shortcut()
        
    def setup_styles(self):
        self.bg_color = "#f0f0f0"
        self.primary_color = "#2c3e50"
        self.secondary_color = "#3498db"
        self.success_color = "#27ae60"
        self.warning_color = "#e67e22"
        self.danger_color = "#e74c3c"
        self.root.configure(bg=self.bg_color)
        
    def setup_ui(self):
        # === BARRA SUPERIOR ===
        top_frame = tk.Frame(self.root, bg=self.primary_color, height=50)
        top_frame.pack(fill='x')
        top_frame.pack_propagate(False)
        
        tk.Label(top_frame, text="SISTEMA DE VENTAS INTELIGENTE", 
                fg='white', bg=self.primary_color,
                font=('Helvetica', 16, 'bold')).pack(side='left', padx=20, pady=10)

        # 👇 NUEVO: Frame para la campanita y usuario (AGREGA ESTO)
        right_frame = tk.Frame(top_frame, bg=self.primary_color)
        right_frame.pack(side='right', padx=20)
        
        # Campanita de notificaciones
        self.btn_notificaciones = tk.Button(right_frame, text="🔔", 
                                           font=('Helvetica', 14),
                                           bg=self.primary_color, fg='white',
                                           bd=0, command=self.mostrar_notificaciones)
        self.btn_notificaciones.pack(side='left', padx=10)
        
        # Label para contador (inicialmente invisible)
        self.lbl_notif_count = tk.Label(right_frame, text="", 
                                       bg='red', fg='white',
                                       font=('Helvetica', 8))
        self.lbl_notif_count.place_configure(relx=0.7, rely=0.1)
        
        # Usuario
        tk.Label(right_frame, text=f"👤 {self.usuario_actual.nombre}", 
        fg='white', bg=self.primary_color).pack(side='left', padx=5)
      
         # === BARRA DE ESTADO ===
        status_frame = tk.Frame(self.root, bg=self.secondary_color, height=30)
        status_frame.pack(fill='x')
        status_frame.pack_propagate(False)
        
        self.lbl_fecha = tk.Label(status_frame, 
                                 text=f"📅 {datetime.now().strftime('%d/%m/%Y %I:%M %p')}",
                                 fg='white', bg=self.secondary_color)
        self.lbl_fecha.pack(side='left', padx=20, pady=5)
        
        self.lbl_tasa = tk.Label(status_frame, text="💵 Tasa USD: Bs. 400.00",
                                fg='white', bg=self.secondary_color)
        self.lbl_tasa.pack(side='left', padx=20, pady=5)
        
        # === PANEL PRINCIPAL ===
        main_panel = tk.PanedWindow(self.root, orient='horizontal', bg=self.bg_color)
        main_panel.pack(fill='both', expand=True, padx=10, pady=10)
        
        # === PANEL IZQUIERDO ===
        left_frame = tk.Frame(main_panel, bg='white', relief='groove', bd=2)
        main_panel.add(left_frame, width=800)
        
        # Selección de cliente
        cliente_frame = tk.LabelFrame(left_frame, text=" Cliente ", font=('Helvetica', 10, 'bold'), bg='white')
        cliente_frame.pack(fill='x', padx=10, pady=10)
        
        self.tipo_cliente_var = tk.StringVar(value="CF")
        
        tk.Radiobutton(cliente_frame, text="Consumidor Final", variable=self.tipo_cliente_var,
                      value="CF", bg='white', command=self.cambiar_tipo_cliente).pack(side='left', padx=10)
        
        tk.Radiobutton(cliente_frame, text="Cliente Registrado", variable=self.tipo_cliente_var,
                      value="REG", bg='white', command=self.cambiar_tipo_cliente).pack(side='left', padx=10)
        
        self.lbl_cliente_info = tk.Label(cliente_frame, text="Cliente: CONSUMIDOR FINAL",
                                        bg='white', fg=self.primary_color, font=('Helvetica', 10, 'bold'))
        self.lbl_cliente_info.pack(anchor='w', padx=10, pady=5)
        
        # Botón de búsqueda
        busqueda_frame = tk.LabelFrame(left_frame, text=" Agregar Producto ", font=('Helvetica', 10, 'bold'), bg='white')
        busqueda_frame.pack(fill='x', padx=10, pady=10)
        
        btn_buscar = tk.Button(busqueda_frame, text="🔍 BUSCAR PRODUCTO", 
                               command=self.abrir_buscador,
                               bg=self.secondary_color, fg='white',
                               font=('Helvetica', 12, 'bold'),
                               height=2)
        btn_buscar.pack(fill='x', padx=20, pady=10)
        
        # Carrito de compras
        carrito_frame = tk.LabelFrame(left_frame, text=" Carrito de Compras ", font=('Helvetica', 10, 'bold'), bg='white')
        carrito_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Columnas: Cant | Producto | Precio $ | Precio Bs. | Subtotal Bs.
        columns = ('Cant', 'Producto', 'Precio $', 'Precio Bs.', 'Subtotal Bs.')
        self.tree_carrito = ttk.Treeview(carrito_frame, columns=columns, show='headings', height=8)
        
        # Configurar encabezados
        self.tree_carrito.heading('Cant', text='Cant')
        self.tree_carrito.heading('Producto', text='Producto')
        self.tree_carrito.heading('Precio $', text='Precio $')
        self.tree_carrito.heading('Precio Bs.', text='Precio Bs.')
        self.tree_carrito.heading('Subtotal Bs.', text='Subtotal Bs.')
        
        # Configurar anchos de columna
        self.tree_carrito.column('Cant', width=50)
        self.tree_carrito.column('Producto', width=300)
        self.tree_carrito.column('Precio $', width=70)
        self.tree_carrito.column('Precio Bs.', width=80)
        self.tree_carrito.column('Subtotal Bs.', width=90)
        
        scrollbar = ttk.Scrollbar(carrito_frame, orient='vertical', command=self.tree_carrito.yview)
        self.tree_carrito.configure(yscrollcommand=scrollbar.set)
        
        self.tree_carrito.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        self.tree_carrito.bind('<Double-1>', self.quitar_producto)
        
                # === FORMAS DE PAGO ===
        pago_frame = tk.LabelFrame(left_frame, text=" Formas de Pago ", 
                                   font=('Helvetica', 10, 'bold'), bg='white')
        pago_frame.pack(fill='x', padx=10, pady=5)
        
        # Frame interno para los botones
        botones_pago = tk.Frame(pago_frame, bg='white')
        botones_pago.pack(pady=5)
        
        # Botones de pago
        self.btn_efectivo = tk.Button(botones_pago, text="Efectivo", 
                                      bg='#27ae60', fg='white', width=12,
                                      command=self.pagar_efectivo) 
        self.btn_efectivo.pack(side='left', padx=5)
        
        self.btn_transferencia = tk.Button(botones_pago, text="Transferencia", 
                                          bg='#3498db', fg='white', width=12,
                                          command=lambda: self.procesar_pago('TRANSFERENCIA'))
        self.btn_transferencia.pack(side='left', padx=5)
        
        self.btn_tarjeta = tk.Button(botones_pago, text="Tarjeta", 
                                    bg='#f39c12', fg='white', width=12,
                                     command=self.pagar_tarjeta)
        self.btn_tarjeta.pack(side='left', padx=5)
        
        # Botón Cashea (inicialmente visible si está activo)
        self.btn_cashea = tk.Button(botones_pago, text="Cashea", 
                                   bg='#9b59b6', fg='white', width=12,
                                   command=self.pagar_con_cashea)
        
  	# 🔥 NUEVO BOTÓN PAGO MIXTO                          
        self.btn_pago_mixto = tk.Button(botones_pago, text="PAGO MIXTO", 
                                       bg='#e74c3c', fg='white', width=12,
                                       command=self.pago_mixto)
        self.btn_pago_mixto.pack(side='left', padx=5)                                   
                                   
        # La visibilidad se controla con actualizar_opciones_pago()
         
        self.btn_simular = tk.Button(botones_pago, text="🔔 Simular", 
                                    bg='#e67e22', fg='white', width=10,
                                    command=self.simular_notificacion_cashea)
        self.btn_simular.pack(side='left', padx=5)         
         
        # Totales
        totales_frame = tk.Frame(left_frame, bg='white', relief='ridge', bd=2)
        totales_frame.pack(fill='x', padx=10, pady=10)
        
        self.totales_inner = tk.Frame(totales_frame, bg='white')
        self.totales_inner.pack(anchor='e', padx=20, pady=10)
        
        self.lbl_subtotal = tk.Label(self.totales_inner, text="SUBTTL Bs.0",
                                    bg='white', font=('Helvetica', 10, 'bold'))
        self.lbl_subtotal.pack(anchor='e')
        
        # Labels para desglose
        self.lbl_exento = tk.Label(self.totales_inner, text="Exento: Bs.0",
                                   bg='white', font=('Helvetica', 10))
        self.lbl_exento.pack(anchor='e')
        
        self.lbl_base = tk.Label(self.totales_inner, text="Base G: Bs.0",
                                bg='white', font=('Helvetica', 10))
        self.lbl_base.pack(anchor='e')
        
        self.lbl_iva = tk.Label(self.totales_inner, text="IVA: Bs.0",
                               bg='white', font=('Helvetica', 10))
        self.lbl_iva.pack(anchor='e')
        
        self.lbl_total_bs = tk.Label(self.totales_inner, text="TOTAL: Bs.0",
                                     bg='white', font=('Helvetica', 14, 'bold'))
        self.lbl_total_bs.pack(anchor='e', pady=5)
        
         # Botón procesar
        btn_procesar = tk.Button(left_frame, text="💰 PROCESAR VENTA 💰", 
                                command=self.procesar_venta,
                                bg=self.success_color, fg='white',
                                font=('Helvetica', 14, 'bold'),
                                height=2)
        btn_procesar.pack(fill='x', padx=10, pady=10)
        
        # === PANEL DERECHO ===
        right_frame = tk.Frame(main_panel, bg='white', relief='groove', bd=2)
        main_panel.add(right_frame, width=400)
        
        notebook = ttk.Notebook(right_frame)
        notebook.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Pestaña: Historial
        historial_frame = tk.Frame(notebook, bg='white')
        notebook.add(historial_frame, text='Últimas Ventas')
        
        columns_hist = ('ID', 'Fecha', 'Cliente', 'Total $')
        self.tree_historial = ttk.Treeview(historial_frame, columns=columns_hist,
                                           show='headings', height=20)
        
        for col in columns_hist:
            self.tree_historial.heading(col, text=col)
            self.tree_historial.column(col, width=70)
        
        self.tree_historial.column('Cliente', width=150)
        
        scroll_hist = ttk.Scrollbar(historial_frame, orient='vertical',
                                    command=self.tree_historial.yview)
        self.tree_historial.configure(yscrollcommand=scroll_hist.set)
        
        self.tree_historial.pack(side='left', fill='both', expand=True)
        scroll_hist.pack(side='right', fill='y')
        
    def cambiar_tipo_cliente(self):
        self.es_consumidor_final = (self.tipo_cliente_var.get() == "CF")
        if self.es_consumidor_final:
            self.cliente_actual = self.cliente_agent.obtener_consumidor_final()
            self.lbl_cliente_info.config(text="Cliente: CONSUMIDOR FINAL")
            self.venta_agent.es_consumidor_final = True
        else:
            self.lbl_cliente_info.config(text="Cliente: No seleccionado")
            self.venta_agent.es_consumidor_final = False

    def actualizar_opciones_pago(self):
        """Actualiza las opciones de pago según configuración"""
        if hasattr(self, 'btn_cashea'):
            if hasattr(self.venta_agent, 'cashea_activo') and self.venta_agent.cashea_activo():
                self.btn_cashea.pack(side='left', padx=5)
            else:
                self.btn_cashea.pack_forget()
    
    def abrir_buscador(self):
        print("\n" + "="*60)
        print("🔍 ABRIENDO BUSCADOR DE PRODUCTOS")
        print("="*60)
        
        dialog = BusquedaProductoDialog(self.root, self.articulo_agent)
        producto = dialog.show()
        
        if producto:
            print(f"\n✅ PRODUCTO SELECCIONADO:")
            print(f"   ID: {producto.get('idarticulo')}")
            print(f"   Nombre: {producto.get('nombre')}")
            print(f"   Precio: ${producto.get('precio', 0)}")
            print(f"   Stock: {producto.get('stock', 0)}")
            
            # Pedir cantidad
            cant_dialog = CantidadDialog(self.root, producto, producto['stock'])
            cantidad = cant_dialog.show()
            
            if cantidad:
                print(f"\n✅ CANTIDAD SELECCIONADA: {cantidad}")
                
                # IMPORTANTE: Incluir stock_actual en el diccionario
                prod_dict = {
                    'idarticulo': producto['idarticulo'],
                    'nombre': producto['nombre'],
                    'precio_venta': producto.get('precio', 0),
                    'stock_actual': producto.get('stock', 0)  # ← ESTO ES CRÍTICO
                }
                
                print(f"📤 Enviando a venta_agent: {prod_dict}")
                
                self.venta_agent.es_consumidor_final = self.es_consumidor_final
                resultado = self.venta_agent.agregar_producto(prod_dict, cantidad)
                
                print(f"📥 Resultado de agregar_producto: {resultado}")
                
                if resultado:
                    print("✅ Producto agregado, actualizando carrito...")
                    self.actualizar_carrito()
                    print("✅ Carrito actualizado")
                else:
                    print("❌ No se pudo agregar el producto")
            else:
                print("❌ No se seleccionó cantidad")
        else:
            print("❌ No se seleccionó producto")
    
    def quitar_producto(self, event):
        selection = self.tree_carrito.selection()
        if selection:
            idx = self.tree_carrito.index(selection[0])
            self.venta_agent.quitar_producto(idx)
            self.actualizar_carrito()
            print("➖ Producto quitado del carrito")
    
    def actualizar_carrito(self):
        """Actualiza la vista del carrito con formato venezolano"""
        print("🔄 Actualizando vista del carrito...")
        
        # Limpiar tree
        for item in self.tree_carrito.get_children():
            self.tree_carrito.delete(item)
        
        # Configurar tags para colores según letra fiscal
        self.tree_carrito.tag_configure('exento', background='#e8f5e8')  # Verde claro
        self.tree_carrito.tag_configure('gravado', background='#fff3e0')  # Naranja claro
        
        # Obtener tasa de cambio
        tasa = self.venta_agent.tasa_cambio
        subtotal_bs_total = 0.0
        
        # Agregar productos al carrito
        for item in self.venta_agent.carrito:
            letra = item.get('letra', '?')
            nombre_con_letra = f"{item['nombre']} ({letra})"
            
            # Calcular montos
            precio_usd = item['precio_unitario']
            precio_bs = precio_usd * tasa
            subtotal_bs = item['subtotal'] * tasa
            subtotal_bs_total += subtotal_bs
            
            # Determinar tag para color según letra
            tag = 'exento' if letra == 'E' else 'gravado'
            
            # Formatear precios
            precio_usd_str = f"${precio_usd:.2f}".replace('.', ',')
            precio_bs_str = f"Bs.{precio_bs:.0f}".replace('.', ',')
            subtotal_bs_str = f"Bs.{subtotal_bs:.0f}".replace('.', ',')
            
            # Insertar en el carrito
            self.tree_carrito.insert('', 'end', values=(
                item['cantidad'],
                nombre_con_letra,
                precio_usd_str,
                precio_bs_str,
                subtotal_bs_str
            ), tags=(tag,))
        
        # Calcular totales fiscales con la nueva lógica
        totales_usd = self.venta_agent.calcular_totales_con_impuestos()
        tasa = self.venta_agent.tasa_cambio
        
        # Convertir a Bs.
        exento_bs = totales_usd['exento'] * tasa
        base_gravada_bs = totales_usd['base_gravada_usd'] * tasa
        iva_bs = base_gravada_bs * 0.16  # IVA = Base gravada Bs. × 16%
        total_bs = totales_usd['total_con_iva'] * tasa  # Total con IVA incluido
        
        # Calcular subtotal (sin IVA) para mostrarlo
        subtotal_sin_iva_bs = exento_bs + base_gravada_bs
        
        # Actualizar SUBTTL (subtotal sin IVA)
        self.lbl_subtotal.config(text=f"SUBTTL Bs.{subtotal_sin_iva_bs:.0f}".replace('.', ','))
        
        # Actualizar desglose fiscal
        if hasattr(self, 'lbl_exento') and self.lbl_exento:
            self.lbl_exento.config(text=f"Exento: Bs.{exento_bs:.0f}".replace('.', ','))
        
        if hasattr(self, 'lbl_base') and self.lbl_base:
            self.lbl_base.config(text=f"Base G: Bs.{base_gravada_bs:.0f}".replace('.', ','))
        
        self.lbl_iva.config(text=f"IVA: Bs.{iva_bs:.0f}".replace('.', ','))
        self.lbl_total_bs.config(text=f"TOTAL: Bs.{total_bs:.0f}".replace('.', ','))
        
        print(f"📊 SUBTTL: Bs.{subtotal_sin_iva_bs:.0f}, Exento: {exento_bs:.0f}, Base G: {base_gravada_bs:.0f}, IVA: {iva_bs:.0f}, TOTAL: {total_bs:.0f}")
    
    def procesar_venta(self, tipo_pago='EFECTIVO', pago_info=None):
        """Procesa la venta actual con información de pago"""
        if not self.venta_agent.carrito:
            messagebox.showwarning("Advertencia", "No hay productos en el carrito")
            return
        
        # Procesar venta
        resultado = self.venta_agent.procesar_venta(tipo_pago=tipo_pago, pago_info=pago_info)
        
        if resultado['success']:
            # Construir mensaje detallado
            mensaje = f"✅ Venta #{resultado['idventa']} procesada\n\n"
            mensaje += f"💰 Total: ${resultado['totales']['usd']:.2f} (Bs.{resultado['totales']['bs']:.2f})\n"
            
            # Mostrar IGTF si se aplicó (revisar en pago_info)
            if pago_info and pago_info.get('igtf_aplicado', False):
                igtf_porcentaje = pago_info.get('igtf_porcentaje', 3)
                igtf_monto = pago_info.get('igtf_monto', 0)
                mensaje += f"📊 IGTF ({igtf_porcentaje}%): +${igtf_monto:.2f}\n"
            
            # Mostrar comisión si existe
            if resultado['totales'].get('comision', 0) > 0:
                mensaje += f"💳 Comisión: -${resultado['totales']['comision']:.2f}\n"
                mensaje += f"🏦 Neto negocio: ${resultado['totales']['neto']:.2f}\n"
            
            messagebox.showinfo("✅ Éxito", mensaje)
            
            self.actualizar_carrito()
            self.actualizar_historial()
        else:
            messagebox.showerror("❌ Error", resultado.get('error', 'Error desconocido'))

    def procesar_pago(self, tipo_pago):
        """Procesa el pago según el tipo seleccionado"""
        if not self.venta_agent.carrito:
            messagebox.showwarning("Advertencia", "No hay productos en el carrito")
            return
        
        if tipo_pago == 'EFECTIVO':
            self.procesar_venta()
        elif tipo_pago == 'TRANSFERENCIA':
            messagebox.showinfo("Transferencia", "Próximamente: Integración con transferencias")
        elif tipo_pago == 'TARJETA':
            messagebox.showinfo("Tarjeta", "Próximamente: Integración con tarjetas")
        elif tipo_pago == 'CASHEA':
            self.pagar_con_cashea()
        else:
            self.procesar_venta()

    def pagar_efectivo(self):
        """Inicia el flujo de pago en efectivo."""
        if not self.venta_agent.carrito:
            messagebox.showwarning("Advertencia", "No hay productos en el carrito")
            return
        
        # Obtener totales fiscales con la nueva estructura
        totales_usd = self.venta_agent.calcular_totales_con_impuestos()
        tasa = self.venta_agent.tasa_cambio
        
        # Calcular montos totales en Bs. y USD (con IVA incluido)
        total_bs = totales_usd['total_con_iva'] * tasa  # ← ESTE ES EL CORRECTO (2088)
        total_usd = totales_usd['total_con_iva']        # ← 5.22
        
        # Obtener configuración de la empresa
        config_empresa = self.venta_agent.obtener_configuracion_empresa(1)
        
        # Mostrar diálogo de pago en efectivo
        from ui.dialogos.pago_efectivo import PagoEfectivoDialog
        dialog = PagoEfectivoDialog(
            self.root,
            total_bs=total_bs,              # ← AHORA PASA 2088
            total_usd=total_usd,            # ← 5.22
            tasa_cambio=tasa,
            config_empresa=config_empresa,
            totales_fiscales=totales_usd
        )
        resultado = dialog.show()
        
        if resultado:
            logger.info(f"💰 Pago en efectivo procesado: {resultado}")
            
            # Preparar información de pago con todos los datos
            pago_info = {
                'moneda': resultado['moneda'],
                'monto_recibido': resultado['monto_recibido'],
                'vuelto': resultado['vuelto'],
                'totales_fiscales': totales_usd
            }
            
            # Agregar información adicional según la moneda
            if 'vuelto_usd' in resultado:
                pago_info['vuelto_usd'] = resultado['vuelto_usd']
                logger.info(f"   Vuelto en Bs.: {resultado['vuelto']:.2f} (${resultado['vuelto_usd']:.2f})")
            elif 'vuelto_bs' in resultado:
                pago_info['vuelto_bs'] = resultado['vuelto_bs']
                logger.info(f"   Vuelto en USD: ${resultado['vuelto']:.2f} (Bs.{resultado['vuelto_bs']:.2f})")
            
            # Determinar tipo de pago según moneda
            tipo_pago = 'EFECTIVO_BS' if resultado['moneda'] == 'BS' else 'EFECTIVO_USD'
            
            # Procesar la venta
            self.procesar_venta(tipo_pago=tipo_pago, pago_info=pago_info)

    def pagar_tarjeta(self):
        """Inicia el flujo de pago con tarjeta (soporta IGTF y comisiones)."""
        if not self.venta_agent.carrito:
            messagebox.showwarning("Advertencia", "No hay productos en el carrito")
            return
        
        # Obtener totales fiscales
        totales_usd = self.venta_agent.calcular_totales_con_impuestos()
        tasa = self.venta_agent.tasa_cambio
        
        # Obtener configuración de pagos (IGTF, comisiones)
        config_pagos = self.venta_agent.obtener_configuracion_pagos(1)
        
        # Combinar con la configuración general de la empresa
        config_empresa = self.venta_agent.obtener_configuracion_empresa(1)
        config_empresa.update(config_pagos)  # Añadir config de pagos
        
        print(f"🔧 Config completa para diálogo: {config_empresa}")  # DEBUG
        
        # Mostrar diálogo de pago con tarjeta
        from ui.dialogos.pago_tarjeta import PagoTarjetaDialog
        dialog = PagoTarjetaDialog(
            self.root,
            total_usd=totales_usd['total_con_iva'],
            total_bs=totales_usd['total_con_iva'] * tasa,
            tasa_cambio=tasa,
            config_empresa=config_empresa,
            totales_fiscales=totales_usd
        )
        resultado = dialog.show()
        
        if resultado:
            logger.info(f"💳 Pago con tarjeta procesado: {resultado}")
            
            # Determinar tipo de pago según moneda
            if resultado['moneda'] == 'USD':
                tipo_pago = 'TARJETA_USD'
            else:
                tipo_pago = 'TARJETA_BS'
            
            # Preparar información de pago
            pago_info = {
                'moneda': resultado['moneda'],
                'monto_recibido': resultado['monto_total'],
                'igtf_aplicado': resultado.get('igtf_aplicado', False),
                'igtf_monto': resultado.get('igtf_monto', 0),
                'igtf_porcentaje': resultado.get('igtf_porcentaje', 3.0),
                'comision_monto': resultado.get('comision_monto', 0),
                'neto': resultado.get('neto', 0),
                'referencia': resultado.get('referencia', '')
            }
            
            # Procesar la venta
            self.procesar_venta(tipo_pago=tipo_pago, pago_info=pago_info)

    def pagar_con_cashea(self):
        """Inicia el flujo de pago con Cashea"""
        if not self.venta_agent.carrito:
            messagebox.showwarning("Advertencia", "No hay productos en el carrito")
            return
        
        totales = self.venta_agent.calcular_totales()
        
        # Solicitar autorización a Cashea
        if hasattr(self.venta_agent, 'cashea_agent'):
            resultado = self.venta_agent.cashea_agent.solicitar_autorizacion(
                totales['total_usd']
            )
            
            if resultado['success']:
                # Mostrar información al cajero
                mensaje = (
                    f"✅ Venta APROBADA por Cashea\n\n"
                    f"Total: ${resultado['monto_total']:.2f}\n"
                    f"Inicial a pagar hoy: ${resultado['inicial']:.2f}\n"
                    f"Resto: ${resultado['resto']:.2f} en {resultado['cuotas']} cuotas\n\n"
                    f"Referencia: {resultado['referencia']}\n\n"
                    f"¿El cliente pagó la inicial?"
                )
                
                respuesta = messagebox.askyesno("Cashea - Aprobado", mensaje)
                
                if respuesta:
                    # Registrar venta con Cashea
                    venta_resultado = self.venta_agent.procesar_venta(
                        tipo_pago='CASHEA',
                        datos_cashea=resultado
                    )
                    
                    if venta_resultado['success']:
                        messagebox.showinfo(
                            "Cashea - Éxito", 
                            f"Venta #{venta_resultado['idventa']} registrada con Cashea\n\n"
                            f"Referencia: {resultado['referencia']}\n"
                            f"Inicial: ${resultado['inicial']:.2f}\n"
                            f"Cashea te pagará el resto (${resultado['resto']:.2f}) en 14 días"
                        )
                        self.actualizar_carrito()
                        self.actualizar_historial()
                    else:
                        messagebox.showerror(
                            "Error", 
                            f"No se pudo registrar la venta:\n{venta_resultado.get('error', 'Error desconocido')}"
                        )
            else:
                messagebox.showerror(
                    "Cashea - Rechazado",
                    f"No se pudo procesar el pago con Cashea:\n{resultado.get('error', 'Error desconocido')}"
                )
    
    def simular_notificacion_cashea(self):
        """Método TEMPORAL para simular una notificación de Cashea"""
        if hasattr(self.venta_agent, 'cashea_agent'):
            # Simular datos de una venta aprobada
            datos = {
                'referencia': f"CASHEA-{datetime.now().strftime('%y%m%d%H%M%S')}",
                'monto_total': 77.70,
                'inicial': 31.08,
                'cuotas': 3,
                'cliente': 'Cliente VIP'
            }
            self.venta_agent.cashea_agent.recibir_notificacion(datos)
            self.actualizar_notificaciones()
            messagebox.showinfo("Simulación", "Notificación de Cashea recibida (simulada)")    
    
    def pago_mixto(self):
        """Inicia el proceso de pago mixto combinando múltiples métodos"""
        if not hasattr(self, 'venta_agent') or not self.venta_agent.carrito:
            messagebox.showwarning("Advertencia", "No hay productos en el carrito")
            return
        
        # Obtener totales
        totales_fiscales = self.venta_agent.calcular_totales_con_impuestos()
        total_usd = totales_fiscales['total_con_iva']
        total_bs = total_usd * self.venta_agent.tasa_cambio
        
        # Obtener configuración
        config_empresa = self.venta_agent.obtener_configuracion_empresa(1)
        
        from ui.dialogos.pago_mixto_dialog import PagoMixtoDialog
        
        dialog = PagoMixtoDialog(
            self.root,
            total_usd=total_usd,
            total_bs=total_bs,
            tasa_cambio=self.venta_agent.tasa_cambio,
            config_empresa=config_empresa,
            totales_fiscales=totales_fiscales,
            venta_agent=self.venta_agent
        )
        
        resultado = dialog.show()
        
        if resultado:
            # Usar el método de venta mixta
            exito = self.venta_agent.procesar_venta_mixta(resultado['pagos'])
            
            if exito and exito.get('success'):
                messagebox.showinfo("Éxito", 
                    f"✅ Venta mixta procesada\n"
                    f"ID: {exito.get('idventa')}\n"
                    f"Total: ${resultado['total_usd']:.2f}\n"
                    f"Métodos: {len(resultado['pagos'])}")
                
                # Limpiar carrito y actualizar vista
                self.venta_agent.carrito = []
                self.actualizar_carrito()
                self.actualizar_opciones_pago()
            else:
                error_msg = exito.get('error', 'Error desconocido') if exito else 'Error procesando venta'
                messagebox.showerror("Error", f"No se pudo procesar la venta:\n{error_msg}") 
    
    def actualizar_notificaciones(self):
        """Revisa si hay notificaciones nuevas consultando la API webhook"""
        import requests
        
        try:
            # Consultar API webhook
            response = requests.get("http://localhost:8000/notificaciones/pendientes", timeout=1)
            if response.status_code == 200:
                data = response.json()
                pendientes = data.get('notificaciones', [])
                cantidad = len(pendientes)
                
                # Guardar en el agente local (para compatibilidad)
                if hasattr(self.venta_agent, 'cashea_agent'):
                    # Simular que el agente local tiene estas notificaciones
                    for n in pendientes:
                        if hasattr(self.venta_agent.cashea_agent, 'notificaciones_pendientes'):
                            # Evitar duplicados
                            existe = False
                            for existente in self.venta_agent.cashea_agent.notificaciones_pendientes:
                                if existente.get('referencia') == n.get('referencia'):
                                    existe = True
                                    break
                            if not existe:
                                self.venta_agent.cashea_agent.notificaciones_pendientes.append(n)
            else:
                pendientes = []
                cantidad = 0
        except:
            # Si no hay servidor webhook, usar el agente local
            if hasattr(self.venta_agent, 'cashea_agent'):
                pendientes = self.venta_agent.cashea_agent.obtener_notificaciones_pendientes()
                cantidad = len(pendientes)
            else:
                pendientes = []
                cantidad = 0
        
        # Actualizar interfaz
        if cantidad > 0:
            self.btn_notificaciones.config(text=f"🔔 ({cantidad})", fg='yellow')
            self.lbl_notif_count.config(text=str(cantidad))
        else:
            self.btn_notificaciones.config(text="🔔", fg='white')
            self.lbl_notif_count.config(text="")
        
        # Revisar cada 30 segundos
        self.root.after(30000, self.actualizar_notificaciones)   
    
    def mostrar_notificaciones(self):
        """Muestra una ventana con las notificaciones pendientes"""
        if not hasattr(self.venta_agent, 'cashea_agent'):
            messagebox.showinfo("Notificaciones", "No hay sistema de notificaciones activo")
            return
        
        pendientes = self.venta_agent.cashea_agent.obtener_notificaciones_pendientes()
        
        if not pendientes:
            messagebox.showinfo("Notificaciones", "No hay notificaciones pendientes")
            return
        
        # Crear ventana emergente
        notif_window = tk.Toplevel(self.root)
        notif_window.title("Notificaciones Cashea")
        notif_window.geometry("500x400")
        
        # Listbox con scrollbar
        frame = tk.Frame(notif_window)
        frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side='right', fill='y')
        
        listbox = tk.Listbox(frame, yscrollcommand=scrollbar.set)
        scrollbar.config(command=listbox.yview)
        
        for n in pendientes:
            texto = f"[{n['fecha']}] {n['cliente']} - ${n['monto_total']} (Inicial: ${n['inicial']})"
            listbox.insert(tk.END, texto)
        
        listbox.pack(side='left', fill='both', expand=True)
        
        # Botón para procesar seleccionada
        def procesar_seleccionada():
            seleccion = listbox.curselection()
            if seleccion:
                idx = seleccion[0]
                notif = pendientes[idx]
                
                respuesta = messagebox.askyesno(
                    "Procesar venta",
                    f"Cliente: {notif['cliente']}\n"
                    f"Total: ${notif['monto_total']}\n"
                    f"Inicial a cobrar: ${notif['inicial']}\n"
                    f"Cuotas: {notif['cuotas']}\n\n"
                    f"¿Cobrar inicial y completar venta?"
                )
                
                if respuesta:
                    self.venta_agent.cashea_agent.marcar_como_leida(notif['referencia'])
                    messagebox.showinfo("Éxito", "Venta procesada correctamente")
                    notif_window.destroy()
                    self.actualizar_notificaciones()
        
        btn_frame = tk.Frame(notif_window)
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="Procesar seleccionada", 
                 command=procesar_seleccionada,
                 bg='#27ae60', fg='white').pack(side='left', padx=5)
        
        tk.Button(btn_frame, text="Cerrar", 
                 command=notif_window.destroy).pack(side='left', padx=5)    
    
    def actualizar_historial(self):
        ventas = self.venta_agent.obtener_historial(20)
        
        for item in self.tree_historial.get_children():
            self.tree_historial.delete(item)
        
        for venta in ventas:
            self.tree_historial.insert('', 'end', values=(
                venta['idventa'],
                venta['fecha'].strftime('%d/%m/%Y') if venta['fecha'] else '',
                venta['cliente'][:20],
                f"${venta['monto_usd']:.2f}"
            ))
    
    def actualizar_tasas(self):
        self.lbl_tasa.config(text=f"💵 Tasa USD: Bs. {self.venta_agent.tasa_cambio:.2f}")
        self.root.after(60000, self.actualizar_tasas)
    
    def run(self):
        self.root.mainloop()
    
    # --- MÉTODOS PARA EL PANEL DE PROGRAMADOR (COMANDOS OCULTOS) ---
    def setup_programador_shortcut(self):
        """Configura el atajo de teclado para el panel de programador."""
        self.root.bind('<Control-Shift-P>', self.abrir_panel_programador)
        logger.debug("🔧 Atajo Ctrl+Shift+P configurado para panel de programador.")

    def abrir_panel_programador(self, event=None):
        """Abre el panel de acceso para programador."""
        from tkinter import simpledialog, messagebox
        
        password = simpledialog.askstring("Acceso Restringido", 
                                          "Ingrese la clave de programador:", 
                                          show='*',
                                          parent=self.root)
        if password is None:
            return
        if password == "CASHEA_MASTER_2026":  # Cambia esto por tu clave secreta
            self._mostrar_consola_programador()
        else:
            messagebox.showerror("Error", "Clave incorrecta. Acceso denegado.")

    def _mostrar_consola_programador(self):
        """Ventana de consola para ejecutar comandos de programador."""
        import tkinter as tk
        from tkinter import ttk
        from agente_escritorio.agents.programador_agent import ProgramadorAgent

        try:
            self.programador_agent = ProgramadorAgent(usuario_actual=self.usuario_actual, parent=self)
        except PermissionError as e:
            messagebox.showerror("Acceso Denegado", str(e))
            return
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo inicializar el agente: {e}")
            return

        top = tk.Toplevel(self.root)
        top.title("⚙️ Consola de Programador")
        top.geometry("700x500")
        top.transient(self.root)
        top.grab_set()

        # Área de comandos
        ttk.Label(top, text="Comando:", font=('Helvetica', 10, 'bold')).pack(anchor='w', padx=10, pady=(10,0))
        entry_comando = ttk.Entry(top, width=80, font=('Courier', 10))
        entry_comando.pack(padx=10, pady=5, fill='x')
        entry_comando.focus()

        # Botón ejecutar
        btn_frame = ttk.Frame(top)
        btn_frame.pack(pady=5)

        def ejecutar():
            comando = entry_comando.get()
            if not comando:
                return
            resultado = self.programador_agent.ejecutar_comando(comando)
            texto_resultado.insert(tk.END, f"> {comando}\n{resultado}\n\n")
            entry_comando.delete(0, tk.END)
            texto_resultado.see(tk.END)

        ttk.Button(btn_frame, text="Ejecutar", command=ejecutar).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Limpiar", command=lambda: texto_resultado.delete(1.0, tk.END)).pack(side='left', padx=5)

        # Área de resultados
        ttk.Label(top, text="Resultado:", font=('Helvetica', 10, 'bold')).pack(anchor='w', padx=10, pady=(10,0))
        texto_resultado = tk.Text(top, wrap='word', font=('Courier', 10))
        scrollbar = ttk.Scrollbar(top, orient='vertical', command=texto_resultado.yview)
        texto_resultado.configure(yscrollcommand=scrollbar.set)
        
        frame_resultado = ttk.Frame(top)
        frame_resultado.pack(fill='both', expand=True, padx=10, pady=5)
        texto_resultado.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # Mostrar ayuda al inicio
        texto_resultado.insert(tk.END, "=== CONSOLA DE PROGRAMADOR ===\n")
        texto_resultado.insert(tk.END, "Comandos disponibles:\n")
        texto_resultado.insert(tk.END, self.programador_agent._ayuda())
        texto_resultado.insert(tk.END, "\n---\n\n")

        entry_comando.bind('<Return>', lambda e: ejecutar())
        top.bind('<Escape>', lambda e: top.destroy())    
    
    def __del__(self):
        try:
            self.venta_agent.cerrar()
        except:
            pass
