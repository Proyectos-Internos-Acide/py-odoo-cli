# Auditoría Wayki Trek — desde 25/09/2026

- Fecha del informe: 2026-11-02
- BD: `wayki-trek` (`https://wayki-trek.odoo.com`, SaaS 19.3 Enterprise)
- Rango: `create_date >= 2026-09-25` **o** `write_date >= 2026-09-25` (creados + tocados en el rango)
- Método: XML-RPC vía `py-odoo-cli`. Sin `auditlog` instalado, los borrados no dejan rastro.

## Resumen

Casi sin actividad desde el 25/09. Todo lo del rango lo hizo **Amaru Cusi** (uid 2), salvo 2 toques de OdooBot (automatizaciones) y 2 mensajes de Américo. **Sales (Américo) y Coordinator (Carlos) no crearon ni modificaron nada** en el rango; Leo solo ingresó, sin registros.

| Modelo | Creados | Tocados (anteriores) |
|---|---|---|
| Contactos | 4 (Amaru) | 0 |
| Leads | 6 (Amaru) | 1 (OdooBot, automatización) |
| Cotizaciones | 0 | 0 |
| Facturas | 0 | 0 |
| Productos | 0 | 0 |
| Tareas | 0 | 0 |
| Mensajes | 27 (Amaru 19, OdooBot 6, Américo 2) | — |
| Parámetros | 0 funcionales (solo telemetría) | — |
| Módulos | 0 instalados/actualizados | — |

## Detalle por usuario (en rango)

- **Amaru Cusi (network@waykitrek.net)**: 4 contactos + 6 leads creados; 19 mensajes. Única actividad humana del período.
- **Leo Cusi**: accesos 24/10 y 02/11, sin crear ni modificar registros.
- **Américo Aguilar (sales)**: último acceso 28/09; solo 2 mensajes automáticos suyos en el rango. Nada creado/modificado.
- **Carlos Fernandez (coordinator)**: sin accesos ni actividad desde el 12/08. Cero en el rango.
- **OdooBot**: 1 lead tocado (Olivia Glarner, 26/09, automatización) + 6 mensajes de sistema.

## Contactos creados (4)

| fecha | contacto | email |
|---|---|---|
| 26/09 16:41 | Arabella Graves | bellagraves1236@gmail.com |
| 03/10 09:50 | Francisco Porras | fco.j.porras@gmail.com |
| 07/10 17:47 | Rebeca Stryde | rebeca@strude.com (posible typo: "strude") |
| 07/10 17:58 | rebeca stryde | rebeca@stryde.com |

**Duplicado probable**: Rebeca Stryde aparece 2 veces con emails casi idénticos (`strude.com` vs `stryde.com`). Recomendación: fusionar.

## Leads creados (6, todos asignados a Amaru)

| fecha | lead | etapa actual |
|---|---|---|
| 26/09 | [WEB] Arabella Graves - Inca Trail 5 Days - Solo - 1 Pax | Seguimiento |
| 03/10 | [WEB] Francisco Porras - Inca Trail 4 Days - 2 Pax | Nuevo Lead (sin mover desde su creación) |
| 07/10 | [WEB] Rebeca Stryde - Peru 6 Days - 9 Pax | Nuevo Lead |
| 07/10 | [WEB] Rebeca Stryde - City Tour - 8 Pax | Nuevo Lead |
| 07/10 | [WEB] rebeca stryde - Peru 6 Days - 7 Pax (duplicado, 2 registros idénticos) | Nuevo Lead |

**Riesgo comercial**: 5 de 6 leads siguen en "Nuevo Lead (Captación Automática)" sin gestión un mes después. Rebeca envió 4 solicitudes el 07/10 (posible cliente caliente duplicado por reintentos web).

## Chatter (27 mensajes)

22 en `crm.lead` (notificaciones/comentarios de creación de los leads de arriba) y 5 en `res.partner`. Nada en ventas ni facturas, coherente con cero movimiento en esos modelos.

## Configuración y módulos

- **0 módulos** instalados, actualizados o desinstalados desde el 25/09.
- **0 cambios funcionales** de parámetros; solo `hash_previous_ping` (telemetría automática, 23/10).

## Accesos en el rango

| fecha | usuario |
|---|---|
| 28/09 | Américo Aguilar (último suyo) |
| 23/10 | Amaru Cusi |
| 24/10 | Leo Cusi |
| 02/11 | Leo Cusi + Amaru Cusi (varias) |

Nota: los accesos de Amaru del 02/11 incluyen esta propia auditoría (cada conexión XML-RPC genera entrada en `res.users.log`).

## Conclusiones

1. La operación está detenida desde fines de septiembre: sin cotizaciones ni facturas en 5+ semanas.
2. Hay 5 leads web sin atender (uno con 4 solicitudes). Prioridad: asignar y mover de etapa.
3. Fusionar el contacto duplicado de Rebeca Stryde.
4. Revisar con Sales/Coordinator su inactividad en el sistema (¿venden por otro canal?).
