# Guía Rápida: Activar Cashea para un Cliente (5-10 minutos)

## Requisitos Previos
- El cliente debe estar **afiliado a Cashea** como comercio.
- Debes tener a mano las credenciales que Cashea proporcionó al cliente:
    - `Public API Key`
    - `Private API Key`
    - `Store ID`
- Tener acceso al sistema como usuario **Administrador**.

## Procedimiento

1.  **Inicia sesión** en el sistema de ventas (menú de consola) con un usuario administrador.
2.  Navega al menú de administración:
    `8. Administración de Usuarios → 6. Configurar Medios de Pago`
3.  En la ventana que se abre, selecciona la pestaña **"Cashea"**.
4.  Marca la casilla **"Activar Cashea"**.
5.  Completa los campos con las credenciales del cliente:
    - `Public API Key`: (Ej: `pk_live_abc123...`)
    - `Private API Key`: (Ej: `sk_live_xyz789...`)
    - `Store ID`: (Ej: `MI_TIENDA_001`)
6.  Configura los parámetros comerciales:
    - `Comisión (%)`: El porcentaje acordado con el cliente (generalmente 3-6%).
    - `Monto mínimo ($)`: Monto mínimo de compra para usar Cashea (generalmente $25.00).
7.  Haz clic en el botón **"Probar Conexión"**. Si las credenciales son correctas, verás un mensaje de éxito.
8.  Si la prueba es exitosa, haz clic en **"Guardar"**.

## Verificación

1.  Abre la **interfaz de ventas inteligente** (`run_inteligente.py`).
2.  Verifica que el botón **"Cashea"** (color morado) aparece junto a los otros métodos de pago.
3.  Realiza una venta de prueba con un monto superior al mínimo configurado.
4.  Al hacer clic en "Cashea", el sistema deberá mostrar el desglose de la inicial y las cuotas.
5.  Confirma la venta. El historial de ventas deberá mostrar la transacción con el tipo "CASHEA".
