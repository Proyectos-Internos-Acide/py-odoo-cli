# Guía Manual: Lotes y Flujo de Compra (Odoo v19)

Esta guía explica cómo gestionar lotes y realizar el proceso de compra manualmente en Odoo SaaS v19.

## 1. Activar Gestión de Lotes y Números de Serie

1. Vaya a **Inventario > Configuración > Ajustes**.
2. Desplácese hasta la sección **Trazabilidad**.
3. Marque la casilla **Lotes y números de serie**.
4. Haga clic en **Guardar**.

## 2. Configurar un Producto para usar Lotes

Cuando creas o editas un producto (ej. Cemento), debes indicar cómo quieres rastrearlo:

1. Vaya a **Inventario > Productos > Productos**.
2. Abra el producto deseado.
3. En la pestaña **Inventario**, busque la sección **Trazabilidad**.
4. En el campo **Seguimiento**, seleccione **Por Lotes**.
5. Guarde los cambios.

## 3. Flujo de Compra con Recepción de Lotes

### Paso A: Crear Orden de Compra (PO)
1. Vaya a **Compra > Órdenes de compra > Nuevo**.
2. Seleccione un **Proveedor**.
3. Añada el producto que configuró con lotes.
4. Haga clic en **Confirmar orden**.

### Paso B: Recibir Mercadería y Asignar Lote
Al confirmar la compra, se genera una **Recepción** (Picking) en Inventario.

1. Haga clic en el botón inteligente **Recepción** (o vaya a Inventario > Por recibir).
2. Verá una columna llamada **Lote/Número de serie**.
3. **IMPORTANTE**: No podrá validar la recepción sin asignar el lote.
4. Haga clic en el icono de "Detalle" (líneas con menú) a la derecha de la línea del producto.
5. En la ventana emergente, haga clic en **Añadir línea**.
6. Escriba el nombre de su lote personalizado (ej: `SERIE-AQP-001`).
7. Indique la cantidad que pertenece a ese lote.
8. Haga clic en **Confirmar**.
9. Finalmente, haga clic en **Validar** en la recepción.

## Referencias Visuales (Docs Oficiales)

- [Configuración de Lotes](https://www.odoo.com/documentation/17.0/es/applications/inventory_and_mrp/inventory/product_management/product_tracking/lots.html)
- [Uso de números de serie](https://www.odoo.com/documentation/17.0/es/applications/inventory_and_mrp/inventory/product_management/product_tracking/serial_numbers.html)

> **Tip Pro:** Puedes automatizar la generación de lotes configurando "Secuencias" en Odoo para que no tengas que escribirlos manualmente.
