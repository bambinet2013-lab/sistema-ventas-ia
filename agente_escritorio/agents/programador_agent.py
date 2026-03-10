"""
Agente con permisos de superusuario para control remoto del sistema.
Solo accesible mediante comandos ocultos.
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from loguru import logger
import pyodbc
from datetime import datetime

class ProgramadorAgent:
    """Agente con control total del sistema. Acceso restringido."""

    def __init__(self, usuario_actual, parent=None):
        """
        Args:
            usuario_actual: Objeto usuario que intenta ejecutar comandos.
            parent: Ventana padre para mostrar diálogos.
        """
        if not self._es_programador(usuario_actual):
            logger.warning(f"⚠️ Intento de acceso no autorizado por {usuario_actual.nombre}")
            raise PermissionError("Acceso denegado. No tienes permisos de programador.")
        
        self.usuario = usuario_actual
        self.parent = parent  # ← NUEVO: Guardar referencia a la ventana padre
        self.conn = self._get_connection()
        logger.info(f"✅ ProgramadorAgent inicializado para {usuario_actual.nombre}")

    def _get_connection(self):
        """Establece conexión con la base de datos."""
        conn_str = (
            "DRIVER={ODBC Driver 18 for SQL Server};"
            "SERVER=localhost,1433;"
            "DATABASE=SistemaVentas;"
            "UID=sa;"
            "PWD=Santi07.;"
            "TrustServerCertificate=yes;"
        )
        return pyodbc.connect(conn_str)

    def _es_programador(self, usuario):
        """
        Verifica si el usuario tiene permisos de programador.
        Por ahora, asumimos que el usuario 'Admin' es el programador.
        """
        return usuario.nombre == "Admin" or usuario.rol == "Administrador"

    def ejecutar_comando(self, comando):
        """
        Procesa y ejecuta un comando de texto.

        Args:
            comando: String con el comando (ej: '/modo 123 normal')

        Returns:
            String con el resultado del comando.
        """
        if not comando or not comando.startswith('/'):
            return "❌ Los comandos deben empezar con '/'"
        
        partes = comando.strip().split()
        cmd = partes[0].lower()

        if cmd == '/modo':
            return self._cambiar_modo(partes)
        elif cmd == '/config':
            if len(partes) < 2:
                return "❌ Uso: /config [efectivo_usd|comision|igtf] ..."
            
            subcmd = partes[1].lower()
            if subcmd == 'efectivo_usd':
                return self._config_efectivo_usd(partes)
            elif subcmd == 'comision':
                return self._config_comision(partes)
            elif subcmd == 'igtf':
                return self._config_igtf(partes)
            else:
                return f"❌ Configuración '{subcmd}' no reconocida"
        elif cmd == '/status':
            return self._ver_estado(partes)
        elif cmd == '/ayuda':
            return self._ayuda()
        # ===== NUEVOS COMANDOS (AGREGADOS AQUÍ - ANTES DEL ELSE) =====
        elif cmd == '/cuentas':
            return self._config_cuentas(partes)
        elif cmd == '/ver_cuentas':
            return self._ver_cuentas(partes)
        else:
            return f"❌ Comando '{cmd}' no reconocido. Usa /ayuda para ver los disponibles."  

    def _cambiar_modo(self, partes):
        """Cambia el modo de operación de un cliente en la BD real"""
        if len(partes) < 3:
            return "❌ Uso: /modo [id_empresa] [normal|pos_solo|hibrido]"
        
        try:
            id_empresa = int(partes[1])
            modo = partes[2].lower()
            
            if modo not in ['normal', 'pos_solo', 'hibrido']:
                return f"❌ Modo '{modo}' inválido. Usa: normal, pos_solo, hibrido"
            
            cursor = self.conn.cursor()
            
            # Verificar si la empresa existe
            cursor.execute("SELECT COUNT(*) FROM configuracion_operacion WHERE id_empresa = ?", (id_empresa,))
            if cursor.fetchone()[0] == 0:
                # Crear registro si no existe
                cursor.execute("""
                    INSERT INTO configuracion_operacion (id_empresa, modo_operacion, pos_activo)
                    VALUES (?, ?, 0)
                """, (id_empresa, modo))
            else:
                # Actualizar modo existente
                cursor.execute("""
                    UPDATE configuracion_operacion 
                    SET modo_operacion = ?, fecha_actualizacion = GETDATE()
                    WHERE id_empresa = ?
                """, (modo, id_empresa))
            
            self.conn.commit()
            logger.info(f"🔧 Modo de empresa {id_empresa} cambiado a '{modo}' en BD")
            
            return f"✅ Modo de empresa {id_empresa} cambiado a '{modo}'"
            
        except ValueError:
            return "❌ El ID de empresa debe ser un número."
        except Exception as e:
            logger.error(f"Error en /modo: {e}")
            return f"❌ Error interno: {e}"

    def _config_efectivo_usd(self, partes):
        """Activa/desactiva la opción de pago en efectivo USD."""
        if len(partes) < 3:
            return "❌ Uso: /config efectivo_usd [on|off] [id_empresa]"
        
        try:
            estado = partes[2].lower()
            id_empresa = int(partes[3])
            
            if estado not in ['on', 'off']:
                return "❌ Estado debe ser 'on' o 'off'"
            
            nuevo_valor = 1 if estado == 'on' else 0
            
            cursor = self.conn.cursor()
            cursor.execute("""
                UPDATE configuracion_operacion 
                SET efectivo_usd_activo = ?, fecha_actualizacion = GETDATE()
                WHERE id_empresa = ?
            """, (nuevo_valor, id_empresa))
            self.conn.commit()
            
            return f"✅ Efectivo USD para empresa {id_empresa} cambiado a '{estado}'"
            
        except ValueError:
            return "❌ El ID de empresa debe ser un número."
        except Exception as e:
            return f"❌ Error: {e}"

    def _config_comision(self, partes):
        """Configura comisiones con activación/desactivación para diferentes tipos."""
        if len(partes) < 4:
            return ("❌ Uso: /config comision [bs|usd|internacional] [on|off|porcentaje] [id_empresa]\n"
                    "Ejemplos:\n"
                    "  /config comision bs on 1\n"
                    "  /config comision bs off 1\n"
                    "  /config comision bs 2.5 1\n"
                    "  /config comision usd on 1\n"
                    "  /config comision internacional 1.5 1")
        
        try:
            tipo = partes[2].lower()  # bs, usd, internacional
            accion = partes[3].lower()
            id_empresa = int(partes[4])
            
            cursor = self.conn.cursor()
            
            # Mapear tipos a campos de la BD
            if tipo == 'bs':
                campo_activo = 'comision_bs_activo'
                campo_porcentaje = 'comision_bs_porcentaje'
                nombre_tipo = "Bolívares"
            elif tipo == 'usd':
                campo_activo = 'comision_usd_activo'
                campo_porcentaje = 'comision_usd_porcentaje'
                nombre_tipo = "Dólares"
            elif tipo == 'internacional':
                campo_activo = 'comision_internacional_activo'
                campo_porcentaje = 'comision_internacional_porcentaje'
                nombre_tipo = "Internacional"
            else:
                return "❌ Tipo inválido. Use: bs, usd, internacional"
            
            # Verificar si la acción es activar/desactivar o porcentaje
            if accion in ['on', 'off']:
                nuevo_valor = 1 if accion == 'on' else 0
                cursor.execute(f"""
                    UPDATE configuracion_operacion 
                    SET {campo_activo} = ?, fecha_actualizacion = GETDATE()
                    WHERE id_empresa = ?
                """, (nuevo_valor, id_empresa))
                self.conn.commit()
                return f"✅ Comisión {nombre_tipo} {'activada' if nuevo_valor else 'desactivada'} para empresa {id_empresa}"
            
            else:
                # Es un porcentaje
                try:
                    porcentaje = float(accion)
                    if porcentaje < 0 or porcentaje > 20:
                        return "❌ La comisión debe estar entre 0% y 20%"
                    
                    cursor.execute(f"""
                        UPDATE configuracion_operacion 
                        SET {campo_porcentaje} = ?, fecha_actualizacion = GETDATE()
                        WHERE id_empresa = ?
                    """, (porcentaje, id_empresa))
                    self.conn.commit()
                    return f"✅ Comisión {nombre_tipo} para empresa {id_empresa} establecida en {porcentaje}%"
                    
                except ValueError:
                    return "❌ El porcentaje debe ser un número"
                    
        except ValueError:
            return "❌ ID de empresa inválido"
        except Exception as e:
            return f"❌ Error: {e}"

    def _config_igtf(self, partes):
        """Configura los parámetros del IGTF."""
        if len(partes) < 4:
            return ("❌ Uso: /config igtf [activo|porcentaje|efectivo|tarjeta|transferencia] [valor] [id_empresa]\n"
                    "Ejemplos:\n"
                    "  /config igtf activo on 1\n"
                    "  /config igtf porcentaje 3.5 1\n"
                    "  /config igtf efectivo on 1\n"
                    "  /config igtf tarjeta off 1")
        
        try:
            subcomando = partes[2].lower()
            valor = partes[3].lower()
            id_empresa = int(partes[4])
            
            cursor = self.conn.cursor()
            
            if subcomando == 'activo':
                nuevo_valor = 1 if valor == 'on' else 0
                cursor.execute("UPDATE configuracion_operacion SET igtf_activo = ? WHERE id_empresa = ?", 
                             (nuevo_valor, id_empresa))
                self.conn.commit()
                return f"✅ IGTF {'activado' if nuevo_valor else 'desactivado'} para empresa {id_empresa}"
                
            elif subcomando == 'porcentaje':
                porcentaje = float(valor)
                cursor.execute("UPDATE configuracion_operacion SET igtf_porcentaje = ? WHERE id_empresa = ?", 
                             (porcentaje, id_empresa))
                self.conn.commit()
                return f"✅ Porcentaje IGTF para empresa {id_empresa} establecido en {porcentaje}%"
                
            elif subcomando in ['efectivo', 'tarjeta', 'transferencia']:
                campo = f"igtf_aplica_{subcomando}_usd"
                nuevo_valor = 1 if valor == 'on' else 0
                cursor.execute(f"UPDATE configuracion_operacion SET {campo} = ? WHERE id_empresa = ?", 
                             (nuevo_valor, id_empresa))
                self.conn.commit()
                return f"✅ IGTF para {subcomando} USD {'activado' if nuevo_valor else 'desactivado'} en empresa {id_empresa}"
            else:
                return "❌ Subcomando no reconocido"
                
        except ValueError:
            return "❌ ID de empresa o valor inválido"
        except Exception as e:
            return f"❌ Error: {e}"

    def _obtener_info_cuentas(self, id_empresa):
        """Obtiene información de cuentas bancarias para mostrar en status"""
        try:
            from models.cuenta_empresa import CuentaEmpresaRepo
            
            repo = CuentaEmpresaRepo(self.conn)
            cuentas = repo.listar_cuentas(solo_programador=True)
            
            if not cuentas:
                return ""
            
            texto = "\n   **CUENTAS BANCARIAS:**\n"
            for c in cuentas:
                visibilidad = "🔒" if c.solo_programador else "👁️"
                texto += f"   {visibilidad} {c.nombre_banco}: {c.numero_cuenta}"
                if c.moneda == 'USD':
                    texto += " (USD)"
                if c.telefono_asociado:
                    texto += f" 📱{c.telefono_asociado}"
                texto += "\n"
            return texto
        except Exception as e:
            logger.error(f"Error obteniendo cuentas para status: {e}")
            return ""

    def _ver_estado(self, partes):
        """Muestra el estado del sistema o de un cliente específico."""
        print(f"🔍 DEBUG - _ver_estado llamado con partes: {partes}")
        logger.info(f"🔍 _ver_estado llamado con partes: {partes}")
        
        if len(partes) == 1:
            # Mostrar resumen general
            try:
                cursor = self.conn.cursor()
                
                cursor.execute("SELECT COUNT(*) FROM configuracion_medios_pago")
                total_medios = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM cliente")
                total_clientes = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM articulo")
                total_articulos = cursor.fetchone()[0]
                
                cursor.execute("SELECT TOP 1 idventa, monto_divisa, tipo_pago, fecha FROM venta ORDER BY idventa DESC")
                ultima = cursor.fetchone()
                ultima_text = f"#{ultima[0]} - ${ultima[1]} ({ultima[2]})" if ultima else "Ninguna"
                
                return (f"📊 **ESTADO GENERAL DEL SISTEMA**\n"
                        f"   - Medios de pago configurados: {total_medios}\n"
                        f"   - Clientes registrados: {total_clientes}\n"
                        f"   - Artículos en catálogo: {total_articulos}\n"
                        f"   - Última venta: {ultima_text}")
            except Exception as e:
                return f"❌ Error obteniendo estado general: {e}"
        
        elif len(partes) == 2:
            try:
                id_empresa = int(partes[1])
                print(f"🔍 DEBUG - Consultando empresa {id_empresa}")
                cursor = self.conn.cursor()
                
                cursor.execute("""
                    SELECT 
                        modo_operacion, pos_activo, efectivo_usd_activo, 
                        redondeo_vuelto, monto_minimo_usd, fecha_actualizacion,
                        comision_bs_activo, comision_bs_porcentaje,
                        comision_usd_activo, comision_usd_porcentaje,
                        comision_internacional_activo, comision_internacional_porcentaje,
                        igtf_activo, igtf_porcentaje,
                        igtf_aplica_efectivo_usd, igtf_aplica_tarjeta_usd,
                        igtf_aplica_transferencia_usd
                    FROM configuracion_operacion 
                    WHERE id_empresa = ?
                """, (id_empresa,))
                
                config = cursor.fetchone()
                print(f"🔍 DEBUG - config obtenido: {config}")
                
                if config:
                    modo, pos_activo, usd_activo, redondeo, min_usd, fecha = config[:6]
                    comision_bs_activo, comision_bs_pct = config[6], config[7]
                    comision_usd_activo, comision_usd_pct = config[8], config[9]
                    comision_int_activo, comision_int_pct = config[10], config[11]
                    igtf_activo, igtf_porcentaje = config[12], config[13]
                    igtf_efectivo, igtf_tarjeta, igtf_transf = config[14], config[15], config[16]
                    
                    # Manejar valores None
                    igtf_porcentaje_val = igtf_porcentaje if igtf_porcentaje is not None else 3.0
                    
                    redondeo_val = redondeo if redondeo is not None else 0
                    min_usd_val = min_usd if min_usd is not None else 0
                    comision_bs_pct_val = comision_bs_pct if comision_bs_pct is not None else 2.5
                    comision_usd_pct_val = comision_usd_pct if comision_usd_pct is not None else 2.5
                    comision_int_pct_val = comision_int_pct if comision_int_pct is not None else 1.5
                    
                    # Construir texto de aplica IGTF
                    aplica_text = ""
                    aplica_text += "Efectivo USD " if igtf_efectivo else ""
                    aplica_text += "Tarjeta USD " if igtf_tarjeta else ""
                    aplica_text += "Transferencia USD" if igtf_transf else ""
                    if not aplica_text.strip():
                        aplica_text = "Ninguno"
                    
                    # Obtener información de cuentas
                    info_cuentas = self._obtener_info_cuentas(id_empresa)
                    
                    return (f"📊 **ESTADO DE EMPRESA {id_empresa}**\n"
                            f"   - Modo operación: {modo}\n"
                            f"   - POS activo: {'Sí' if pos_activo else 'No'}\n"
                            f"   - Efectivo USD activo: {'Sí' if usd_activo else 'No'}\n"
                            f"   - Redondeo vuelto: {redondeo_val} Bs.\n"
                            f"   - Monto mínimo USD: ${min_usd_val:.2f}\n"
                            f"\n"
                            f"   **COMISIONES TARJETA:**\n"
                            f"   - Bs.: {'✅ Activa' if comision_bs_activo else '❌ Inactiva'} ({comision_bs_pct_val}%)\n"
                            f"   - USD: {'✅ Activa' if comision_usd_activo else '❌ Inactiva'} ({comision_usd_pct_val}%)\n"
                            f"   - Internacional: {'✅ Activa' if comision_int_activo else '❌ Inactiva'} ({comision_int_pct_val}%)\n"
                            f"\n"
                            f"   **IGTF:**\n"
                            f"   - Estado: {'✅ Activo' if igtf_activo else '❌ Inactivo'} ({igtf_porcentaje_val}%)\n"
                            f"   - Aplica a: {aplica_text}\n"
                            f"{info_cuentas}"
                            f"   - Config actualizada: {fecha}")
                else:
                    return f"❌ No hay configuración para empresa {id_empresa}"
            except ValueError:
                return "❌ El ID de empresa debe ser un número."
            except Exception as e:
                return f"❌ Error obteniendo estado de empresa: {e}"
        else:
            return "❌ Uso: /status [id_empresa]"

    def _config_cuentas(self, partes):
        """Abre el diálogo de configuración de cuentas bancarias"""
        try:
            # Importar aquí para evitar dependencias circulares
            from ui.dialogos.config_cuentas_dialog import ConfigCuentasDialog
            from models.cuenta_empresa import CuentaEmpresaRepo
            
            if not self.parent:
                return "❌ Error: No hay ventana padre para mostrar el diálogo"
            
            repo = CuentaEmpresaRepo(self.conn)
            dialog = ConfigCuentasDialog(self.parent, repo)
            dialog.show()
            return "✅ Configuración de cuentas finalizada"
        except ImportError as e:
            logger.error(f"Error importando: {e}")
            return f"❌ Error importando módulos: {e}"
        except Exception as e:
            logger.error(f"Error en _config_cuentas: {e}")
            return f"❌ Error: {e}"
    
    def _ver_cuentas(self, partes):
        """Muestra las cuentas configuradas"""
        try:
            from models.cuenta_empresa import CuentaEmpresaRepo
            
            repo = CuentaEmpresaRepo(self.conn)
            cuentas = repo.listar_cuentas(solo_programador=True)
            
            if not cuentas:
                return "📭 No hay cuentas configuradas"
            
            resultado = "🏦 **CUENTAS DE LA EMPRESA**\n\n"
            for c in cuentas:
                visibilidad = "🔒 Programador" if c.solo_programador else "👁️ Todos"
                resultado += f"{visibilidad} **{c.nombre_banco}**\n"
                resultado += f"   📋 N°: {c.numero_cuenta}\n"
                resultado += f"   📁 Tipo: {c.tipo_cuenta} ({c.moneda})\n"
                if c.telefono_asociado:
                    resultado += f"   📱 Pago Móvil: {c.telefono_asociado}\n"
                resultado += "\n"
            
            return resultado
        except ImportError:
            return "❌ No se pudo importar el modelo de cuentas"
        except Exception as e:
            logger.error(f"Error en _ver_cuentas: {e}")
            return f"❌ Error: {e}"

    def _ayuda(self):
        """Muestra la ayuda de comandos disponibles."""
        return """
📚 **COMANDOS DISPONIBLES**

`/modo [id_empresa] [normal|pos_solo|hibrido]`
    Cambia el modo de operación de una empresa.

`/status [id_empresa]`
    Muestra el estado general del sistema o de una empresa específica.
    
`/cuentas`
    Abrir configuración de cuentas bancarias.

`/ver_cuentas`
    Listar cuentas configuradas.

`/ayuda`
    Muestra esta ayuda.

`/salir`
    Cierra la consola de programador (desde la UI).
        """

    def cerrar(self):
        """Cierra la conexión a la base de datos."""
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()
            logger.info("🔒 Conexión de ProgramadorAgent cerrada.")
