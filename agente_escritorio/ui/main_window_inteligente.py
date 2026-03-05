"""
Ventana principal con búsqueda inteligente - VERSIÓN CORREGIDA
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
        
        self.usuario = Usuario()
        print("✅ Usuario creado")
        
        # Inicializar agentes
        print("📦 Inicializando agentes...")
        self.venta_agent = VentaAgent(self.usuario)
        self.cliente_agent = ClienteAgent()
        self.articulo_agent = ArticuloAgent()
        print("✅ Agentes inicializados")
        
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
        
        # Carrito
        carrito_frame = tk.LabelFrame(left_frame, text=" Carrito de Compras ", font=('Helvetica', 10, 'bold'), bg='white')
        carrito_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        columns = ('Cant', 'Producto', 'Precio $', 'Subtotal $')
        self.tree_carrito = ttk.Treeview(carrito_frame, columns=columns, show='headings', height=8)
        
        self.tree_carrito.heading('Cant', text='Cant')
        self.tree_carrito.heading('Producto', text='Producto')
        self.tree_carrito.heading('Precio $', text='Precio $')
        self.tree_carrito.heading('Subtotal $', text='Subtotal $')
        
        self.tree_carrito.column('Cant', width=60)
        self.tree_carrito.column('Producto', width=350)
        self.tree_carrito.column('Precio $', width=80)
        self.tree_carrito.column('Subtotal $', width=100)
        
        scrollbar = ttk.Scrollbar(carrito_frame, orient='vertical', command=self.tree_carrito.yview)
        self.tree_carrito.configure(yscrollcommand=scrollbar.set)
        
        self.tree_carrito.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        self.tree_carrito.bind('<Double-1>', self.quitar_producto)
        
        # Totales
        totales_frame = tk.Frame(left_frame, bg='white', relief='ridge', bd=2)
        totales_frame.pack(fill='x', padx=10, pady=10)
        
        totales_inner = tk.Frame(totales_frame, bg='white')
        totales_inner.pack(anchor='e', padx=20, pady=10)
        
        self.lbl_subtotal = tk.Label(totales_inner, text="Subtotal: $0.00",
                                    bg='white', font=('Helvetica', 10))
        self.lbl_subtotal.pack(anchor='e')
        
        self.lbl_iva = tk.Label(totales_inner, text="IVA: $0.00",
                               bg='white', font=('Helvetica', 10))
        self.lbl_iva.pack(anchor='e')
        
        self.lbl_total_usd = tk.Label(totales_inner, text="TOTAL USD: $0.00",
                                     bg='white', font=('Helvetica', 14, 'bold'))
        self.lbl_total_usd.pack(anchor='e', pady=5)
        
        self.lbl_total_bs = tk.Label(totales_inner, text="TOTAL Bs: Bs.0.00",
                                    bg='white', font=('Helvetica', 12))
        self.lbl_total_bs.pack(anchor='e')
        
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
        print("🔄 Actualizando vista del carrito...")
        for item in self.tree_carrito.get_children():
            self.tree_carrito.delete(item)
        
        for item in self.venta_agent.carrito:
            self.tree_carrito.insert('', 'end', values=(
                item['cantidad'],
                item['nombre'],
                f"${item['precio_unitario']:.2f}",
                f"${item['subtotal']:.2f}"
            ))
        
        totales = self.venta_agent.calcular_totales()
        self.lbl_subtotal.config(text=f"Subtotal: ${totales['subtotal_usd']:.2f}")
        self.lbl_iva.config(text=f"IVA: ${totales['iva_usd']:.2f}")
        self.lbl_total_usd.config(text=f"TOTAL USD: ${totales['total_usd']:.2f}")
        self.lbl_total_bs.config(text=f"TOTAL Bs: Bs.{totales['total_bs']:.2f}")
        print(f"💰 Totales actualizados: ${totales['total_usd']:.2f}")
    
    def procesar_venta(self):
        if not self.venta_agent.carrito:
            messagebox.showwarning("Advertencia", "No hay productos en el carrito")
            return
        
        totales = self.venta_agent.calcular_totales()
        
        respuesta = messagebox.askyesno(
            "Confirmar Venta",
            f"Total: ${totales['total_usd']:.2f} (Bs. {totales['total_bs']:.2f})\n"
            f"¿Procesar venta?"
        )
        
        if respuesta:
            print("\n💰 Procesando venta...")
            resultado = self.venta_agent.procesar_venta()
            
            if resultado['success']:
                print(f"✅ Venta #{resultado['idventa']} procesada")
                messagebox.showinfo("Éxito", f"Venta #{resultado['idventa']} procesada")
                self.actualizar_carrito()
                self.actualizar_historial()
            else:
                print(f"❌ Error: {resultado.get('error')}")
                messagebox.showerror("Error", resultado.get('error'))
    
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
    
    def __del__(self):
        try:
            self.venta_agent.cerrar()
        except:
            pass
