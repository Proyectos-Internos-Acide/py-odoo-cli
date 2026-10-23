# Relación de comprobantes electrónicos — TEXTILES Y CONFECCIONES ATLAS E.I.R.L.

- **Empresa:** TEXTILES Y CONFECCIONES ATLAS E.I.R.L.
- **RUC:** 20558074427
- **Fecha de corte:** 2026-10-23
- **Fuente:** `account.move` en Odoo (instancia conectada, `move_type` venta: `out_invoice`, `out_refund`)
- **Moneda:** PEN
- **Alcance:** solo comprobantes de venta con tipo de documento LATAM informado. No incluye asientos contables internos (`entry`) ni comprobantes de compra.

## Resumen por tipo de comprobante

| Tipo | Código SUNAT | Total | Enviados a SUNAT (`sent`) | Pendientes de envío (`to_send`) |
|---|---|---:|---:|---:|
| Factura | 01 | 2 | 2 | 0 |
| Boleta | 03 | 4 | 4 | 0 |
| Nota de Crédito (Factura) | 07 | 2 | 1 | 1 |
| Nota de Crédito (Boleta) | 07 | 4 | 1 | 3 |
| Nota de Débito | 08 | 0 | 0 | 0 |
| **Total** | — | **12** | **8** | **4** |

## Resumen con montos (PEN)

| Tipo | Total (PEN) | Enviado (PEN) | Pendiente (PEN) | IGV total (PEN) | Base total (PEN) |
|---|---:|---:|---:|---:|---:|
| Factura (01) | 2.00 | 2.00 | 0.00 | 0.30 | 1.70 |
| Boleta (03) | 17.00 | 17.00 | 0.00 | 2.59 | 14.41 |
| Nota de Crédito Factura (07) | 2.00 | 1.00 | 1.00 | 0.30 | 1.70 |
| Nota de Crédito Boleta (07) | 17.00 | 1.00 | 16.00 | 2.59 | 14.41 |
| **Total general** | **38.00** | **21.00** | **17.00** | **5.78** | **32.22** |

Detalle: enviado = `sent` (8 compr., S/ 21.00); pendiente = `to_send` (4 NC, S/ 17.00).

## Resumen por estado

| Estado Odoo / EDI | Cantidad |
|---|---:|
| `posted` / `sent` (enviado a SUNAT) | 8 |
| `posted` / `to_send` (registrado, pendiente de envío) | 4 |
| Borrador / cancelado | 0 |

Todos los comprobantes listados están en estado contable `posted` (registrado/publicado).

## Comprobantes enviados a SUNAT (`l10n_pe_edi_status = sent`) — 8

| N.° | Tipo SUNAT | Fecha | Cliente | Doc. identidad | Total (PEN) | IGV (PEN) | Base (PEN) | Estado pago | Observación |
|---|---|---|---|---:|---:|---:|---|---|---|
| F101-00000005 | 01 Factura | 2026-09-25 | COLEGIO MÉDICO DEL PERÚ | RUC 20139589638 | 1.00 | 0.15 | 0.85 | reversed | Anulada con FC01-00000001 |
| B101-00000005 | 03 Boleta | 2026-09-25 | CLIENTE BOLETA PRUEBA | DNI 72190044 | 1.00 | 0.15 | 0.85 | reversed | Anulada con BC01-00000001 |
| FC01-00000001 | 07 Nota de Crédito (Factura) | 2026-09-25 | COLEGIO MÉDICO DEL PERÚ | RUC 20139589638 | 1.00 | 0.15 | 0.85 | paid | Revierte a F101-00000005 |
| BC01-00000001 | 07 Nota de Crédito (Boleta) | 2026-09-25 | CLIENTE BOLETA PRUEBA | DNI 72190044 | 1.00 | 0.15 | 0.85 | paid | Revierte a B101-00000005 |
| B101-00000006 | 03 Boleta | 2026-09-28 | CLIENTE BOLETA PRUEBA | DNI 72190044 | 1.00 | 0.15 | 0.85 | paid | — |
| B101-00000007 | 03 Boleta | 2026-10-06 | Consumidor Final | DNI 00000000 | 11.00 | 1.68 | 9.32 | paid | — |
| B101-00000008 | 03 Boleta | 2026-10-06 | Consumidor Final | DNI 00000000 | 4.00 | 0.61 | 3.39 | paid | — |
| F101-00000006 | 01 Factura | 2026-10-06 | COLEGIO MÉDICO DEL PERÚ | RUC 20139589638 | 1.00 | 0.15 | 0.85 | paid | — |

