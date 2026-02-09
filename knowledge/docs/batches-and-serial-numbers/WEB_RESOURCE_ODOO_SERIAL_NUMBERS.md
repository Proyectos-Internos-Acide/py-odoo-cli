---
title: Usar números de serie para rastrear productos en Odoo 15
source: https://www.odoo.com/documentation/15.0/es/applications/inventory_and_mrp/inventory/management/lots_serial_numbers/serial_numbers.html
---

# Usar números de serie para rastrear productos

Los **números de serie** son una de las dos maneras en las que se pueden identificar productos para rastrearlos con Odoo.  
Un **número de serie** es un identificador único que se asigna a los productos o artículos de forma incremental (o secuencial) para distinguirlos de otros productos y artículos.

Los números de serie pueden:

- Ser solo **numéricos**.
- Incluir **letras**.
- Incluir otros **símbolos tipográficos**.
- O una combinación de todos los anteriores.

Se asignan a **productos individuales** para poder identificar el **historial completo** de cada artículo a lo largo de la cadena de suministro.  
Esto es especialmente útil para fabricantes que ofrecen **servicio posventa** (garantías, reparaciones, soporte técnico, etc.).

> Referencia relacionada:
> - [Use lotes para gestionar grupos y productos](https://www.odoo.com/documentation/15.0/es/applications/inventory_and_mrp/inventory/management/lots_serial_numbers/lots.html)
> - [Diferencia entre lotes y números de serie](https://www.odoo.com/documentation/15.0/es/applications/inventory_and_mrp/inventory/management/lots_serial_numbers/differences.html)

---

## Activar lotes y números de serie

Para rastrear productos usando números de serie, primero se debe activar la función **Números de lote y de serie**:

1. Ir a la aplicación `Inventario ‣ Configuración ‣ Ajustes`.
2. Bajar a la sección **Trazabilidad**.
3. Marcar la casilla **Números de lote y de serie**.
4. Hacer clic en **Guardar**.

Esta configuración habilita el uso tanto de **lotes** como de **números de serie** en el inventario.

> En la documentación oficial se muestra una captura con el ajuste activado.

---

## Configurar el rastreo por número de serie en los productos

Una vez activados los **Números de lote y de serie**, se puede configurar que un producto se rastree por **número de serie único**.

Pasos:

1. Ir a `Inventario ‣ Productos ‣ Productos`.
2. Seleccionar el producto a rastrear.
3. Hacer clic en **Editar**.
4. Ir a la pestaña **Inventario**.
5. En la sección **Trazabilidad**, elegir la opción **Por número de serie único**.
6. Guardar los cambios (icono de nube o botón de guardar).

Con esto:

- El producto queda configurado para manejarse **unidad por unidad** con número de serie.
- Al recibir o fabricar, se podrá asignar o crear números de serie para ese producto.

> Advertencia: Si hay existencias sin número de serie/lote asignado, Odoo mostrará una ventana de **error de usuario** indicando que es necesario asignarlos mediante un **ajuste de inventario**.

### Crear nuevos números de serie para productos ya en existencias

Es posible crear números de serie nuevos para productos que ya están en stock y aún no tienen número de serie.

1. Ir a `Inventario ‣ Productos ‣ Números de lote/serie`.
2. Hacer clic en **Nuevo**.
3. Odoo genera automáticamente un valor en **Número de lote/serie** (puede editarse).
4. En el campo **Producto**, seleccionar el producto al que se le asignará este número.
5. Opcionalmente:
   - Ajustar la **Cantidad**.
   - Definir una **Referencia interna** única.
   - Asociar a un **Sitio web** específico (si aplica multi-sitio).
   - Añadir una **descripción** en la pestaña correspondiente.
6. Hacer clic en **Guardar**.

Luego:

- Volver a `Productos ‣ Productos`.
- Abrir el producto.
- Usar el botón inteligente **Número de lote/serie** para ver los números asignados.

---

## Gestionar números de serie en envíos y recepciones

Los números de serie se pueden asignar tanto en operaciones **entrantes** (compras/recepciones) como **salientes** (ventas/entregas).

### Gestionar números de serie en recepciones (bienes entrantes)

1. Ir a la aplicación **Compra** y crear una nueva **Solicitud de cotización**.
2. Completar:
   - **Proveedor**.
   - Productos en las líneas.
   - **Cantidad** de cada producto.
3. Hacer clic en **Confirmar orden** para convertirla en **Orden de compra**.
4. Pulsar el botón inteligente **Recepción** para abrir el albarán/recepción en almacén.

> Advertencia: Si se pulsa **Validar** sin asignar números de serie a productos que lo requieren, aparece una ventana de **Error de usuario** que obliga a ingresar lote/número de serie.

Para asignar los números:

1. En la recepción, ir a la pestaña **Operaciones**.
2. Hacer clic en el icono de **Opciones adicionales** (las cuatro líneas horizontales).
3. Se abre la ventana **Operaciones detalladas**.
4. En la parte inferior, usar la columna **Nombre del número de lote/de serie** para registrar los números.

Hay tres opciones:

#### Asignar números de serie manualmente

- Hacer clic en **Agregar una línea**.
- Definir la **Ubicación** donde se almacenará.
- Escribir el **Nombre del número de serie**.
- Indicar la **Cantidad hecha**.
- Repetir hasta cubrir la cantidad total del producto (campo **Demanda** / **Cantidad programada**).

#### Asignar números de serie de manera automática

Para muchos productos, Odoo puede generar números de serie de forma masiva:

1. En la ventana **Operaciones detalladas**, rellenar:
   - **Primer NS**: primer número de la secuencia.
   - **Cantidad de NS**: número total de números de serie a generar.
2. Hacer clic en **Asignar números de serie**.

Odoo creará las líneas necesarias y asignará los números secuenciales según la cantidad solicitada.

#### Copiar y pegar números de serie desde una hoja de cálculo

1. Preparar en una hoja de cálculo todos los números de serie recibidos del proveedor.
2. Copiar esa lista.
3. En la ventana **Operaciones detalladas**, pegar en la columna **Nombre del número de lote/serie**.
4. Odoo creará automáticamente una línea por cada número pegado.
5. Completar **Cantidades hechas** y **Ubicaciones** por línea.

> Truco: Para órdenes de compra con muchas unidades, el botón **Asignar números de serie** evita duplicar o reciclar números y mejora la trazabilidad.

Una vez asignados todos los números de serie:

1. Hacer clic en **Confirmar** en la ventana emergente.
2. Pulsar **Validar** en la recepción.
3. Se habilita el botón inteligente **Trazabilidad** para ver:
   - Documento de referencia.
   - Producto.
   - Lote/número de serie.
   - Movimientos asociados.

---

### Gestionar números de serie en órdenes de entrega (bienes salientes)

1. Ir a la aplicación **Ventas** y hacer clic en **Crear**.
2. Completar los datos de la cotización:
   - **Cliente**.
   - Productos en la pestaña **Líneas de la orden**.
   - **Cantidad** a vender.
3. Hacer clic en **Confirmar** para convertir la cotización en **Orden de venta**.
4. Pulsar el botón inteligente **Entrega** para abrir el albarán de salida en almacén.

En la entrega:

1. Hacer clic en el icono de **Opciones adicionales** en la pestaña **Operaciones**.
2. Se abre la ventana **Operaciones detalladas**.
3. Odoo suele proponer en automático números de serie ya reservados para cada línea.
4. Si se requiere cambiar un número:
   - Abrir el desplegable **Número de lote/serie**.
   - Elegir (o escribir) el número de serie deseado.
   - Ajustar las **Cantidades hechas**.
5. Confirmar la ventana emergente y luego pulsar **Validar** para registrar la entrega.

Tras validar:

- Aparece el botón inteligente **Trazabilidad**, donde se ve el reporte actualizado con:
  - Documento de referencia.
  - Producto.
  - Fecha.
  - Lote/número de serie.
  - Posibles referencias cruzadas con recepciones previas que compartan el mismo número de serie.

---

## Gestionar números de serie para distintos tipos de operaciones

Por defecto, Odoo se comporta así:

- En **recepciones (compras)**:
  - Se pueden **crear nuevos** números de serie.
  - No se pueden usar números de serie ya existentes por defecto.
- En **órdenes de entrega (ventas)**:
  - **No** se pueden crear nuevos números de serie.
  - Solo se pueden usar números de serie **existentes**.

Este comportamiento se puede ajustar por **tipo de operación**:

1. Ir a `Inventario ‣ Configuración ‣ Tipos de operaciones`.
2. Seleccionar el tipo de operación deseado.

Ejemplos:

- Tipo **Recepciones**:
  - Activar la opción **Utilizar números de lote o de serie existentes** en la sección **Números de lote/serie**.
- Tipo **Órdenes de entrega**:
  - Activar la opción **Crear nuevo** en la sección **Números de lote/serie** para permitir generar nuevos números en la salida.

Los cambios se guardan automáticamente (o se puede usar el icono de nube para guardar manualmente).

---

## Trazabilidad del número de serie

Los reportes de **trazabilidad** permiten ver el ciclo de vida completo de un producto:

- De dónde vino y **cuándo**.
- Dónde se **almacenó**.
- A quién y **cuándo** se entregó.

Para consultar esta información:

1. Ir a `Inventario ‣ Productos ‣ Números de serie/lote`.
2. Allí se visualiza el tablero con todos los números de lote y de serie.
3. Se puede expandir cada registro para ver:
   - Productos asociados.
   - Cantidades.
   - Movimientos.

Para agrupar por número de serie o lote:

1. Quitar los filtros automáticos de la barra de búsqueda (esquina superior derecha).
2. Hacer clic en **Agrupar por**.
3. Elegir **Agregar grupo personalizado**.
4. Seleccionar **Lote/Número de serie**.
5. Pulsar **Aplicar**.

De esta forma, se muestran todos los números de serie y de lote existentes, con las cantidades de productos que usan cada uno.  
Para números de serie **únicos** que no se reutilizan, debe existir **solo un producto por número de serie**.

> Truco: Al hacer clic sobre una línea de número de serie se abre su formulario, desde donde los botones inteligentes **Ubicación** y **Trazabilidad** permiten ver:
> - Todas las existencias actuales que usan ese número.
> - Todas las operaciones en las que se ha utilizado.

---

## Referencia de imágenes

La documentación oficial incluye capturas de pantalla para cada paso.  
Aunque en esta exportación no se listan explícitamente todas las URLs de las imágenes, puedes consultarlas y descargarlas directamente desde la página oficial:

- [Usar números de serie para rastrear productos — Odoo 15](https://www.odoo.com/documentation/15.0/es/applications/inventory_and_mrp/inventory/management/lots_serial_numbers/serial_numbers.html)

Si necesitas alinearlo con otros recursos (como los de SUNAT), puedes:

1. Abrir la página anterior en el navegador.
2. Inspeccionar las imágenes con las herramientas de desarrollador.
3. Copiar las URLs (normalmente bajo `/documentation/15.0/_images/...`).
4. Guardarlas en una carpeta local (por ejemplo, `imgs/`) y referenciarlas así:

```markdown
![Título descriptivo](imgs/odoo-serial-numbers-paso-1.png)
```

