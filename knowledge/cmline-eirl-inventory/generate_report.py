#!/usr/bin/env python3
"""
Generador de Reporte Consolidado de Comprobantes de Pago de Odoo.
Empresa: CM LINE E.I.R.L.
"""
import json
import os

SCRATCH_DATA = '/home/roger/.gemini/antigravity-ide/brain/6538d3ff-e492-4205-b694-c52b7c1c484a/scratch/all_moves.json'

def main():
    with open(SCRATCH_DATA, 'r', encoding='utf-8') as f:
        moves = json.load(f)

    facturas = [m for m in moves if '(01)' in m['doc_type']]
    boletas = [m for m in moves if '(03)' in m['doc_type']]
    notas_credito = [m for m in moves if 'Nota de Crédito' in m['doc_type']]
    notas_debito = [m for m in moves if 'Nota de Débito' in m['doc_type']]

    total_facturas_posted = sum(m['total'] for m in facturas if m['state'] == 'posted')
    total_boletas_posted = sum(m['total'] for m in boletas if m['state'] == 'posted')
    total_nc_posted = sum(m['total'] for m in notas_credito if m['state'] == 'posted')
    neto_facturado = total_facturas_posted + total_boletas_posted - total_nc_posted

    def format_currency(val):
        return f"S/ {val:,.2f}"

    def translate_state(st):
        mapping = {
            'posted': 'Publicado',
            'draft': 'Borrador',
            'cancel': 'Cancelado'
        }
        return mapping.get(st, st)

    def translate_payment(ps):
        mapping = {
            'paid': 'Pagado',
            'in_payment': 'En proceso de pago',
            'not_paid': 'Pendiente de pago',
            'reversed': 'Revertido',
            'partial': 'Pago parcial'
        }
        return mapping.get(ps, ps or 'N/A')

    md = []
    md.append('# Informe Consolidado de Comprobantes de Pago Emitidos en Odoo')
    md.append('')
    md.append('> [!NOTE]')
    md.append('> **Finalidad del Documento:** Presentar un desglose exhaustivo y formal de todas las Facturas, Boletas de Venta, Notas de Crédito y Notas de Débito generadas en la plataforma contable Odoo para conocimiento y conciliación con la empresa destino.')
    md.append('')
    md.append('### Ficha de la Empresa Emisora')
    md.append('* **Razón Social:** CM LINE E.I.R.L.')
    md.append('* **RUC:** `20608453271`')
    md.append('* **Dirección Fiscal:** Avenida PACIFICO MZA. 32, LOTE. 5B, P.J. MIGUEL, Arequipa, Perú')
    md.append('* **Instancia Odoo:** [https://cm-line.odoo.com](https://cm-line.odoo.com)')
    md.append('* **Base de Datos:** `cm-line`')
    md.append('* **Fecha de Emisión del Informe:** 21 de Octubre de 2026')
    md.append('')
    md.append('---')
    md.append('')
    md.append('## 1. Resumen Ejecutivo y Totales Financieros')
    md.append('')
    md.append('A continuación se presenta el balance global de comprobantes procesados en el sistema contable:')
    md.append('')
    md.append('| Tipo de Comprobante | Código SUNAT | Total Registrados | Válidos (Publicados) | En Borrador / Anulados | Monto Bruto (S/) |')
    md.append('| :--- | :---: | :---: | :---: | :---: | :---: |')
    md.append(f"| **Facturas de Venta** | `01` | {len(facturas)} | {len([m for m in facturas if m['state'] == 'posted'])} | {len([m for m in facturas if m['state'] != 'posted'])} | {format_currency(total_facturas_posted)} |")
    md.append(f"| **Boletas de Venta** | `03` | {len(boletas)} | {len([m for m in boletas if m['state'] == 'posted'])} | {len([m for m in boletas if m['state'] != 'posted'])} | {format_currency(total_boletas_posted)} |")
    md.append(f"| **Notas de Crédito** | `07` | {len(notas_credito)} | {len([m for m in notas_credito if m['state'] == 'posted'])} | 0 | -{format_currency(total_nc_posted)} |")
    md.append(f"| **Notas de Débito** | `08` | {len(notas_debito)} | 0 | 0 | S/ 0.00 |")
    md.append(f"| **TOTAL NETO CONSOLIDADO** | - | **{len(moves)}** | **{len([m for m in moves if m['state'] == 'posted'])}** | **{len([m for m in moves if m['state'] != 'posted'])}** | **{format_currency(neto_facturado)}** |")
    md.append('')
    md.append('### Balance de Cobranza sobre Comprobantes Válidos:')
    paid_moves = [m for m in moves if m['state'] == 'posted' and m['payment_state'] == 'paid']
    in_payment_moves = [m for m in moves if m['state'] == 'posted' and m['payment_state'] == 'in_payment']
    not_paid_moves = [m for m in moves if m['state'] == 'posted' and m['payment_state'] == 'not_paid']
    
    total_paid = sum(m['total'] for m in paid_moves)
    total_in_payment = sum(m['total'] for m in in_payment_moves)
    total_not_paid = sum(m['total'] for m in not_paid_moves)

    md.append(f"* **Comprobantes Pagados / Conciliados:** {len(paid_moves)} comprobantes ({format_currency(total_paid)})")
    md.append(f"* **Comprobantes en Proceso de Pago:** {len(in_payment_moves)} comprobantes ({format_currency(total_in_payment)})")
    md.append(f"* **Comprobantes Pendientes de Pago:** {len(not_paid_moves)} comprobantes ({format_currency(total_not_paid)})")
    md.append('')
    md.append('---')
    md.append('')

    # SECTION 2: FACTURAS
    md.append('## 2. Relación Detallada de Facturas de Venta (Tipo 01)')
    md.append('')
    md.append('Se registran un total de **24 facturas**, de las cuales **21 se encuentran debidamente publicadas**, 2 corresponden a comprobantes de prueba preliminares cancelados, y 1 se encuentra en borrador.')
    md.append('')
    md.append('| ID | Número / Serie | Fecha | RUC / Documento | Razón Social / Cliente | Diario | Estado Contable | Estado de Pago | Base Imponible (S/) | IGV 18% (S/) | Total (S/) |')
    md.append('| :-: | :--- | :-: | :--- | :--- | :--- | :--- | :--- | -: | -: | -: |')

    for m in facturas:
        doc_num = m['doc_number'] or (m['name'] if m['name'] else 'Borrador')
        partner_doc = m['partner_doc'] or 'Sin Doc'
        partner_name = m['partner_name'] or 'Sin Cliente'
        md.append(f"| {m['id']} | `{doc_num}` | {m['date']} | {partner_doc} | {partner_name} | {m['journal']} | {translate_state(m['state'])} | {translate_payment(m['payment_state'])} | {m['untaxed']:,.2f} | {m['tax']:,.2f} | **{m['total']:,.2f}** |")

    md.append('')
    md.append('### Desglose de Productos por Factura:')
    md.append('')

    for m in facturas:
        doc_num = m['doc_number'] or (m['name'] if m['name'] else 'Borrador')
        md.append(f"#### Factura `{doc_num}` (ID Odoo: `{m['id']}`)")
        md.append(f"* **Cliente:** {m['partner_name']} ({m['partner_doc']})")
        md.append(f"* **Fecha de Emisión:** {m['date']} | **Diario:** {m['journal']} | **Referencia/Pedido:** {m['ref'] or 'N/A'}")
        md.append(f"* **Estado:** {translate_state(m['state'])} | **Condición de Cobro:** {translate_payment(m['payment_state'])}")
        md.append(f"* **Resumen de Importes:** Base: S/ {m['untaxed']:,.2f} | IGV: S/ {m['tax']:,.2f} | **Total: S/ {m['total']:,.2f}**")
        if m['items']:
            md.append('')
            md.append('| Ítem / Descripción del Producto | Cantidad | P. Unitario (S/) | Subtotal (S/) | Total c/IGV (S/) |')
            md.append('| :--- | :-: | -: | -: | -: |')
            for it in m['items']:
                md.append(f"| {it['product']} | {it['qty']:g} | {it['price_unit']:,.2f} | {it['subtotal']:,.2f} | {it['total']:,.2f} |")
        else:
            md.append('* *Comprobante sin líneas de productos.*')
        md.append('')

    md.append('---')
    md.append('')

    # SECTION 3: BOLETAS
    md.append('## 3. Relación Detallada de Boletas de Venta (Tipo 03)')
    md.append('')
    md.append('Se registran un total de **8 boletas de venta**, de las cuales **7 se encuentran publicadas** y 1 fue cancelada durante pruebas de serie.')
    md.append('')
    md.append('| ID | Número / Serie | Fecha | DNI / Documento | Cliente / Consumidor | Diario | Estado Contable | Estado de Pago | Base Imponible (S/) | IGV 18% (S/) | Total (S/) |')
    md.append('| :-: | :--- | :-: | :--- | :--- | :--- | :--- | :--- | -: | -: | -: |')

    for m in boletas:
        doc_num = m['doc_number'] or (m['name'] if m['name'] else 'Borrador')
        partner_doc = m['partner_doc'] or 'Sin Doc'
        partner_name = m['partner_name'] or 'Sin Cliente'
        md.append(f"| {m['id']} | `{doc_num}` | {m['date']} | {partner_doc} | {partner_name} | {m['journal']} | {translate_state(m['state'])} | {translate_payment(m['payment_state'])} | {m['untaxed']:,.2f} | {m['tax']:,.2f} | **{m['total']:,.2f}** |")

    md.append('')
    md.append('### Desglose de Productos por Boleta:')
    md.append('')

    for m in boletas:
        doc_num = m['doc_number'] or (m['name'] if m['name'] else 'Borrador')
        md.append(f"#### Boleta `{doc_num}` (ID Odoo: `{m['id']}`)")
        md.append(f"* **Cliente:** {m['partner_name']} ({m['partner_doc']})")
        md.append(f"* **Fecha de Emisión:** {m['date']} | **Diario:** {m['journal']} | **Referencia/Pedido:** {m['ref'] or 'N/A'}")
        md.append(f"* **Estado:** {translate_state(m['state'])} | **Condición de Cobro:** {translate_payment(m['payment_state'])}")
        md.append(f"* **Resumen de Importes:** Base: S/ {m['untaxed']:,.2f} | IGV: S/ {m['tax']:,.2f} | **Total: S/ {m['total']:,.2f}**")
        if m['items']:
            md.append('')
            md.append('| Ítem / Descripción del Producto | Cantidad | P. Unitario (S/) | Subtotal (S/) | Total c/IGV (S/) |')
            md.append('| :--- | :-: | -: | -: | -: |')
            for it in m['items']:
                md.append(f"| {it['product']} | {it['qty']:g} | {it['price_unit']:,.2f} | {it['subtotal']:,.2f} | {it['total']:,.2f} |")
        else:
            md.append('* *Comprobante sin líneas de productos.*')
        md.append('')

    md.append('---')
    md.append('')

    # SECTION 4: NOTAS DE CREDITO
    md.append('## 4. Relación Detallada de Notas de Crédito (Tipo 07)')
    md.append('')
    md.append('Se registran **3 notas de crédito**, emitidas para formalizar la anulación y reversión contable de boletas de venta previas conforme a normativa tributaria.')
    md.append('')
    md.append('| ID | Número / Serie | Fecha | Cliente | Comprobante Modificado | Diario | Estado | Motivo de Emisión | Importe Revertido (S/) |')
    md.append('| :-: | :--- | :-: | :--- | :--- | :--- | :--- | :--- | -: |')

    for m in notas_credito:
        doc_num = m['doc_number'] or (m['name'] if m['name'] else 'Borrador')
        partner_name = m['partner_name'] or 'Sin Cliente'
        rev_entry = m['reversed_entry'] or 'N/A'
        md.append(f"| {m['id']} | `{doc_num}` | {m['date']} | {partner_name} | `{rev_entry}` | {m['journal']} | {translate_state(m['state'])} | Anulación de la operación | **-{m['total']:,.2f}** |")

    md.append('')
    md.append('### Desglose por Nota de Crédito:')
    md.append('')

    for m in notas_credito:
        doc_num = m['doc_number'] or (m['name'] if m['name'] else 'Borrador')
        md.append(f"#### Nota de Crédito `{doc_num}` (ID Odoo: `{m['id']}`)")
        md.append(f"* **Cliente:** {m['partner_name']} ({m['partner_doc']})")
        md.append(f"* **Fecha de Emisión:** {m['date']} | **Diario:** {m['journal']}")
        md.append(f"* **Documento Modificado / Anulado:** `{m['reversed_entry'] or 'N/A'}`")
        md.append(f"* **Motivo SUNAT:** `01 - Anulación de la operación`")
        md.append(f"* **Importe Revertido:** Base: S/ {m['untaxed']:,.2f} | IGV: S/ {m['tax']:,.2f} | **Total: -S/ {m['total']:,.2f}**")
        if m['items']:
            md.append('')
            md.append('| Ítem Revertido | Cantidad | P. Unitario (S/) | Subtotal Revertido (S/) | Total Revertido (S/) |')
            md.append('| :--- | :-: | -: | -: | -: |')
            for it in m['items']:
                md.append(f"| {it['product']} | {it['qty']:g} | {it['price_unit']:,.2f} | {it['subtotal']:,.2f} | {it['total']:,.2f} |")
        md.append('')

    md.append('---')
    md.append('')

    # SECTION 5: NOTAS DE DEBITO
    md.append('## 5. Notas de Débito (Tipo 08)')
    md.append('')
    md.append('> [!NOTE]')
    md.append('> **Sin Registros:** A la fecha de este informe, **no se han generado Notas de Débito** en la base de datos de CM LINE E.I.R.L. No existieron penalidades, intereses moratorios ni diferencias de precio que requirieran emitir notas de débito electrónicas.')
    md.append('')
    md.append('---')
    md.append('')

    # SECTION 6: DIARIOS Y SERIES
    md.append('## 6. Estructura de Diarios y Series Documentarias Utilizadas')
    md.append('')
    md.append('Para trazabilidad y auditoría de la empresa destino, se desglosan los diarios de venta configurados y sus respectivas series correlativas:')
    md.append('')
    md.append('1. **Diario `Facturas Sucursal` (Código `F999`):**')
    md.append('   * Serie activa para ventas comerciales mayoristas y con personas jurídicas con RUC.')
    md.append('   * Rango emitido: `F999-00000001` al `F999-00000020`.')
    md.append('2. **Diario `Boletas Sucursal` (Código `B999`):**')
    md.append('   * Serie activa para ventas a consumidores finales con DNI.')
    md.append('   * Rango emitido: `B999-00000001` al `B999-00000003`.')
    md.append('3. **Diarios de Pruebas Iniciales (`Sales` / `Facturas Electrónicas` / `Boletas Electrónicas`):**')
    md.append('   * Comprobantes `FFI-00000001` (cancelado), `F001-00000001` (cancelado), `B001-00000001` (cancelado).')
    md.append('   * Comprobantes `BOL-00000001` a `BOL-00000004` (anulados y conciliados mediante las notas de crédito `CNE-00000001` a `CNE-00000003`).')
    md.append('')
    md.append('---')
    md.append('')
    md.append('*Informe generado directamente desde la base de datos de Odoo Enterprise (`cm-line`) para fines de entrega, auditoría y conocimiento de la empresa destino.*')

    final_content = '\n'.join(md)

    dest1 = '/home/roger/Escritorio/work/py-odoo-cli/REPORTE_COMPROBANTES_ODOO.md'
    dest2 = '/home/roger/Escritorio/work/py-odoo-cli/knowledge/cmline-eirl-inventory/reporte_comprobantes_emitidos_odoo.md'

    with open(dest1, 'w', encoding='utf-8') as f:
        f.write(final_content)
    with open(dest2, 'w', encoding='utf-8') as f:
        f.write(final_content)

    print(f"Reporte generado con exito en:\n- {dest1}\n- {dest2}")
    print(f"Total lineas generadas: {len(md)}")

if __name__ == '__main__':
    main()
