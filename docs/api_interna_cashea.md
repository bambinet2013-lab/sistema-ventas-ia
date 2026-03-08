# API Interna: Módulo Cashea

## Clase: `CasheaAgent` (`agente_escritorio/agents/cashea_agent.py`)

Agente principal para la integración con Cashea.

### Métodos Principales

#### `__init__(self)`
Inicializa el agente y carga la configuración desde la base de datos (tabla `configuracion_medios_pago`).

#### `esta_activo(self) -> bool`
Retorna `True` si Cashea está activo en la configuración, `False` en caso contrario.

#### `solicitar_autorizacion(self, monto_total: float, id_cliente: int = None) -> dict`
Simula la solicitud de autorización a la API de Cashea.
- **Args:**
    - `monto_total`: Monto total de la venta en USD.
    - `id_cliente`: ID del cliente (opcional).
- **Returns:** Diccionario con el resultado de la autorización. Ejemplo de éxito:
    ```json
    {
        'success': True,
        'autorizado': True,
        'monto_total': 100.0,
        'inicial': 40.0,
        'resto': 60.0,
        'porcentaje_inicial': 40,
        'cuotas': 3,
        'referencia': 'CASHEA-240306-XXXX',
        'mensaje': 'Aprobado: Paga $40.0 hoy y 3 cuotas...'
    }
