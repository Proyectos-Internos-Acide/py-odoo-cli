# Industria Textil Atlas E.I.R.L.

Este directorio contiene los scripts, configuraciones y documentación para la integración y automatización de la instancia de Odoo de **INDUSTRIA TEXTIL ATLAS E.I.R.L.** (fábrica de prendas de vestir).

## Información de la Empresa

| Campo | Detalle |
| :--- | :--- |
| **RUC** | `20453869882` |
| **Razón Social** | INDUSTRIA TEXTIL ATLAS E.I.R.L. |
| **Tipo de Empresa** | Empresa Individual de Responsabilidad Limitada |
| **Condición** | Activo |
| **Fecha de Inicio de Actividades** | 01 de Septiembre de 2004 |
| **Actividad Comercial** | Fabricación de Prendas de Vestir |
| **CIIU** | `18100` |

---

## Estructura de Almacenes en Odoo
El proyecto utiliza los almacenes reales preexistentes en la base de datos de Odoo:
1. **Almacén casa (WHC):** Ubicación principal de existencias utilizada para recepción de compras y almacenamiento mayorista (`WHC/Existencias`, ID: `16`).
2. **Almacén Tienda (WH):** Ubicación para venta al público, punto de venta y despacho a clientes (`WH/Stock`, ID: `5`).

*(Nota: Los almacenes temporales creados por error fueron renombrados a `[INACTIVO] ALMACEN GRANDE` y `[INACTIVO] ALMACEN TIENDA` para evitar conflictos en la interfaz de Odoo).*

---

## Scripts Disponibles

### 1. Generación Masiva de Datos
* **Archivo:** [generate_all_data.py](file:///home/acide/py-odoo-cli/knowledge/industria-textil-atlas/generate_all_data.py)
* **Descripción:** Automatiza la creación de los clientes, productos, reglas de abastecimiento, órdenes de compra, transferencias internas y órdenes de entrega utilizando los almacenes reales (`Almacén casa` y `Almacén Tienda`).
* **Ejecución:**
  ```bash
  python knowledge/industria-textil-atlas/generate_all_data.py
  ```

### 2. Generación de Historial (Últimos 5 Días)
* **Archivo:** [generate_historical_data.py](file:///home/acide/py-odoo-cli/knowledge/industria-textil-atlas/generate_historical_data.py)
* **Descripción:** Genera un historial completo de movimientos de inventario distribuidos a lo largo de los últimos 5 días (compras, traslados entre almacenes y ventas), aplicando las fechas históricas correspondientes (`scheduled_date` y `date_done`) en Odoo.
* **Ejecución:**
  ```bash
  python knowledge/industria-textil-atlas/generate_historical_data.py
  ```

### 3. Verificación de Datos e Inventario
* **Archivo:** [verify_stock_and_partners.py](file:///home/acide/py-odoo-cli/knowledge/industria-textil-atlas/verify_stock_and_partners.py)
* **Descripción:** Imprime un reporte detallado con los almacenes activos, clientes creados, reglas de abastecimiento y cantidades físicas por ubicación en Odoo.
* **Ejecución:**
  ```bash
  python knowledge/industria-textil-atlas/verify_stock_and_partners.py
  ```

### 4. Utilidades y Diagnóstico
* [cleanup_warehouses.py](file:///home/acide/py-odoo-cli/knowledge/industria-textil-atlas/cleanup_warehouses.py) / [force_cleanup.py](file:///home/acide/py-odoo-cli/knowledge/industria-textil-atlas/force_cleanup.py): Scripts para aislar y renombrar/desactivar almacenes e ubicaciones obsoletas.
* [make_products_storable.py](file:///home/acide/py-odoo-cli/knowledge/industria-textil-atlas/make_products_storable.py): Habilita el seguimiento físico de inventario para los productos del catálogo.

---

## Datos de Prueba Generados

### Clientes Creados (res.partner)
* **Juan Carlos Quispe Mamani** (DNI: `10453869811` - Arequipa)
* **Ana María Condori Huamán** (DNI: `09348123` - Arequipa)
* **Carlos Alberto Sánchez Rodríguez** (DNI: `40128945` - Lima)
* **Patricia Fiorella Torres Chávez** (DNI: `43928174` - Lima)
* **Víctor Raúl Haya de la Torre** (DNI: `07281945` - Lima)

### Productos y Niveles de Stock Actuales (Almacenes Activos)

| Producto | Código | Almacén Casa (WHC/Existencias) | Almacén Tienda (WH/Stock) |
| :--- | :--- | :---: | :---: |
| **Polo Camisero Piqué** | `POLO-PIQUE` | 680.0 uds | 270.0 uds |
| **Camisa de Vestir Oxford** | `CAMISA-OXFORD` | 360.0 uds | 90.0 uds |
| **Pantalón Chino Slim Fit** | `PANTALON-CHINO` | 210.0 uds | 90.0 uds |
| **Casaca Cortaviento Térmica** | `CASACA-CORTAVIENTO` | 210.0 uds | 60.0 uds |
| **Polera con Capucha Algodón** | `POLERA-CAPUCHA` | 250.0 uds | 130.0 uds |
