-- ===================================================
-- ESTRUCTURA COMPLETA DE BASE DE DATOS SistemaVentas
-- Generado el: mié 04 mar 2026 10:15:16 -04
-- ===================================================

USE [master];
GO

IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = N'SistemaVentas')
BEGIN
    CREATE DATABASE [SistemaVentas];
END
GO

USE [SistemaVentas];
GO

-- ===================================================
-- TABLAS PRINCIPALES
-- ===================================================

-- ===================================================
-- CLAVES FORÁNEAS
-- ===================================================


-- ===================================================
-- FIN DEL SCRIPT
-- ===================================================
