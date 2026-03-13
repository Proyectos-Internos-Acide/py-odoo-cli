# 🚀 Guía: Flujo de CRM a Ventas (Odoo LatAm)

Esta guía explica el proceso desde que llega un interesado (Lead) hasta que confirmas la venta en una agencia de viajes.

---

## 1. Gestión de Oportunidades (CRM)

El CRM es donde centralizamos todas las consultas de los viajeros.

![CRM Pipeline](https://www.odoo.com/web/image/75217822-e421be00/crm_pipeline.png)

1.  **Crear Prospecto**: Vaya a **CRM > Oportunidades** y haga clic en **Nuevo**.
2.  **Calificación**: Arrastre la oportunidad a través de las etapas (Nuevo, Calificado, Propuesta, Ganado).
3.  **Actividades**: Use el icono de reloj para agendar llamadas o correos. Odoo le avisará cuando sea momento de contactar al cliente.

---

## 2. Creación de la Cotización (Presupuesto)

Una vez que el cliente muestra interés real, generamos la oferta de viaje.

1.  Dentro de la oportunidad, haga clic en el botón **Nuevo Presupuesto**.
2.  **Seleccionar Plantilla**: En el campo "Plantilla de presupuesto", elija su programa (ej. *Cusco Mágico*).
    *   *Nota:* Odoo cargará automáticamente el itinerario detallado.
3.  **Líneas del Pedido**: Verifique los servicios incluidos. Use **Secciones** para separar los días del viaje.

---

## 3. Envío y Firma Online

![Quotation Preview](https://erpsoftapp.com/wp-content/uploads/2021/04/odoo-sales-quotation-builder.png)

1.  Haga clic en **Enviar por correo**. El cliente recibirá un enlace a un portal web profesional.
2.  **Firma Online**: El cliente puede aceptar y firmar digitalmente desde su celular o computadora.
3.  **Confirmación**: Al firmar, el presupuesto se convierte automáticamente en una **Orden de Venta**.

---

## 4. Tip para la Agencia: Margen de Ganancia

Para ver cuánto está ganando por cada viajero:
1.  En la Orden de Venta, fíjese en la columna **Margen** (si está habilitada).
2.  Odoo resta el costo de los proveedores (Hoteles, Trenes) del precio de venta final para darle su utilidad bruta real.

---

> [!TIP]
> **Esencia Odoo LatAm:** En las versiones para Latinoamérica, verá que usamos el término **"Cotización"** en lugar de "Presupuesto" para que sea más natural al mercado regional.

---
*Referencia: [Documentación oficial de Ventas Odoo](https://www.odoo.com/documentation/17.0/es/applications/sales/sales.html)*
