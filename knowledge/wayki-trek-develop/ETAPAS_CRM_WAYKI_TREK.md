# Pipeline CRM Wayki Trek

Este documento define las etapas del pipeline comercial en Odoo CRM, actualizadas según la configuración real en producción.

## 1) Nuevo Lead (Captación Automática) [ID: 5]
- **Descripción:** Entrada automática de todos los prospectos desde formularios web.
- **Acción:** Mapeo de datos (tour, personas, nacionalidad).

## 2) Primer mensaje [ID: 11]
- **Descripción:** Se ha enviado el primer mensaje automático o manual al cliente por WhatsApp.
- **Acción:** Esperar la respuesta inicial del cliente.

## 3) Seguimiento [ID: 12]
- **Descripción:** Lead que requiere insistencia. (La automatización traslada aquí a los leads de "Primer mensaje" si no responden en 3 días).
- **Acción:** Retomar contacto o descartar si no hay interés.

## 4) Negociación / Cotización [ID: 6]
- **Descripción:** Interacción activa, se envían itinerarios y cotizaciones.
- **Acción:** Aclarar dudas y cerrar el servicio.

## 5) Confirmado / Pago de Saldo [ID: 9]
- **Descripción:** El viaje está reservado, pendiente del pago final antes de la salida.
- **Acción:** Seguimiento administrativo para asegurar el cobro.

## 6) Convertido en Cliente / Post-Venta [ID: 10] (Ganado)
- **Descripción:** Cliente con servicio completado o cerrado exitosamente.
- **Acción:** Seguimiento post-tour, solicitud de reseñas (TripAdvisor).

---

## Orden actual en Odoo

1. Nuevo Lead (Captación Automática)
2. Primer mensaje
3. Seguimiento
4. Negociación / Cotización
5. Confirmado / Pago de Saldo
6. Convertido en Cliente / Post-Venta

## Nota de configuración
- La etapa **Convertido en Cliente / Post-Venta** es la única marcada como ganada (`is_won = true`).
