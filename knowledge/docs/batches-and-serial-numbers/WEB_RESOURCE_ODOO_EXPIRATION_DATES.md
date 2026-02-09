---
title: Fechas de vencimiento y caducidad en Odoo 15
source: https://www.odoo.com/documentation/15.0/es/applications/inventory_and_mrp/inventory/management/lots_serial_numbers/expiration_dates.html
---

# Fechas de vencimiento

En Odoo se pueden usar **fechas de vencimiento/caducidad** para gestionar el ciclo de vida de productos **perecederos**:

- Reducen pérdidas por productos que caducan sin control.
- Evitan enviar productos caducados a los clientes.
- Permiten planificar mejor la rotación de inventario.

Las fechas de caducidad solo pueden usarse en productos que se gestionan con **lotes** o **números de serie**.  
Una vez que se asigna un lote o número de serie, se puede configurar su **información de caducidad**.

> Referencias relacionadas:
> - [Use lotes para gestionar grupos y productos](https://www.odoo.com/documentation/15.0/es/applications/inventory_and_mrp/inventory/management/lots_serial_numbers/lots.html)
> - [Usar números de serie para rastrear productos](https://www.odoo.com/documentation/15.0/es/applications/inventory_and_mrp/inventory/management/lots_serial_numbers/serial_numbers.html)

---

## Activar las fechas de caducidad

1. Ir a `Inventario ‣ Configuración ‣ Ajustes`.
2. En la sección **Trazabilidad**, marcar:
   - **Lotes y números de serie**.
3. Al activar lo anterior, aparece la opción **Fechas de caducidad**:
   - Marcar la casilla para activarla.
4. Hacer clic en **Guardar**.

> Truco: Al activar **Lotes y números de serie** también se pueden activar opciones como:
> - Mostrar números de lote/serie en **recibos de entrega**.
> - Mostrar números de lote/serie en **facturas**.
> - Mostrar **fecha de caducidad** en notas de remisión.  
> Estas opciones ayudan a tener **trazabilidad completa** y a gestionar mejor retiros de productos o lotes problemáticos.

---

## Configurar fechas de caducidad en productos

Una vez activadas las funciones de **Fechas de caducidad** y **Lotes y números de serie**, se puede configurar la caducidad por producto.

1. Ir a `Inventario ‣ Productos ‣ Productos`.
2. Seleccionar el producto.
3. Hacer clic en **Editar**.

> Importante: El **Tipo de producto** (en la pestaña **Información general**) debe ser **Producto almacenable**.

Luego:

1. Ir a la pestaña **Inventario**.
2. En la sección **Trazabilidad**:
   - Marcar **Por número de serie único** o **Por lotes**.
3. Al hacerlo, aparece la casilla **Fecha de caducidad**:
   - Marcarla.
4. A la derecha se habilita el campo **Fechas**, donde se definen los parámetros de caducidad.

> Nota: Si el producto ya tenía stock antes de activar el seguimiento por lotes/números de serie, puede ser necesario un **ajuste de inventario** para asignar lotes a ese stock previo.

### Campos de fechas de caducidad

En el bloque **Fechas** hay cuatro valores clave:

- **Fecha de caducidad**:  
  Número de días después de la **recepción/fabricación** a partir del cual el producto ya no debe usarse o consumirse por seguridad.

- **Consumir preferentemente antes de**:  
  Número de días **antes de la fecha de caducidad** en los que el producto empieza a deteriorarse, pero aún **no es peligroso**.

- **Tiempo de remoción**:  
  Número de días antes de la fecha de caducidad en los que el producto debe retirarse del stock (por ejemplo, retirarlo de la zona de venta).

- **Periodo de alerta**:  
  Número de días antes de la caducidad en los que se debe **disparar una alerta** para los productos de un lote o número de serie.

> Nota: Estos valores se usan para calcular automáticamente las fechas de caducidad/alerta en cada entrada de inventario (compras o fabricación).

Después de rellenar estos campos, hacer clic en **Guardar**.

> Truco: Aunque no se rellenen estos valores de forma global en el producto, siempre se pueden ajustar **fechas y lotes de forma manual** al recibir o entregar productos.

---

## Configurar fechas de caducidad al recibir productos (lotes/números de serie)

Se pueden generar fechas de caducidad para bienes **entrantes** directamente desde la **Orden de compra**:

1. Ir a la app **Compra** y hacer clic en **Crear**.
2. En la **Solicitud de cotización**:
   - Indicar el **Proveedor**.
   - Agregar productos (botón **Añadir un producto**).
   - Ajustar la **Cantidad** en la columna correspondiente.
3. Hacer clic en **Confirmar orden** para convertirla en **Orden de compra**.
4. Pulsar el botón inteligente **Recepción** para abrir el albarán de entrada.

> Nota: Si se pulsa **Validar** antes de asignar un lote/número de serie, aparece una ventana de **Error de usuario** indicando que hay que registrar lote o número de serie. No se puede validar sin ello.

Para asignar lote/número de serie y fechas:

1. En la recepción, pulsar el icono de **Opciones adicionales** (a la derecha de la línea del producto).
2. Se abre la ventana **Operaciones detalladas**.
3. Hacer clic en **Agregar una línea**.
4. En el campo **Lote/número de serie**, asignar el valor deseado.
5. Odoo rellenará automáticamente la **fecha de caducidad** según la configuración del producto (si se definió en el bloque **Fechas**).
6. Marcar la **Cantidad hecha**.
7. Pulsar **Confirmar** y luego **Validar**.

Si el producto no tenía configurados valores en **Fechas**, es posible ingresar la fecha de caducidad **manual** en esta misma ventana.

Tras validar la recepción:

- El botón **Trazabilidad** muestra un reporte con:
  - Documento de referencia.
  - Producto.
  - Lote/número de serie.
  - Fechas de caducidad asociadas.

---

## Configurar fechas de caducidad en productos fabricados

También se pueden gestionar fechas de caducidad en productos **fabricados** mediante órdenes de fabricación.

1. Ir a `Fabricación ‣ Operaciones ‣ Órdenes de fabricación`.
2. Hacer clic en **Crear**.
3. En el formulario:
   - Seleccionar el **Producto** a fabricar.
   - Indicar la **Cantidad a producir**.

> Nota: Debe haber materiales en las líneas de **Producto** (lista de materiales o añadidos manualmente) para poder fabricar.

Luego:

1. Hacer clic en **Confirmar**.
2. En el campo **Lote/Número de serie**:
   - Seleccionar un lote existente, o
   - Hacer clic en el **+ verde** para crear uno nuevo.
3. Definir la **Cantidad** a producir.
4. Hacer clic en **Marcar como hecho**.

Para revisar los detalles de caducidad:

1. Hacer clic en el icono de **enlace externo** al lado del campo **Lote/Número de serie**.
2. Se abrirá el formulario de ese lote/número de serie.
3. En la pestaña **Fechas** se verán los datos de:
   - Fecha de caducidad.
   - Consumir preferentemente antes de.
   - Tiempo de remoción.
   - Periodo de alerta.

Esta misma información también está disponible desde `Inventario ‣ Productos ‣ Lote/Número de serie`.

---

## Vender productos con fechas de caducidad

Los productos con fecha de caducidad se **venden** igual que cualquier otro producto, pero respetando la **estrategia de remoción FEFO** (First Expired, First Out) para priorizar los lotes que caducan antes.

Pasos:

1. Ir a la app **Ventas** y hacer clic en **Crear**.
2. En la **Cotización**:
   - Agregar un **Cliente**.
   - Añadir productos (botón **Agregar un producto**).
   - Ajustar la **Cantidad**.
3. Ir a la pestaña **Otra información**.
4. En la sección **Entrega**, ajustar la **Fecha de entrega**.
5. Confirmar la orden con el botón **Confirmar**.
6. Pulsar el botón inteligente **Entrega** para abrir el albarán de salida.
7. En el albarán:
   - Pulsar **Validar** y luego **Aplicar** en la ventana emergente para procesar las cantidades hechas.

Si los productos se entregan **antes del periodo de alerta**, no se mostrarán advertencias.

> Importante: Para que Odoo venda correctamente productos perecederos respetando fechas de caducidad, la estrategia de remoción de la ubicación debe ser **FEFO (First Expired, First Out)**.  
> Si no hay stock suficiente en un lote, Odoo completará automáticamente con el siguiente lote que tenga la **fecha de caducidad más cercana**.  
> Esto se configura en las **Categorías de producto** (donde se definen las estrategias de remoción).

---

## Ver las fechas de caducidad para lotes y números de serie

Para obtener una vista consolidada de caducidad:

1. Ir a `Inventario ‣ Productos ‣ Lotes/Números de serie`.
2. Quitar todos los **filtros automáticos** de la barra de búsqueda.
3. Hacer clic en **Agrupar por**.
4. Seleccionar **Agregar grupo personalizado**.
5. Elegir el parámetro **Fecha de caducidad**.
6. Pulsar **Aplicar**.

Con esto se obtiene un desglose de:

- Todos los productos perecederos.
- Sus **fechas de caducidad**.
- Los **números de lote** asociados.

---

### Alertas de caducidad

Para revisar únicamente productos con alerta de caducidad:

1. Ir a `Inventario ‣ Productos ‣ Lotes/Números de serie`.
2. Hacer clic sobre un **Lote/Número de serie** que contenga productos perecederos.
3. En el formulario:
   - Ir a la pestaña **Fechas**.
   - Ver/editar la **Fecha de caducidad**.

Si se cambia la fecha de caducidad a **hoy** (o una fecha pasada) y se guarda:

- El formulario del lote mostrará una **alerta de caducidad en rojo** en la parte superior.

Para filtrar todas las alertas:

1. Volver al tablero de `Lotes/Números de serie`.
2. Quitar todos los filtros de la barra de búsqueda.
3. Hacer clic en **Filtros**.
4. Elegir la opción **Alerta de caducidad**.

De esta forma se listan todos los lotes/números de serie que:

- Ya caducaron, o
- Están próximos a caducar según el **periodo de alerta** configurado.

---

## Notas sobre imágenes

La documentación oficial incluye capturas de pantalla para:

- Activar lotes y fechas de caducidad.
- Configurar el formulario de producto.
- Ver las fechas y alertas en lotes/números de serie.

Puedes consultar y descargar estas imágenes directamente desde la página oficial:

- [Fechas de vencimiento — Odoo 15](https://www.odoo.com/documentation/15.0/es/applications/inventory_and_mrp/inventory/management/lots_serial_numbers/expiration_dates.html)

Si necesitas tenerlas en local (por ejemplo en `imgs/`), puedes:

1. Abrir el enlace anterior en el navegador.
2. Inspeccionar los elementos de imagen para obtener las URLs (normalmente en `/documentation/15.0/_images/...`).
3. Guardarlas en tu proyecto y referenciarlas en Markdown, por ejemplo:

```markdown
![Configuración de fechas de caducidad](imgs/odoo-expiration-dates-config.png)
```

