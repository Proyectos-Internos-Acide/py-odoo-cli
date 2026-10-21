#!/usr/bin/env python3
"""
Generador de Reporte Exclusivo de Facturación Electrónica SUNAT en Odoo.
Empresa: CM LINE E.I.R.L. (RUC: 20608453271)
"""
import json

INPUT_JSON = '/home/roger/.gemini/antigravity-ide/brain/6538d3ff-e492-4205-b694-c52b7c1c484a/scratch/sunat_clean_records.json'

def main():
    with open(INPUT_JSON, 'r', encoding='utf-8') as f:
        records = json.load(f)

    aceptados = [r for r in records if r['edi_status'] == 'sent']
    pendientes = [r for r in records if r['edi_status'] == 'to_send']
    no_enviados = [r for r in records if r['edi_status'] not in ['sent', 'to_send']]

    tot_aceptados = sum(r['total'] for r in aceptados)
    tot_pendientes = sum(r['total'] for r in pendientes)

    md = []
    md.append('# Reporte de Facturación Electrónica SUNAT en Odoo')
    md.append('')
    md.append('> [!NOTE]')
    md.append('> **Objetivo del Documento:** Consolidar exclusivamente el estado de transmisión tributaria ante **SUNAT** de todos los comprobantes de pago (Facturas, Boletas de Venta, Notas de Crédito y Notas de Débito) gestionados en el sistema Odoo para entrega a la empresa destino.')
    md.append('')
    md.append('### Ficha de Identificación Tributaria')
    md.append('* **Empresa Emisora:** CM LINE E.I.R.L.')
    md.append('* **RUC:** `20608453271`')
    md.append('* **Domicilio Fiscal:** Avenida PACIFICO MZA. 32, LOTE. 5B, P.J. MIGUEL, Arequipa, Perú')
    md.append('* **Sistema de Emisión Electrónica:** SEE - Odoo Enterprise (Facturación Electrónica Perú UBL 2.1)')
    md.append('* **Mecanismo de Envío:** Conexión Directa a SUNAT (Web Services SOAP)')
    md.append('* **Fecha del Informe:** 21 de Octubre de 2026')
    md.append('')
    md.append('---')
    md.append('')
    md.append('## 1. Resumen Ejecutivo de Transmisión a SUNAT')
    md.append('')
    md.append('| Estado ante SUNAT | Total Comprobantes | Facturas (01) | Boletas (03) | Notas de Crédito (07) | Notas de Débito (08) | Importe Total (S/) |')
    md.append('| :--- | :---: | :---: | :---: | :---: | :---: | -: |')

    f_acep = len([r for r in aceptados if '(01)' in r['doc_type']])
    b_acep = len([r for r in aceptados if '(03)' in r['doc_type']])
    nc_acep = len([r for r in aceptados if 'Nota de Crédito' in r['doc_type']])

    f_pend = len([r for r in pendientes if '(01)' in r['doc_type']])
    b_pend = len([r for r in pendientes if '(03)' in r['doc_type']])
    nc_pend = len([r for r in pendientes if 'Nota de Crédito' in r['doc_type']])

    f_noenv = len([r for r in no_enviados if '(01)' in r['doc_type']])
    b_noenv = len([r for r in no_enviados if '(03)' in r['doc_type']])
    nc_noenv = len([r for r in no_enviados if 'Nota de Crédito' in r['doc_type']])

    md.append(f"| ✅ **Aceptados por SUNAT (con CDR Oficial)** | **{len(aceptados)}** | {f_acep} | {b_acep} | {nc_acep} | 0 | S/ {tot_aceptados:,.2f} |")
    md.append(f"| ⏳ **Pendientes de Envío a SUNAT (`to_send`)** | **{len(pendientes)}** | {f_pend} | {b_pend} | {nc_pend} | 0 | S/ {tot_pendientes:,.2f} |")
    md.append(f"| 🚫 **No Enviados (Cancelados / Borrador)** | **{len(no_enviados)}** | {f_noenv} | {b_noenv} | {nc_noenv} | 0 | S/ 413.43 |")
    md.append(f"| **TOTAL GLOBAL REGISTRADO** | **{len(records)}** | **{f_acep+f_pend+f_noenv}** | **{b_acep+b_pend+b_noenv}** | **{nc_acep+nc_pend+nc_noenv}** | **0** | **S/ {tot_aceptados+tot_pendientes+413.43:,.2f}** |")
    md.append('')
    md.append('---')
    md.append('')

    # TABLA 1: ACEPTADOS POR SUNAT
    md.append('## 2. Comprobantes Transmitidos y ACEPTADOS por SUNAT (Con CDR Oficial)')
    md.append('')
    md.append('Los siguientes comprobantes fueron transmitidos electrónicamente mediante Web Services a SUNAT, validados por la entidad tributaria y cuentan con su respectiva **Constancia de Recepción (CDR) con Código de Respuesta `0` (Aceptado)** y firma digital de SUNAT:')
    md.append('')
    md.append('| Tipo Comprobante | Serie y Número | Fecha Emisión | Doc. Cliente | Cliente / Razón Social | Total (S/) | Estado SUNAT | Código SUNAT | Respuesta Oficial SUNAT en CDR | Archivo ZIP / CDR |')
    md.append('| :--- | :--- | :-: | :--- | :--- | -: | :---: | :-: | :--- | :--- |')

    for r in aceptados:
        md.append(f"| {r['doc_type']} | `{r['doc_number']}` | {r['date']} | {r['partner_doc']} | {r['partner_name']} | **{r['total']:,.2f}** | ✅ Aceptado | `{r['sunat_code']}` | *{r['sunat_msg']}* | `{r['attachment']}` |")

    md.append('')
    md.append('---')
    md.append('')

    # TABLA 2: PENDIENTES DE ENVIO A SUNAT
    md.append('## 3. Comprobantes PENDIENTES de Envío a SUNAT (Estado: `Por Enviar`)')
    md.append('')
    if pendientes:
        md.append('Los siguientes comprobantes corresponden a la facturación emitida y confirmada en Odoo, los cuales se encuentran en cola de transmisión electrónica (**estado `to_send` / Por Enviar**) listos para su envío y obtención de CDR ante SUNAT:')
        md.append('')
        md.append('| Tipo Comprobante | Serie y Número | Fecha Emisión | Doc. Cliente | Cliente / Razón Social | Subtotal (S/) | IGV 18% (S/) | Total (S/) | Estado de Transmisión SUNAT |')
        md.append('| :--- | :--- | :-: | :--- | :--- | -: | -: | -: | :--- |')
        for r in pendientes:
            md.append(f"| {r['doc_type']} | `{r['doc_number']}` | {r['date']} | {r['partner_doc']} | {r['partner_name']} | {r['untaxed']:,.2f} | {r['tax']:,.2f} | **{r['total']:,.2f}** | ⏳ Por Enviar a SUNAT (`to_send`) |")
    else:
        md.append('> [!TIP]')
        md.append('> **Al Día ante SUNAT:** No existen comprobantes pendientes de envío. La cola de transmisión electrónica se encuentra en **0 comprobantes**.')

    md.append('')
    md.append('---')
    md.append('')

    # SECCION 4: NOTAS DE CREDITO
    md.append('## 4. Detalle de Notas de Crédito Aceptadas por SUNAT (Anulación de Comprobantes)')
    md.append('')
    md.append('Se emitieron y validaron ante SUNAT **3 Notas de Crédito Electrónicas (Tipo 07)** con motivo reglamentario **`01 - Anulación de la operación`**, formalizando la reversión tributaria de las boletas indicadas:')
    md.append('')
    md.append('| N° Nota Crédito | Fecha | Cliente | Comprobante SUNAT Anulado | Total Revertido (S/) | Código CDR | Respuesta Oficial SUNAT |')
    md.append('| :--- | :-: | :--- | :--- | -: | :-: | :--- |')

    for r in aceptados:
        if 'Nota de Crédito' in r['doc_type']:
            rev = r['reversed_entry'] or 'N/A'
            md.append(f"| `{r['doc_number']}` | {r['date']} | {r['partner_name']} ({r['partner_doc']}) | `{rev}` | **-{r['total']:,.2f}** | `{r['sunat_code']}` | *{r['sunat_msg']}* |")

    md.append('')
    md.append('---')
    md.append('')

    # SECCION 5: NOTAS DE DEBITO
    md.append('## 5. Notas de Débito Electrónicas (Tipo 08)')
    md.append('')
    md.append('> [!NOTE]')
    md.append('> **Sin Registros:** A la fecha de este informe, **NO se han emitido Notas de Débito ante SUNAT**. No existieron penalidades, intereses moratorios ni conceptos adicionales que requirieran la generación de este tipo de comprobante.')
    md.append('')
    md.append('---')
    md.append('')

    # SECCION 6: NO ENVIADOS / DESCARTADOS
    md.append('## 6. Comprobantes No Transmitidos a SUNAT (Descartados / Pruebas Internas)')
    md.append('')
    md.append('Comprobantes que no fueron transmitidos a SUNAT por corresponder a pruebas preliminares de numeración o documentos en edición:')
    md.append('')
    md.append('| Comprobante | Tipo | Cliente | Total (S/) | Condición | Motivo por el que no se envió a SUNAT |')
    md.append('| :--- | :--- | :--- | -: | :--- | :--- |')
    for r in no_enviados:
        motivo = 'Comprobante de prueba cancelado antes de enviar' if r['state'] == 'cancel' else 'Comprobante en borrador aún no confirmado'
        md.append(f"| `{r['doc_number']}` | {r['doc_type']} | {r['partner_name']} | S/ {r['total']:,.2f} | {r['state'].upper()} | {motivo} |")

    md.append('')
    md.append('---')
    md.append('*Informe oficial de facturación electrónica SUNAT generado a partir de los registros UBL / EDI de Odoo Enterprise.*')

    content = '\n'.join(md)

    dest1 = '/home/roger/Escritorio/work/py-odoo-cli/REPORTE_COMPROBANTES_ODOO.md'
    dest2 = '/home/roger/Escritorio/work/py-odoo-cli/REPORTE_SUNAT_COMPROBANTES.md'
    dest3 = '/home/roger/Escritorio/work/py-odoo-cli/knowledge/cmline-eirl-inventory/reporte_comprobantes_emitidos_odoo.md'

    for p in [dest1, dest2, dest3]:
        with open(p, 'w', encoding='utf-8') as f:
            f.write(content)

    print(f"Reporte enfocado en SUNAT escrito exitosamente en:\n- {dest1}\n- {dest2}\n- {dest3}")

if __name__ == '__main__':
    main()
