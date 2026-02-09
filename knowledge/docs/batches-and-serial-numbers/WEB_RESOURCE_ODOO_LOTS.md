---
title: Uso de lotes para gestionar grupos y productos en Odoo 15
source: https://www.odoo.com/documentation/15.0/es/applications/inventory_and_mrp/inventory/management/lots_serial_numbers/lots.html
---

# Use lotes para gestionar grupos y productos

En Odoo hay dos maneras de identificar y rastrear productos: **lotes** y **números de serie**.  
En este recurso se documenta el uso de **lotes** para gestionar grupos de productos.

Un **lote** indica un grupo específico de artículos que:

- Se recibió, almacenó o envió desde un almacén, o
- Se fabricó dentro de la empresa en un mismo proceso o periodo.

Los fabricantes asignan un **número de lote** a grupos de producto que comparten propiedades en común, por ejemplo:

- Misma fecha de fabricación.
- Mismo proveedor o lote de producción.
- Misma fecha de caducidad.

Esto permite:

- Identificar rápidamente un conjunto de productos dentro de un grupo.
- Seguir el ciclo de vida del grupo completo de inicio a fin.
- Gestionar **retiros de productos** y **fechas de caducidad** de forma eficiente.

> Referencias relacionadas:
> - [Usar números de serie para rastrear productos](https://www.odoo.com/documentation/15.0/es/applications/inventory_and_mrp/inventory/management/lots_serial_numbers/serial_numbers.html)
> - [Diferencia entre lotes y números de serie](https://www.odoo.com/documentation/15.0/es/applications/inventory_and_mrp/inventory/management/lots_serial_numbers/differences.html)

---

## Activar lotes y números de serie

Para rastrear productos por medio de lotes, primero se debe activar la función **Números de serie y lote**:

1. Ir a `Inventario ‣ Configuración ‣ Ajustes`.
2. Buscar la sección **Trazabilidad**.
3. Marcar la casilla **Números de serie y lote**.
4. Hacer clic en **Guardar**.

Esto habilita el uso de:

- **Lotes** para grupos de productos.
- **Números de serie** para productos individuales.

---

## Rastrear productos por lotes

Una vez activada la funcionalidad, se puede configurar cada producto para que se rastree **por lotes**.

Pasos:

1. Ir a `Inventario ‣ Productos ‣ Productos`.
2. Seleccionar el producto a configurar.
3. Hacer clic en **Editar**.
4. Ir a la pestaña **Inventario**.
5. En la sección **Trazabilidad**, seleccionar **Por lotes**.
6. Guardar los cambios.

Con esta configuración:

- El producto se controlará por **número de lote**.
- Podrás asignar números de lote (existentes o nuevos) a grupos de unidades recibidas o fabricadas.

> Importante: Si el producto ya tenía existencias antes de activar el seguimiento por lotes/números de serie, será necesario hacer un **ajuste de inventario** para asignar lotes a ese stock histórico.

### Crear nuevos lotes para productos ya en existencias

Es posible crear lotes nuevos para productos que ya están en existencia y que aún no tienen número de lote asignado.

1. Ir a `Inventario ‣ Productos ‣ Lotes/Números de serie`.
2. Hacer clic en **Crear**.
3. Odoo genera automáticamente un valor en **Lote/Número de serie** (puede editarse).

> Truco: Odoo propone el nuevo número de lote/serie siguiendo la numeración más reciente, pero puedes cambiarlo manualmente haciendo clic en el campo correspondiente.

En el formulario del nuevo lote:

1. En el campo **Producto**, seleccionar el producto al que se le asignará el lote.
2. Opcionalmente:
   - Ajustar la **Cantidad**.
   - Definir una **Referencia interna** para trazabilidad.
   - Asociar un **Sitio web** (en entornos multi-sitio).
   - Añadir una **descripción** en la pestaña de descripción.
3. Hacer clic en **Guardar**.

Luego:

1. Ir a `Inventario ‣ Productos ‣ Productos`.
2. Abrir el producto al que se le asignó el lote.
3. Usar el botón inteligente **Lote/Número de serie** para ver el lote creado.
4. Al recibir o fabricar más unidades de este producto, se puede reutilizar ese mismo **número de lote**.

---

## Gestión de lotes para envío y recepción

Los números de lote se pueden asignar tanto a bienes **entrantes** (compras/recepciones) como a bienes **salientes** (ventas/entregas).

### Gestión de lotes al recibir productos (bienes entrantes)

1. Ir a la aplicación **Compra** y hacer clic en **Crear**.
2. En la **Solicitud de cotización**:
   - Indicar el **Proveedor**.
   - Agregar productos en la pestaña **Productos** (botón **Agregar un producto**).
   - Ajustar la **Cantidad** en la columna correspondiente.
3. Hacer clic en **Confirmar orden** para convertir la solicitud en **Orden de compra**.
4. Pulsar el botón inteligente **Recepción** para abrir el albarán de entrada en almacén.

> Nota: Si se hace clic en **Validar** antes de asignar un número de lote a las cantidades, aparecerá una ventana de **Error de usuario** indicando que es necesario ingresar un número de serie/lote. No se puede validar sin ese dato.

Para asignar los lotes:

1. En la recepción, ir a la pestaña **Operaciones**.
2. Hacer clic en el icono de **Opciones adicionales** (tipo hamburguesa, cuatro líneas horizontales).
3. Se abre la ventana de **Operaciones detalladas**.
4. En la parte inferior, usar la columna **Nombre del número de lote/serie** para registrar los lotes.

Hay dos formas:

#### Asignar números de lote de forma manual

1. Hacer clic en **Agregar una línea**.
2. Elegir la **Ubicación** donde se almacenará en la columna A.
3. Escribir el **Nombre del número de lote**.
4. Indicar la **Cantidad hecha**.

Si las cantidades se deben repartir en varios lotes o ubicaciones:

- Repetir **Agregar una línea** con diferentes números de lote y ubicaciones.
- Asegurarse de que la suma de **Cantidad hecha** sea igual a la **Demanda**.

#### Copiar y pegar números de lote desde una hoja de cálculo

1. Preparar una hoja de cálculo con todos los **números de lote** recibidos (o definidos).
2. Copiar esa lista.
3. En la ventana de **Operaciones detalladas**, pegar en la columna **Lote/Número de serie**.
4. Odoo creará automáticamente tantas líneas como números se hayan pegado.
5. Completar manualmente:
   - Las **Ubicaciones** (columna A).
   - Las **Cantidades hechas** por línea.

Una vez asignados los lotes para toda la cantidad:

1. Hacer clic en **Confirmar** para cerrar la ventana emergente.
2. Pulsar **Validar** en la recepción.
3. Se habilita el botón inteligente **Trazabilidad** para revisar:
   - Documento de **Referencia**.
   - **Producto**.
   - **Lote/Número de serie**.
   - Movimientos relacionados.

---

### Gestión de lotes en órdenes de entrega (bienes salientes)

1. Ir a la aplicación **Ventas** y hacer clic en **Crear**.
2. En el formulario de **Cotización**:
   - Agregar un **Cliente**.
   - Añadir productos en la pestaña **Líneas de orden** (botón **Agregar un producto**).
   - Ajustar la **Cantidad** de cada línea.
3. Hacer clic en **Confirmar** para convertir la cotización en **Orden de venta**.
4. Pulsar el botón inteligente **Entrega** para abrir el albarán de salida en almacén.

En la entrega:

1. Hacer clic en el icono de **Opciones adicionales** (cuatro líneas horizontales) en la pestaña **Operaciones**.
2. Se abre la ventana de **Operaciones detalladas**.
3. Odoo selecciona automáticamente un **Lote/Número de serie** para cubrir la **cantidad reservada**, si hay stock suficiente en un solo lote.

Casos posibles:

- **Hay stock suficiente en un lote**:
  - Se reserva toda la **Demanda** de ese lote.
- **No hay stock suficiente en un solo lote**:
  - Las cantidades se reparten entre varios lotes.
  - Es necesario ajustar la **Cantidad hecha** por lote.

> Nota: El lote propuesto para las entregas dependerá de la **estrategia de remoción** configurada (FIFO, LIFO, etc.).  
> Ver: [Estrategias de remoción (PEPS, UEPS, LIFO)](https://www.odoo.com/documentation/15.0/es/applications/inventory_and_mrp/inventory/routes/strategies/removal.html)

Para completar el proceso:

1. Hacer clic en **Agregar una línea** si se requiere usar más lotes.
2. Seleccionar otros **Lotes/Números de serie**.
3. Ajustar las **Cantidades hechas**.
4. Hacer clic en **Confirmar** para cerrar la ventana emergente.
5. Pulsar **Validar** para confirmar la entrega.

Después de validar:

- El botón inteligente **Trazabilidad** muestra:
  - Documento de **Referencia**.
  - **Producto**.
  - **Fecha**.
  - **Lote/Número de serie**.
  - Referencias a recepciones previas que compartan el mismo número de lote.

---

## Gestione lotes para diferentes tipos de operaciones

Comportamiento por defecto en Odoo:

- En **recepciones (compras)**:
  - Se pueden **crear nuevos lotes**.
  - No se pueden usar lotes existentes.
- En **órdenes de entrega (ventas)**:
  - No se pueden crear lotes nuevos.
  - Solo se pueden usar **lotes existentes**.

Para cambiar esta configuración por tipo de operación:

1. Ir a `Inventario ‣ Configuración ‣ Tipos de operación`.
2. Seleccionar el tipo de operación deseado.

Ejemplos:

- **Recepciones**:
  - Activar la opción **Utilizar números de lotes/de serie existentes** en la sección **Trazabilidad**.
- **Órdenes de entrega**:
  - Activar la opción **Crear nuevos números de lote/de serie**.

No olvidar **Guardar** los cambios.

> Truco: Para transferencias internas dentro del mismo almacén, que involucren productos con seguimiento por lote, es recomendable activar **Utilizar números de lotes/de serie existentes** en los tipos de operación de **recibos de inventario**.

---

## 6. Trazabilidad de lotes y reportes

Los reportes de **trazabilidad** permiten ver el ciclo de vida del producto:

- De dónde vino y **cuándo**.
- Dónde se **almacenó**.
- A quién y **cuándo** se entregó.

### 6.1. Tablero de Lotes/Números de serie

1. Ir a `Inventario ‣ Productos ‣ Lotes/Números de serie`.
2. Allí se ve el tablero de **Lotes/Números de serie**.
3. Se listan todos los productos a los que se les ha asignado un número de lote.
4. Se puede:
   - Expandir cada línea para ver números de lote asociados y cantidades.
   - Agrupar por **Producto**, **Lote/Número de serie** o **Fecha de caducidad**.

### 6.2. Reporte de trazabilidad

1. Desde el tablero, hacer clic en un lote específico.
2. En el formulario del lote, pulsar el botón **Trazabilidad (Traceability)**.
3. Verás todos los movimientos de stock donde se utilizó ese lote, con sus documentos de referencia.

También puedes usar los reportes de:

- **Historial de movimientos**.
- **Análisis de movimientos**.

filtrando o agrupando por **Lote/Número de serie**.

---

## 7. Referencia de imágenes (saas‑18.4)

La página oficial de *Lot numbers* en Odoo saas‑18.4 incluye capturas para:

- Activar **Lots & Serial Numbers**.
- Configurar productos con **By Lots**.
- El popup **Detailed Operations** en recepciones/entregas.
- El tablero de **Lots/Serial Numbers** y el reporte de trazabilidad.

Para gestionarlas en local (como en el recurso de SUNAT):

1. Abrir  
   `https://www.odoo.com/documentation/saas-18.4/es/applications/inventory_and_mrp/inventory/product_management/product_tracking/lots.html`
2. Inspeccionar cada imagen con las herramientas de desarrollador y copiar su URL (normalmente bajo `/documentation/saas-18.4/_images/...`).
3. Descargar a `knowledge/docs/batches-and-serial-numbers/imgs/`, por ejemplo:

```bash
cd knowledge/docs/batches-and-serial-numbers
mkdir -p imgs
curl -o imgs/lots-setting.png "https://www.odoo.com/documentation/saas-18.4/_images/lots-setting.png"
```

4. Referenciar las imágenes con rutas relativas:

```markdown
![Ajuste de lotes en Inventario](imgs/lots-setting.png)
```

De esta forma tendrás la documentación de **lotes** alineada con Odoo saas‑18.4 y las imágenes disponibles en local.


![Reporte de trazabilidad de lotes y números de serie](https://www.odoo.com/documentation/15.0/_images/lots-traceability-report.png)

---

## Referencia de imágenes

Todas las imágenes apuntan al sitio oficial de Odoo.  
Si quieres descargarlas para trabajarlas en local (por ejemplo en `knowledge/docs/batches-and-serial-numbers/imgs/`), puedes usar esta tabla como referencia:

| Descripción                                                                 | URL (Odoo)                                                                                 | Nombre sugerido local                       |
|----------------------------------------------------------------------------|--------------------------------------------------------------------------------------------|---------------------------------------------|
| Ajuste activado: números de serie y lote en Inventario                     | `https://www.odoo.com/documentation/15.0/_images/lots-enabled-lots-setting.png`           | `lots-enabled-lots-setting.png`             |
| Formulario de producto con seguimiento por lotes                           | `https://www.odoo.com/documentation/15.0/_images/lots-tracking-product-form.png`          | `lots-tracking-product-form.png`            |
| Nuevo número de lote creado para producto en existencias                   | `https://www.odoo.com/documentation/15.0/_images/lots-new-lot-number.png`                 | `lots-new-lot-number.png`                   |
| Error de usuario: falta asignar lote/número de serie en recepción          | `https://www.odoo.com/documentation/15.0/_images/lots-user-error-popup.png`               | `lots-user-error-popup.png`                 |
| Asignación manual de lotes en operaciones detalladas                       | `https://www.odoo.com/documentation/15.0/_images/lots-assign-lot-number-popup.png`        | `lots-assign-lot-number-popup.png`          |
| Ejemplo de hoja de cálculo con números de lote                             | `https://www.odoo.com/documentation/15.0/_images/lots-excel-spreadsheet.png`              | `lots-excel-spreadsheet.png`                |
| Ventana de operaciones detalladas para órdenes de entrega con lotes        | `https://www.odoo.com/documentation/15.0/_images/lots-detailed-operations-popup.png`      | `lots-detailed-operations-popup.png`        |
| Ajustes de tipos de operación para gestión de lotes                        | `https://www.odoo.com/documentation/15.0/_images/lots-operations-type-form.png`           | `lots-operations-type-form.png`             |
| Reporte de trazabilidad de lotes y números de serie                        | `https://www.odoo.com/documentation/15.0/_images/lots-traceability-report.png`            | `lots-traceability-report.png`              |

Ejemplo de descarga desde la raíz del proyecto:

```bash
cd knowledge/docs/batches-and-serial-numbers
mkdir -p imgs
curl -o imgs/lots-enabled-lots-setting.png "https://www.odoo.com/documentation/15.0/_images/lots-enabled-lots-setting.png"
curl -o imgs/lots-tracking-product-form.png "https://www.odoo.com/documentation/15.0/_images/lots-tracking-product-form.png"
curl -o imgs/lots-new-lot-number.png "https://www.odoo.com/documentation/15.0/_images/lots-new-lot-number.png"
curl -o imgs/lots-user-error-popup.png "https://www.odoo.com/documentation/15.0/_images/lots-user-error-popup.png"
curl -o imgs/lots-assign-lot-number-popup.png "https://www.odoo.com/documentation/15.0/_images/lots-assign-lot-number-popup.png"
curl -o imgs/lots-excel-spreadsheet.png "https://www.odoo.com/documentation/15.0/_images/lots-excel-spreadsheet.png"
curl -o imgs/lots-detailed-operations-popup.png "https://www.odoo.com/documentation/15.0/_images/lots-detailed-operations-popup.png"
curl -o imgs/lots-operations-type-form.png "https://www.odoo.com/documentation/15.0/_images/lots-operations-type-form.png"
curl -o imgs/lots-traceability-report.png "https://www.odoo.com/documentation/15.0/_images/lots-traceability-report.png"
```

Si guardas las imágenes en `imgs/`, puedes referenciarlas en este mismo archivo con rutas relativas, por ejemplo: `![Lotes en recepción](imgs/lots-user-error-popup.png)`.


