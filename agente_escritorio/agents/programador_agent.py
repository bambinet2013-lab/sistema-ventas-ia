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

    def __init__(self, usuario_actual):
        """
        Args:
            usuario_actual: Objeto usuario que intenta ejecutar comandos.
        """
        if not self._es_programador(usuario_actual):
            logger.warning(f"⚠️ Intento de acceso no autorizado por {usuario_actual.nombre}")
            raise PermissionError("Acceso denegado. No tienes permisos de programador.")
        
        self.usuario = usuario_actual
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
        """Configura la comisión del banco para pagos con tarjeta."""
        if len(partes) < 4:
            return "❌ Uso: /config comision [porcentaje] [id_empresa]"
        
        try:
            comision = float(partes[2])
            id_empresa = int(partes[3])
            
            if comision < 0 or comision > 20:
                return "❌ La comisión debe estar entre 0% y 20%"
            
            cursor = self.conn.cursor()
            cursor.execute("""
                UPDATE configuracion_operacion 
                SET comision_tarjeta = ?, fecha_actualizacion = GETDATE()
                WHERE id_empresa = ?
            """, (comision, id_empresa))
            self.conn.commit()
            
            return f"✅ Comisión para empresa {id_empresa} establecida en {comision}%"
            
        except ValueError:
            return "❌ El porcentaje debe ser un número"
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

    def _ver_estado(self, partes):
        """Muestra el estado del sistema o de un cliente específico."""
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
                
                # Obtener última venta
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
                cursor = self.conn.cursor()
                
                # Obtener configuración de la empresa
                cursor.execute("""
                    SELECT modo_operacion, pos_activo, efectivo_usd_activo, redondeo_vuelto, monto_minimo_usd, fecha_actualizacion 
                    FROM configuracion_operacion WHERE id_empresa = ?
                """, (id_empresa,))
                config = cursor.fetchone()
                
                if config:
                    modo, pos_activo, usd_activo, redondeo, min_usd, fecha = config
                    return (f"📊 **ESTADO DE EMPRESA {id_empresa}**\n"
                            f"   - Modo operación: {modo}\n"
                            f"   - POS activo: {'Sí' if pos_activo else 'No'}\n"
                            f"   - Efectivo USD activo: {'Sí' if usd_activo else 'No'}\n"
                            f"   - Redondeo vuelto: {redondeo} Bs.\n"
                            f"   - Monto mínimo USD: ${min_usd:.2f}\n"
                            f"   - Config actualizada: {fecha}")
                else:
                    return f"❌ No hay configuración para empresa {id_empresa}"
            except ValueError:
                return "❌ El ID de empresa debe ser un número."
        else:
            return "❌ Uso: /status [id_empresa]"

    def _ayuda(self):
        """Muestra la ayuda de comandos disponibles."""
        return ("""
📚 **COMANDOS DISPONIBLES**

`/modo [id_empresa] [normal|pos_solo|hibrido]`
    Cambia el modo de operación de una empresa.

`/status [id_empresa]`
    Muestra el estado general del sistema o de una empresa específica.

`/ayuda`
    Muestra esta ayuda.

`/salir`
    Cierra la consola de programador (desde la UI).
        """)

    def cerrar(self):
        """Cierra la conexión a la base de datos."""
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()
            logger.info("🔒 Conexión de ProgramadorAgent cerrada.")
