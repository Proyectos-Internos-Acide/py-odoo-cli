# Reporte de Facturación Electrónica SUNAT en Odoo

> [!NOTE]
> **Objetivo del Documento:** Consolidar exclusivamente el estado de transmisión tributaria ante **SUNAT** de todos los comprobantes de pago (Facturas, Boletas de Venta, Notas de Crédito y Notas de Débito) gestionados en el sistema Odoo para entrega a la empresa destino.

### Ficha de Identificación Tributaria
* **Empresa Emisora:** CM LINE E.I.R.L.
* **RUC:** `20608453271`
* **Domicilio Fiscal:** Avenida PACIFICO MZA. 32, LOTE. 5B, P.J. MIGUEL, Arequipa, Perú
* **Sistema de Emisión Electrónica:** SEE - Odoo Enterprise (Facturación Electrónica Perú UBL 2.1)
* **Mecanismo de Envío:** Conexión Directa a SUNAT (Web Services SOAP)
* **Fecha del Informe:** 21 de Octubre de 2026

---

## 1. Resumen Ejecutivo de Transmisión a SUNAT

| Estado ante SUNAT | Total Comprobantes | Facturas (01) | Boletas (03) | Notas de Crédito (07) | Notas de Débito (08) | Importe Total (S/) |
| :--- | :---: | :---: | :---: | :---: | :---: | -: |
| ✅ **Aceptados por SUNAT (con CDR Oficial)** | **8** | 1 | 4 | 3 | 0 | S/ 509.76 |
| ⏳ **Pendientes de Envío a SUNAT (`to_send`)** | **0** | 0 | 0 | 0 | 0 | S/ 0.00 |
| 🚫 **No Enviados (Cancelados / Borrador)** | **4** | 3 | 1 | 0 | 0 | S/ 413.43 |
| **TOTAL GLOBAL REGISTRADO** | **12** | **4** | **5** | **3** | **0** | **S/ 923.19** |

---

## 2. Comprobantes Transmitidos y ACEPTADOS por SUNAT (Con CDR Oficial)

Los siguientes comprobantes fueron transmitidos electrónicamente mediante Web Services a SUNAT, validados por la entidad tributaria y cuentan con su respectiva **Constancia de Recepción (CDR) con Código de Respuesta `0` (Aceptado)** y firma digital de SUNAT:

| Tipo Comprobante | Serie y Número | Fecha Emisión | Doc. Cliente | Cliente / Razón Social | Total (S/) | Estado SUNAT | Código SUNAT | Respuesta Oficial SUNAT en CDR | Archivo ZIP / CDR |
| :--- | :--- | :-: | :--- | :--- | -: | :---: | :-: | :--- | :--- |
| (03) Boleta | `BOL-00000001` | 2026-10-02 | DNI 00000000 | Consumidor Final | **151.04** | ✅ Aceptado | `0` | *La Boleta numero BBOL-00000001, ha sido aceptada* | `20608453271-03-BBOL-00000001.zip` |
| (03) Boleta | `BOL-00000002` | 2026-10-04 | DNI 00000000 | Consumidor Final | **1.18** | ✅ Aceptado | `0` | *La Boleta numero BBOL-00000002, ha sido aceptada* | `20608453271-03-BBOL-00000002.zip` |
| (03) Boleta | `BOL-00000003` | 2026-10-04 | DNI 72190044 | Roger Prueba | **1.18** | ✅ Aceptado | `0` | *La Boleta numero BBOL-00000003, ha sido aceptada* | `20608453271-03-BBOL-00000003.zip` |
| (07) Nota de Crédito Boleta | `CNE-00000001` | 2026-10-04 | DNI 72190044 | Roger Prueba | **1.18** | ✅ Aceptado | `0` | *La Nota de credito numero BCNE-00000001, ha sido aceptada* | `20608453271-07-BCNE-00000001.zip` |
| (07) Nota de Crédito Boleta | `CNE-00000002` | 2026-10-04 | DNI 00000000 | Consumidor Final | **1.18** | ✅ Aceptado | `0` | *La Nota de credito numero BCNE-00000002, ha sido aceptada* | `20608453271-07-BCNE-00000002.zip` |
| (03) Boleta | `BOL-00000004` | 2026-10-05 | DNI 00000000 | Consumidor Final | **118.00** | ✅ Aceptado | `0` | *La Boleta numero BBOL-00000004, ha sido aceptada* | `20608453271-03-BBOL-00000004.zip` |
| (07) Nota de Crédito Boleta | `CNE-00000003` | 2026-10-05 | DNI 00000000 | Consumidor Final | **118.00** | ✅ Aceptado | `0` | *La Nota de credito numero BCNE-00000003, ha sido aceptada* | `20608453271-07-BCNE-00000003.zip` |
| (01) Factura | `FFI-00000002` | 2026-10-05 | RUC 10047257242 | MAMANI ROQUE ANASTACIA | **118.00** | ✅ Aceptado | `0` | *La Factura numero FFFI-00000002, ha sido aceptada* | `20608453271-01-FFFI-00000002.zip` |

