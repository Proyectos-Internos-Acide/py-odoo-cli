# CM Line EIRL Inventory

Este proyecto contiene scripts y herramientas específicas para la gestión de inventario y datos de **CM Line EIRL**.

## Scripts Disponibles

### `debug_customer.py`
Busca y muestra información cruda de clientes basada en su nombre. Útil para verificar IDs y datos antes de realizar operaciones.

### `delete_jessica_huaman.py`
**⚠️ PELIGRO**
Script de un solo uso para eliminar (o archivar) al partner 'Jessica Huaman Arias'.

### `create_client.py`
Crea (o actualiza) al cliente 'HUAMAN ARIAS JESSICA' con los datos correctos de SUNAT:
- RUC: 10425620687
- Tipo Doc: RUC (Código 6)
- Email: contactorogeris@gmail.com
Asegura que el tipo de documento sea explícitamente el ID de RUC para evitar errores de facturación (Código 1007/0111).
