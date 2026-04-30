# Pipeline CRM Wayki Trek

Este documento define las etapas del pipeline comercial en Odoo CRM, alineadas con el flujo operativo acordado para Wayki Trek.

## 1) Nuevo Lead (Captación Automática)

- **Descripción:** Aquí entran automáticamente todos los prospectos que completan el formulario en WordPress.
- **Acción:** El sistema mapea datos como el tour de interés, número de personas y nacionalidad.

## 2) Negociación / Cotización

- **Descripción:** En esta etapa, el equipo de ventas interviene manualmente para verificar la disponibilidad (especialmente para Camino Inca y Machu Picchu).
- **Acción:** Se envían propuestas comerciales usando plantillas de cotización en PDF de Odoo. Si no hay respuesta en 3 días, se activa el seguimiento de recordatorio.

## 3) Validación Interna (Vistos Buenos)

- **Descripción:** Etapa crítica donde se coordinan las áreas internas antes de formalizar el viaje.
- **Sub-pasos necesarios:**
  - **Operaciones:** Da el visto bueno sobre la viabilidad técnica del tour.
  - **Contabilidad:** Confirma la recepción del depósito inicial del 50%.

## 4) Reserva en Ejecución

- **Descripción:** Una vez obtenidos los vistos buenos, el área de Reservas procede a la compra de permisos, ingresos y espacios logísticos.
- **Acción:** Se comunica oficialmente al cliente que su espacio está asegurado.

## 5) Confirmado / Pago de Saldo

- **Descripción:** Oportunidades donde el servicio ya está reservado, pero se espera el 50% restante del pago (entre 15 y 8 días antes del viaje).
- **Acción:** Seguimiento administrativo para asegurar el cierre financiero antes de la salida.

## 6) Ganado / Post-Venta

- **Descripción:** El servicio se ha ejecutado con éxito.
- **Acción:** Se solicita feedback y se invita al cliente a dejar su testimonio en TripAdvisor.

---

## Orden recomendado en Odoo

1. Nuevo Lead (Captación Automática)
2. Negociación / Cotización
3. Validación Interna (Vistos Buenos)
4. Reserva en Ejecución
5. Confirmado / Pago de Saldo
6. Ganado / Post-Venta

## Nota de configuración

- Marcar **Ganado / Post-Venta** como etapa ganada (`is_won = true`) en Odoo CRM.
