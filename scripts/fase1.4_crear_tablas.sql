-- =====================================================
-- SCRIPT PARA TABLAS DE PAGO MIXTO (FASE 1.4)
-- EJECUTAR UNA SOLA VEZ
-- =====================================================

USE SistemaVentas;
GO

-- Tabla de bancos
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='banco' AND xtype='U')
CREATE TABLE banco (
    idbanco INT IDENTITY(1,1) PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    codigo_sudeban VARCHAR(4) NULL,
    activo BIT DEFAULT 1,
    fecha_registro DATETIME DEFAULT GETDATE()
);
GO

-- Insertar bancos principales de Venezuela
IF NOT EXISTS (SELECT * FROM banco)
INSERT INTO banco (nombre, codigo_sudeban) VALUES
('Banco de Venezuela', '0102'),
('Banesco', '0134'),
('Mercantil', '0105'),
('Provincial', '0108'),
('BOD', '0116'),
('Banco Exterior', '0115'),
('Banco Nacional de Crédito', '0191'),
('Banplus', '0174'),
('Bancaribe', '0114');
GO

-- Tabla de cuentas de la empresa
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='cuenta_empresa' AND xtype='U')
CREATE TABLE cuenta_empresa (
    idcuenta INT IDENTITY(1,1) PRIMARY KEY,
    idbanco INT NOT NULL,
    numero_cuenta VARCHAR(30) NOT NULL,
    tipo_cuenta VARCHAR(20) NOT NULL CHECK (tipo_cuenta IN ('CORRIENTE', 'AHORRO')),
    moneda VARCHAR(3) DEFAULT 'VES' CHECK (moneda IN ('VES', 'USD')),
    telefono_asociado VARCHAR(20) NULL,
    cedula_titular VARCHAR(15) NULL,
    activa BIT DEFAULT 1,
    solo_programador BIT DEFAULT 0,
    fecha_registro DATETIME DEFAULT GETDATE(),
    FOREIGN KEY (idbanco) REFERENCES banco(idbanco)
);
GO

-- Tabla de detalle de pagos múltiples
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='venta_pago_detalle' AND xtype='U')
CREATE TABLE venta_pago_detalle (
    idpago INT IDENTITY(1,1) PRIMARY KEY,
    idventa INT NOT NULL,
    metodo_pago VARCHAR(20) NOT NULL,
    monto_bs DECIMAL(10,2) NOT NULL,
    moneda_original VARCHAR(3) NULL,
    monto_original_usd DECIMAL(10,2) NULL,
    idcuenta_destino INT NULL,
    referencia_cliente VARCHAR(50) NULL,
    telefono_cliente VARCHAR(20) NULL,
    igtf_aplicado BIT DEFAULT 0,
    igtf_monto DECIMAL(10,2) NULL,
    comision_banco DECIMAL(10,2) NULL,
    neto_parcial DECIMAL(10,2) NULL,
    estado_pago VARCHAR(20) DEFAULT 'COMPLETADO',
    fecha_registro DATETIME DEFAULT GETDATE(),
    fecha_confirmacion DATETIME NULL,
    confirmado_por INT NULL,
    FOREIGN KEY (idventa) REFERENCES venta(idventa),
    FOREIGN KEY (idcuenta_destino) REFERENCES cuenta_empresa(idcuenta)
);
GO

-- Índices
CREATE INDEX IX_venta_pago_detalle_idventa ON venta_pago_detalle(idventa);
CREATE INDEX IX_venta_pago_detalle_estado ON venta_pago_detalle(estado_pago);
GO

PRINT '✅ Tablas de pago mixto creadas exitosamente';
