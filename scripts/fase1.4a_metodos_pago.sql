-- =====================================================
-- FASE 1.4A: TABLA PARA ASIGNAR MÉTODOS DE PAGO A CUENTAS
-- SOLO CREA SI NO EXISTE - NO MODIFICA NADA EXISTENTE
-- =====================================================

USE SistemaVentas;
GO

-- Tabla de relación cuenta-método de pago
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='cuenta_metodo_pago' AND xtype='U')
CREATE TABLE cuenta_metodo_pago (
    id INT IDENTITY(1,1) PRIMARY KEY,
    idcuenta INT NOT NULL,
    metodo_pago VARCHAR(20) NOT NULL,
    activo BIT DEFAULT 1,
    fecha_asignacion DATETIME DEFAULT GETDATE(),
    FOREIGN KEY (idcuenta) REFERENCES cuenta_empresa(idcuenta),
    CONSTRAINT UQ_cuenta_metodo UNIQUE (idcuenta, metodo_pago)
);
GO

-- Índices para mejorar performance
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_cuenta_metodo_pago_idcuenta')
CREATE INDEX IX_cuenta_metodo_pago_idcuenta ON cuenta_metodo_pago(idcuenta);
GO

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_cuenta_metodo_pago_metodo')
CREATE INDEX IX_cuenta_metodo_pago_metodo ON cuenta_metodo_pago(metodo_pago);
GO

PRINT '✅ Tabla cuenta_metodo_pago creada exitosamente';
GO

-- Migrar datos existentes (para compatibilidad)
-- Esto asigna automáticamente PAGO_MOVIL y TRANSFERENCIA a cuentas que tengan teléfono
INSERT INTO cuenta_metodo_pago (idcuenta, metodo_pago)
SELECT idcuenta, 'PAGO_MOVIL'
FROM cuenta_empresa
WHERE telefono_asociado IS NOT NULL
AND NOT EXISTS (
    SELECT 1 FROM cuenta_metodo_pago 
    WHERE idcuenta = cuenta_empresa.idcuenta 
    AND metodo_pago = 'PAGO_MOVIL'
);
GO

INSERT INTO cuenta_metodo_pago (idcuenta, metodo_pago)
SELECT idcuenta, 'TRANSFERENCIA'
FROM cuenta_empresa
WHERE NOT EXISTS (
    SELECT 1 FROM cuenta_metodo_pago 
    WHERE idcuenta = cuenta_empresa.idcuenta 
    AND metodo_pago = 'TRANSFERENCIA'
);
GO

PRINT '✅ Datos migrados para compatibilidad';
GO
