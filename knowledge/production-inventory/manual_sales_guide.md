# Guía Manual: Flujo de Ventas y Facturación (Odoo v19)

Esta guía explica el ciclo de vida de una venta en Odoo, desde el primer contacto con el cliente hasta la emisión de la factura (sin incluir SUNAT por ahora).

---

## 1. Crear una Cotización (Quotation)

La **Cotización** es el documento borrador donde le ofreces productos a tu cliente.

1.  Vaya a **Ventas > Ordenes > Cotizaciones**.
2.  Haga clic en **Nuevo**.
3.  Seleccione un **Cliente** (o cree uno nuevo).
4.  En la pestaña **Líneas del pedido**, haga clic en **Añadir un producto**.
5.  Seleccione el producto (ej. Cemento), indique la cantidad y el precio.
6.  Haga clic en **Enviar por correo electrónico** para que el cliente la reciba o simplemente **Guarde**.

---

## 2. Confirmar la Venta (Orden de Venta)

Cuando el cliente acepta el presupuesto, la cotización se convierte en una **Orden de Venta**.

1.  Abra la cotización que creó.
2.  Haga clic en el botón **Confirmar**.
3.  El estado cambiará de "Cotización" a **"Orden de venta"**.
    *   *Nota:* En este momento Odoo reserva el stock en tu almacén pero aún no ha salido físicamente.

---

## 3. Entrega de Mercadería (Delivery)

Al confirmar la venta, Odoo genera automáticamente una **Entrega**.

1.  Haga clic en el botón inteligente **Entrega** (icono de camión arriba a la derecha) o vaya a **Inventario > Operaciones > Transferencias**.
2.  Verá la lista de productos a enviar.
3.  **Si usa Lotes**: Debe hacer clic en el botón de "Detalles" (líneas con menú) y seleccionar de qué lote está sacando el producto.
4.  Haga clic en **Validar**. El stock ahora ha salido oficialmente de tu inventario.

---

## 4. Facturación (Invoicing)

Una vez entregado (o según tu política), puedes generar el cobro.

1.  Vuelva a la **Orden de Venta**.
2.  Haga clic en el botón **Crear factura**.
3.  Seleccione **Factura regular** y haga clic en **Crear y ver factura**.
4.  Odoo generará una factura en estado **Borrador**.
5.  Revise los datos y haga clic en **Confirmar**.
    *   La factura pasará a estado **Publicado/Asentado**.
    *   *Nota:* En esta etapa, la factura es interna. No se enviará a SUNAT hasta que actives el módulo correspondiente más adelante.

---

## Referencias Oficiales
- [Flujo de Ventas](https://www.odoo.com/documentation/17.0/es/applications/sales/sales/send_quotations/get_started.html)
- [Gestión de Facturas](https://www.odoo.com/documentation/17.0/es/applications/finance/accounting/customer_invoices/overview.html)

> [!IMPORTANT]
> Recuerda que para facturar productos almacenables (como el Cemento), usualmente la política de Odoo está configurada para "Facturar lo entregado". Esto significa que primero debes validar la **Entrega** (Paso 3) antes de que Odoo te permita crear la **Factura** (Paso 4).
