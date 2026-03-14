# 🔔 Guía: Automatización de Reservas (MTO)

Esta es la "magia" de Odoo para agencias: cómo hacer que una venta genere automáticamente las órdenes de compra a tus proveedores.

---

## 1. El Concepto MTO (Bajo pedido)

La ruta **Obtener bajo pedido (MTO)** le dice a Odoo: *"No tengo esto en stock, cómpralo o resérvalo en cuanto lo venda"*.

![Odoo Purchase Automation](https://www.odoo.com/web/image/75217822-e421be00/purchase_mto.png)

---

## 2. Configuración Necesaria

Para que un hotel o tour se reserve solo, el producto debe tener estos 3 puntos en su ficha:

1.  **Proveedor**: En la pestaña **Compra**, añada el proveedor oficial y el precio acordado.
2.  **Ruta "Comprar"**: En la pestaña **Inventario**, marque ☑️ **Comprar**.
3.  **Ruta "Bajo pedido"**: En la pestaña **Inventario**, marque ☑️ **Obtener bajo pedido (MTO)**.

---

## 3. El Flujo en Vivo

1.  **Venta**: Confirmas una Orden de Venta que incluye el servicio (o un Kit que lo contiene).
2.  **Magia**: Al instante, Odoo busca si hay una Orden de Compra abierta para ese proveedor.
3.  **Resultado**: 
    *   Si no hay ninguna, crea una nueva **SdP (Solicitud de Presupuesto)** en borrador.
    *   Si ya tienes una abierta, añade el servicio como una línea nueva.

---

## 4. Ventajas para la Operatividad

*   **Cero Olvidos**: Nunca olvidarás reservar un hotel; el sistema lo hace por ti.
*   **Centralización**: Todas las reservas pendientes están en un solo lugar (**Compras > Solicitudes de Presupuesto**).
*   **Conciliación**: Puedes ver exactamente qué compra corresponde a qué venta.

---

> [!TIP]
> **Esencia Odoo LatAm:** En Compras, verá que los documentos nuevos aparecen como **"Solicitud de Presupuesto"**. Una vez que el proveedor le confirma la disponibilidad, usted le da a **Confirmar Orden** para convertirla en una **Orden de Compra**.

---
*Referencia: [Reabastecimiento bajo pedido en Odoo](https://www.odoo.com/documentation/17.0/es/applications/inventory_and_mrp/inventory/management/replenishment/strategies.html#make-to-order-mto)*
