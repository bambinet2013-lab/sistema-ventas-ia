"""
Modelo para cuentas bancarias de la empresa
"""
from dataclasses import dataclass
from typing import Optional, List
from loguru import logger

@dataclass
class Banco:
    idbanco: Optional[int] = None
    nombre: str = ""
    codigo_sudeban: Optional[str] = None
    activo: bool = True

@dataclass
class CuentaEmpresa:
    idcuenta: Optional[int] = None
    idbanco: Optional[int] = None
    nombre_banco: Optional[str] = None
    numero_cuenta: str = ""
    tipo_cuenta: str = "CORRIENTE"  # CORRIENTE, AHORRO
    moneda: str = "VES"  # VES, USD
    telefono_asociado: Optional[str] = None
    cedula_titular: Optional[str] = None
    activa: bool = True
    solo_programador: bool = False

class CuentaEmpresaRepo:
    """Repositorio para cuentas de la empresa"""
    
    def __init__(self, conn):
        self.conn = conn
    
    def listar_bancos(self) -> List[Banco]:
        """Lista todos los bancos activos"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT idbanco, nombre, codigo_sudeban 
                FROM banco 
                WHERE activo = 1 
                ORDER BY nombre
            """)
            
            bancos = []
            for row in cursor.fetchall():
                bancos.append(Banco(
                    idbanco=row[0],
                    nombre=row[1],
                    codigo_sudeban=row[2]
                ))
            return bancos
        except Exception as e:
            logger.error(f"Error listando bancos: {e}")
            return []
    
    def listar_cuentas(self, solo_programador: bool = False) -> List[CuentaEmpresa]:
        """Lista cuentas activas de la empresa"""
        try:
            cursor = self.conn.cursor()
            query = """
                SELECT c.idcuenta, c.numero_cuenta, c.tipo_cuenta, 
                       c.moneda, c.telefono_asociado, c.cedula_titular,
                       c.solo_programador, c.activa,
                       b.idbanco, b.nombre as banco_nombre
                FROM cuenta_empresa c
                JOIN banco b ON c.idbanco = b.idbanco
                WHERE c.activa = 1
            """
            if not solo_programador:
                query += " AND c.solo_programador = 0"
            query += " ORDER BY b.nombre, c.idcuenta"
            
            cursor.execute(query)
            
            cuentas = []
            for row in cursor.fetchall():
                cuentas.append(CuentaEmpresa(
                    idcuenta=row[0],
                    numero_cuenta=row[1],
                    tipo_cuenta=row[2],
                    moneda=row[3],
                    telefono_asociado=row[4],
                    cedula_titular=row[5],
                    solo_programador=bool(row[6]),
                    activa=bool(row[7]),
                    idbanco=row[8],
                    nombre_banco=row[9]
                ))
            return cuentas
        except Exception as e:
            logger.error(f"Error listando cuentas: {e}")
            return []
    
    def obtener_cuenta(self, idcuenta: int) -> Optional[CuentaEmpresa]:
        """Obtiene una cuenta por ID"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT c.idcuenta, c.numero_cuenta, c.tipo_cuenta, 
                       c.moneda, c.telefono_asociado, c.cedula_titular,
                       c.solo_programador, c.activa,
                       b.idbanco, b.nombre as banco_nombre
                FROM cuenta_empresa c
                JOIN banco b ON c.idbanco = b.idbanco
                WHERE c.idcuenta = ?
            """, (idcuenta,))
            
            row = cursor.fetchone()
            if row:
                return CuentaEmpresa(
                    idcuenta=row[0],
                    numero_cuenta=row[1],
                    tipo_cuenta=row[2],
                    moneda=row[3],
                    telefono_asociado=row[4],
                    cedula_titular=row[5],
                    solo_programador=bool(row[6]),
                    activa=bool(row[7]),
                    idbanco=row[8],
                    nombre_banco=row[9]
                )
            return None
        except Exception as e:
            logger.error(f"Error obteniendo cuenta {idcuenta}: {e}")
            return None
    
    def crear_cuenta(self, cuenta: CuentaEmpresa) -> Optional[int]:
        """Crea una nueva cuenta"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO cuenta_empresa 
                (idbanco, numero_cuenta, tipo_cuenta, moneda, 
                 telefono_asociado, cedula_titular, solo_programador)
                OUTPUT INSERTED.idcuenta
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                cuenta.idbanco,
                cuenta.numero_cuenta,
                cuenta.tipo_cuenta,
                cuenta.moneda,
                cuenta.telefono_asociado,
                cuenta.cedula_titular,
                1 if cuenta.solo_programador else 0
            ))
            
            row = cursor.fetchone()
            self.conn.commit()
            logger.success(f"✅ Cuenta creada ID: {row[0]}")
            return row[0] if row else None
        except Exception as e:
            logger.error(f"Error creando cuenta: {e}")
            self.conn.rollback()
            return None
    
    def actualizar_cuenta(self, cuenta: CuentaEmpresa) -> bool:
        """Actualiza una cuenta existente"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                UPDATE cuenta_empresa 
                SET idbanco = ?, numero_cuenta = ?, tipo_cuenta = ?,
                    moneda = ?, telefono_asociado = ?, cedula_titular = ?,
                    solo_programador = ?
                WHERE idcuenta = ?
            """, (
                cuenta.idbanco,
                cuenta.numero_cuenta,
                cuenta.tipo_cuenta,
                cuenta.moneda,
                cuenta.telefono_asociado,
                cuenta.cedula_titular,
                1 if cuenta.solo_programador else 0,
                cuenta.idcuenta
            ))
            
            self.conn.commit()
            logger.success(f"✅ Cuenta {cuenta.idcuenta} actualizada")
            return True
        except Exception as e:
            logger.error(f"Error actualizando cuenta {cuenta.idcuenta}: {e}")
            self.conn.rollback()
            return False
    
    def desactivar_cuenta(self, idcuenta: int) -> bool:
        """Desactiva una cuenta (no la elimina)"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                UPDATE cuenta_empresa 
                SET activa = 0 
                WHERE idcuenta = ?
            """, (idcuenta,))
            
            self.conn.commit()
            logger.success(f"✅ Cuenta {idcuenta} desactivada")
            return True
        except Exception as e:
            logger.error(f"Error desactivando cuenta {idcuenta}: {e}")
            self.conn.rollback()
            return False
            
    def asignar_metodo_pago(self, idcuenta, metodo_pago, activo=True):
        """
        Asigna un método de pago a una cuenta
        Args:
            idcuenta: ID de la cuenta
            metodo_pago: 'EFECTIVO_BS', 'EFECTIVO_USD', 'TARJETA_BS', 
                        'TARJETA_USD', 'PAGO_MOVIL', 'TRANSFERENCIA'
            activo: True para activar, False para desactivar
        Returns:
            bool: True si se asignó correctamente
        """
        try:
            cursor = self.conn.cursor()
            
            # Verificar si ya existe la asignación
            cursor.execute("""
                SELECT id FROM cuenta_metodo_pago 
                WHERE idcuenta = ? AND metodo_pago = ?
            """, (idcuenta, metodo_pago))
            
            if cursor.fetchone():
                # Actualizar estado
                cursor.execute("""
                    UPDATE cuenta_metodo_pago 
                    SET activo = ? 
                    WHERE idcuenta = ? AND metodo_pago = ?
                """, (1 if activo else 0, idcuenta, metodo_pago))
            else:
                # Insertar nueva asignación
                cursor.execute("""
                    INSERT INTO cuenta_metodo_pago (idcuenta, metodo_pago, activo)
                    VALUES (?, ?, ?)
                """, (idcuenta, metodo_pago, 1 if activo else 0))
            
            self.conn.commit()
            logger.success(f"✅ Método {metodo_pago} {'activado' if activo else 'desactivado'} para cuenta {idcuenta}")
            return True
            
        except Exception as e:
            logger.error(f"Error asignando método {metodo_pago} a cuenta {idcuenta}: {e}")
            self.conn.rollback()
            return False

    def obtener_cuentas_por_metodo(self, metodo_pago, solo_activas=True, solo_visibles=False):
        """
        Obtiene cuentas que soportan un método específico
        Args:
            metodo_pago: Método de pago a filtrar
            solo_activas: Solo cuentas activas
            solo_visibles: Solo cuentas no-programador (para cajeros)
        Returns:
            List[CuentaEmpresa]: Lista de cuentas
        """
        try:
            cursor = self.conn.cursor()
            
            query = """
                SELECT c.idcuenta, c.numero_cuenta, c.tipo_cuenta, 
                       c.moneda, c.telefono_asociado, c.cedula_titular,
                       c.solo_programador, c.activa,
                       b.idbanco, b.nombre as banco_nombre
                FROM cuenta_empresa c
                JOIN banco b ON c.idbanco = b.idbanco
                JOIN cuenta_metodo_pago cmp ON c.idcuenta = cmp.idcuenta
                WHERE cmp.metodo_pago = ? AND cmp.activo = 1
            """
            
            if solo_activas:
                query += " AND c.activa = 1"
            
            if solo_visibles:
                query += " AND c.solo_programador = 0"
                
            query += " ORDER BY b.nombre, c.idcuenta"
            
            cursor.execute(query, (metodo_pago,))
            
            cuentas = []
            for row in cursor.fetchall():
                cuentas.append(CuentaEmpresa(
                    idcuenta=row[0],
                    numero_cuenta=row[1],
                    tipo_cuenta=row[2],
                    moneda=row[3],
                    telefono_asociado=row[4],
                    cedula_titular=row[5],
                    solo_programador=bool(row[6]),
                    activa=bool(row[7]),
                    idbanco=row[8],
                    nombre_banco=row[9]
                ))
            return cuentas
            
        except Exception as e:
            logger.error(f"Error obteniendo cuentas para método {metodo_pago}: {e}")
            return []

    def obtener_metodos_por_cuenta(self, idcuenta):
        """
        Obtiene los métodos de pago asignados a una cuenta
        Args:
            idcuenta: ID de la cuenta
        Returns:
            List[str]: Lista de métodos activos
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT metodo_pago 
                FROM cuenta_metodo_pago 
                WHERE idcuenta = ? AND activo = 1
                ORDER BY metodo_pago
            """, (idcuenta,))
            
            return [row[0] for row in cursor.fetchall()]
            
        except Exception as e:
            logger.error(f"Error obteniendo métodos para cuenta {idcuenta}: {e}")
            return []            