---

## 3. Comprobantes PENDIENTES de Envío a SUNAT (Estado: `Por Enviar`)

> [!TIP]
> **Al Día ante SUNAT:** No existen comprobantes pendientes de envío. La cola de transmisión electrónica se encuentra en **0 comprobantes**.

---

## 4. Detalle de Notas de Crédito Aceptadas por SUNAT (Anulación de Comprobantes)

Se emitieron y validaron ante SUNAT **3 Notas de Crédito Electrónicas (Tipo 07)** con motivo reglamentario **`01 - Anulación de la operación`**, formalizando la reversión tributaria de las boletas indicadas:

| N° Nota Crédito | Fecha | Cliente | Comprobante SUNAT Anulado | Total Revertido (S/) | Código CDR | Respuesta Oficial SUNAT |
| :--- | :-: | :--- | :--- | -: | :-: | :--- |
| `CNE-00000001` | 2026-10-04 | Roger Prueba (DNI 72190044) | `B BOL-00000003 (CM LINE - 000002)` | **-1.18** | `0` | *La Nota de credito numero BCNE-00000001, ha sido aceptada* |
| `CNE-00000002` | 2026-10-04 | Consumidor Final (DNI 00000000) | `B BOL-00000002 (CM LINE - 000001)` | **-1.18** | `0` | *La Nota de credito numero BCNE-00000002, ha sido aceptada* |
| `CNE-00000003` | 2026-10-05 | Consumidor Final (DNI 00000000) | `B BOL-00000004 (CM LINE - 000005)` | **-118.00** | `0` | *La Nota de credito numero BCNE-00000003, ha sido aceptada* |

---

## 5. Notas de Débito Electrónicas (Tipo 08)

> [!NOTE]
> **Sin Registros:** A la fecha de este informe, **NO se han emitido Notas de Débito ante SUNAT**. No existieron penalidades, intereses moratorios ni conceptos adicionales que requirieran la generación de este tipo de comprobante.

---

## 6. Comprobantes No Transmitidos a SUNAT (Descartados / Pruebas Internas)

Comprobantes que no fueron transmitidos a SUNAT por corresponder a pruebas preliminares de numeración o documentos en edición:

| Comprobante | Tipo | Cliente | Total (S/) | Condición | Motivo por el que no se envió a SUNAT |
| :--- | :--- | :--- | -: | :--- | :--- |
| `FFI-00000001` | (01) Factura | MAMANI ROQUE ANASTACIA | S/ 1.18 | CANCEL | Comprobante de prueba cancelado antes de enviar |
| `F001-00000001` | (01) Factura | MAMANI ROQUE ANASTACIA | S/ 1.00 | CANCEL | Comprobante de prueba cancelado antes de enviar |
| `B001-00000001` | (03) Boleta | Roger Prueba | S/ 1.18 | CANCEL | Comprobante de prueba cancelado antes de enviar |
| `Borrador` | (01) Factura | Panadería La Espiga S.A.C. | S/ 410.07 | DRAFT | Comprobante en borrador aún no confirmado |

---
*Informe oficial de facturación electrónica SUNAT generado a partir de los registros UBL / EDI de Odoo Enterprise.*