## Comprobantes pendientes de envío (`l10n_pe_edi_status = to_send`) — 4

| N.° | Tipo SUNAT | Fecha | Cliente | Total (PEN) | IGV (PEN) | Base (PEN) | Revierte a | Estado pago |
|---|---|---|---|---:|---:|---:|---|---|
| BC01-00000002 | 07 Nota de Crédito (Boleta) | 2026-09-28 | CLIENTE BOLETA PRUEBA | 1.00 | 0.15 | 0.85 | B101-00000006 | in_payment |
| BC01-00000003 | 07 Nota de Crédito (Boleta) | 2026-10-06 | Consumidor Final | 11.00 | 1.68 | 9.32 | B101-00000007 | in_payment |
| BC01-00000004 | 07 Nota de Crédito (Boleta) | 2026-10-06 | Consumidor Final | 4.00 | 0.61 | 3.39 | B101-00000008 | in_payment |
| FC01-00000002 | 07 Nota de Crédito (Factura) | 2026-10-06 | COLEGIO MÉDICO DEL PERÚ | 1.00 | 0.15 | 0.85 | F101-00000006 | in_payment |
| **Subtotal pendiente** | — | — | — | **17.00** | **2.59** | **14.41** | — | — |

## Incidencia de envío OSE — 2026-10-23

- **Error registrado en Odoo** (`BC01-00000002`, campo `l10n_pe_edi_warnings`):
  `1079|Solo puede enviar el comprobante en un resumen diario - Detalle: ... Presentacion fuera de fecha (5 días)`
- **Causa:** envío individual fuera de plazo. La norma (RS N.° 097-2012 modificada por RS N.° 114-2019, art. 12 y art. 21 / art. 15.2 y 23 para OSE) establece:
  - Boleta y nota vinculada (serie B), por ejemplar: hasta **5 días calendario** desde el día siguiente a la emisión. Vencido ese plazo, **solo resumen diario**.
  - Resumen diario de boletas/notas: hasta el **7.º día calendario** siguiente a la emisión.
  - Factura y nota vinculada: hasta **7 días calendario** desde el día siguiente a la emisión.
- **Situación al 2026-10-23:**

| N.° | Fecha | Días transcurridos | Plazo individual | Plazo resumen | Estado |
|---|---|---:|---|---|---|
| BC01-00000002 | 2026-09-28 | 25 | vencido (5 d) | vencido (7 d) | error 1079 confirmado en Odoo |
| BC01-00000003 | 2026-10-06 | 17 | vencido (5 d) | vencido (7 d) | pendiente, mismo riesgo |
| BC01-00000004 | 2026-10-06 | 17 | vencido (5 d) | vencido (7 d) | pendiente, mismo riesgo |
| FC01-00000002 | 2026-10-06 | 17 | vencido (7 d, factura) | no aplica resumen | pendiente, pierde calidad electrónica si no se remitió a tiempo |

- **Qué no reintentar:** el envío individual de esas 3 NC de boleta seguirá devolviendo 1079. No es un error de conexión ni de XML.
- **Vías a definir:** resumen diario rectificatorio/extemporáneo si el sistema lo permite, o tratamiento contable-tributario del comprobante vencido; en el caso de la NC de factura fuera de plazo, la norma prevé pérdida de calidad electrónica. Requiere decisión tributaria con la documentación de origen.

## Notas de débito

Sin registros de Nota de Débito (códigos 08) en el periodo consultado.

## Notas

- El campo usado para envío a SUNAT es `l10n_pe_edi_status`: `sent` = enviado, `to_send` = pendiente de envío (flujo asincrónico por cron o botón "Enviar ahora").
- Las 4 notas de crédito pendientes mantienen a sus comprobantes de origen con montos aún no conciliados a saldo cero en SUNAT hasta completar el envío.
- Los importes de las notas de crédito se muestran en valor absoluto según `amount_total` de Odoo; contablemente extornan el débito fiscal y el ingreso del documento original.
