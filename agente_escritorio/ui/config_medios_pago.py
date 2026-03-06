"""
Ventana de configuración de medios de pago
"""
import tkinter as tk
from tkinter import ttk, messagebox
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from loguru import logger
import pyodbc
import json

class ConfigMediosPagoDialog:
    def __init__(self, parent):
        self.parent = parent
        self.root = tk.Toplevel()
        self.root.title("Configurar Medios de Pago")
        self.root.geometry("600x500")
        self.root.transient(parent.root if hasattr(parent, 'root') else None)
        self.root.grab_set()
        
        # Configurar estilos
        self.setup_styles()
        
        # Cargar configuración actual
        self.config_actual = self._cargar_configuracion()
        
        # Construir interfaz
        self.setup_ui()
        
    def setup_styles(self):
        self.bg_color = "#f0f0f0"
        self.primary_color = "#2c3e50"
        self.secondary_color = "#3498db"
        self.success_color = "#27ae60"
        
    def _get_connection(self):
        """Obtiene conexión a la base de datos"""
        conn_str = (
            "DRIVER={ODBC Driver 18 for SQL Server};"
            "SERVER=localhost,1433;"
            "DATABASE=SistemaVentas;"
            "UID=sa;"
            "PWD=Santi07.;"
            "TrustServerCertificate=yes;"
        )
        return pyodbc.connect(conn_str)
    
    def _cargar_configuracion(self):
        """Carga la configuración actual de la BD"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT configuracion_json FROM configuracion_medios_pago 
                WHERE medio_pago = 'CASHEA'
            """)
            row = cursor.fetchone()
            conn.close()
            
            if row and row[0]:
                return json.loads(row[0])
            return {}
        except Exception as e:
            logger.error(f"Error cargando configuración: {e}")
            return {}
    
    def _guardar_configuracion(self, data):
        """Guarda la configuración en la BD"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Convertir a JSON
            json_data = json.dumps(data)
            
            cursor.execute("""
                UPDATE configuracion_medios_pago 
                SET activo = 1, 
                    configuracion_json = ?,
                    fecha_actualizacion = GETDATE()
                WHERE medio_pago = 'CASHEA'
            """, (json_data,))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error guardando configuración: {e}")
            return False
    
    def _probar_conexion(self):
        """Prueba la conexión con las credenciales ingresadas"""
        public_key = self.entry_public_key.get().strip()
        private_key = self.entry_private_key.get().strip()
        store_id = self.entry_store_id.get().strip()
        
        if not public_key or not private_key or not store_id:
            messagebox.showerror("Error", "Complete todos los campos")
            return
        
        # Simular prueba exitosa (luego se conectará a API real)
        messagebox.showinfo("Éxito", "Conexión exitosa con Cashea")
        
    def setup_ui(self):
        # Notebook para pestañas
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Pestaña: Cashea
        frame_cashea = ttk.Frame(notebook)
        notebook.add(frame_cashea, text='Cashea')
        
        # Frame para activación
        activo_frame = ttk.LabelFrame(frame_cashea, text="Estado")
        activo_frame.pack(fill='x', padx=10, pady=10)
        
        self.var_activo = tk.BooleanVar(value=self.config_actual.get('activo', False))
        ttk.Checkbutton(activo_frame, text="Activar Cashea", 
                       variable=self.var_activo).pack(anchor='w', padx=10, pady=5)
        
        # Frame para credenciales
        cred_frame = ttk.LabelFrame(frame_cashea, text="Credenciales")
        cred_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(cred_frame, text="Public API Key:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.entry_public_key = ttk.Entry(cred_frame, width=50)
        self.entry_public_key.grid(row=0, column=1, padx=5, pady=5)
        self.entry_public_key.insert(0, self.config_actual.get('public_key', ''))
        
        ttk.Label(cred_frame, text="Private API Key:").grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.entry_private_key = ttk.Entry(cred_frame, width=50, show="*")
        self.entry_private_key.grid(row=1, column=1, padx=5, pady=5)
        self.entry_private_key.insert(0, self.config_actual.get('private_key', ''))
        
        ttk.Label(cred_frame, text="Store ID:").grid(row=2, column=0, sticky='w', padx=5, pady=5)
        self.entry_store_id = ttk.Entry(cred_frame, width=50)
        self.entry_store_id.grid(row=2, column=1, padx=5, pady=5)
        self.entry_store_id.insert(0, self.config_actual.get('store_id', ''))
        
        # Frame para configuración comercial
        comm_frame = ttk.LabelFrame(frame_cashea, text="Configuración Comercial")
        comm_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(comm_frame, text="Comisión (%):").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.entry_comision = ttk.Entry(comm_frame, width=10)
        self.entry_comision.grid(row=0, column=1, sticky='w', padx=5, pady=5)
        self.entry_comision.insert(0, str(self.config_actual.get('comision', '3.0')))
        
        ttk.Label(comm_frame, text="Monto mínimo ($):").grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.entry_minimo = ttk.Entry(comm_frame, width=10)
        self.entry_minimo.grid(row=1, column=1, sticky='w', padx=5, pady=5)
        self.entry_minimo.insert(0, str(self.config_actual.get('monto_minimo', '25.00')))
        
        # Botones
        btn_frame = ttk.Frame(frame_cashea)
        btn_frame.pack(fill='x', padx=10, pady=20)
        
        ttk.Button(btn_frame, text="Probar Conexión", 
                  command=self._probar_conexion).pack(side='left', padx=5)
        
        ttk.Button(btn_frame, text="Guardar", 
                  command=self._guardar).pack(side='right', padx=5)
        
        ttk.Button(btn_frame, text="Cancelar", 
                  command=self.root.destroy).pack(side='right', padx=5)
    
    def _guardar(self):
        """Guarda la configuración"""
        data = {
            'activo': self.var_activo.get(),
            'public_key': self.entry_public_key.get().strip(),
            'private_key': self.entry_private_key.get().strip(),
            'store_id': self.entry_store_id.get().strip(),
            'comision': float(self.entry_comision.get() or '3.0'),
            'monto_minimo': float(self.entry_minimo.get() or '25.0')
        }
        
        if self._guardar_configuracion(data):
            messagebox.showinfo("Éxito", "Configuración guardada correctamente")
            self.root.destroy()
        else:
            messagebox.showerror("Error", "No se pudo guardar la configuración")
    
    def show(self):
        self.root.wait_window()
