# Guía: Traslados Internos y Alertas de Inventario (Odoo v19)

Esta guía detalla los pasos para mover stock entre tus ubicaciones configuradas (AQP, MOC, PUN) y cómo configurar alertas para no quedarte sin mercadería.

---

## 1. Traslados Internos (Internal Transfers)

Los traslados internos se utilizan para mover productos entre tus almacenes o ubicaciones sin que medie una compra o venta.

### Pasos para realizar un traslado:
1.  **Navegación**: Vaya a **Inventario > Operaciones > Interno**.
2.  **Crear**: Haga clic en el botón **Nuevo**.
3.  **Tipo de Operación**: Seleccione **Traslados internos** (esto filtrará las ubicaciones de origen/destino para que sean internas).
4.  **Ubicaciones**:
    *   **Ubicación de origen**: Por ejemplo, `AQP/Stock`.
    *   **Ubicación de destino**: Por ejemplo, `MOC/Stock`.
5.  **Añadir Productos**: En la pestaña **Operaciones**, haga clic en **Añadir línea** y seleccione los productos y cantidades.
6.  **Validar**: Haga clic en **Marcar como pendiente** y luego en **Validar** cuando la mercadería haya sido movida físicamente.

> [!TIP]
> Si el producto tiene **lotes**, Odoo te pedirá seleccionar específicamente qué lote estás trasladando en el icono de "detalles" de la línea.

---

## 2. Alertas de Inventario (Reglas de Reabastecimiento)

Odoo no usa "alertas" pasivas, sino que utiliza **Reglas de Reabastecimiento** que actúan como alertas proactivas para generar órdenes de compra automáticamente.

### Cómo configurar una alerta (Regla de Stock Mínimo):
1.  Vaya a **Inventario > Productos > Productos** y elija un producto (ej: Cemento).
2.  Haga clic en el botón inteligente **Reglas de reabastecimiento** (arriba a la derecha).
3.  Haga clic en **Nuevo** y configure:
    *   **Ubicación**: Donde quieres vigilar el stock (ej: `AQP/Stock`).
    *   **Cantidad mínima**: El punto de alerta. Si el stock cae por debajo de esto, Odoo "se queja".
    *   **Cantidad máxima**: La cantidad a la que Odoo intentará llegar al reabastecer.
4.  **Ruta**: Asegúrate que diga **Comprar**.

### Visualizar productos en Alerta:
Vaya a **Inventario > Operaciones > Reabastecimiento**. Aquí aparecerán todos los productos que están por debajo de su mínimo, resaltados para que tomes acción.

---

## 3. Notas Extras (Alertas Visuales)

Si quieres alertas visuales en órdenes de venta o compra ("¡Cuidado, este producto está dañado!"), puedes usar **Advertencias**:
1.  En el formulario del producto, ve a la pestaña **Ventas** o **Compra**.
2.  Busca el campo **Advertencia** (Warning).
3.  Selecciona **Advertencia** y escribe el mensaje. Este mensaje saltará como un "pop-up" cuando alguien intente vender o comprar ese producto.

---

## Referencias Oficiales
- [Traslados Internos](https://www.odoo.com/documentation/17.0/es/applications/inventory_and_mrp/inventory/routes/strategies/internal_transfers.html)
- [Reglas de Reabastecimiento](https://www.odoo.com/documentation/17.0/es/applications/inventory_and_mrp/inventory/management/replenishment/reordering_rules.html)

> [!NOTE]
> Las capturas de pantalla de la v19 siguen la misma lógica visual de la v17 citada en los links anteriores, pero con un diseño más minimalista y rápido.
