from odoo_cli import OdooClient

def revert_server_action():
    client = OdooClient()
    client.connect()
    
    old_code = """if records:
    for wizard in records:
        pax_qty = wizard.x_passenger_qty or 1

        for line in wizard.x_line_ids:
            for svc in line.x_service_line_ids:
                price = svc.x_price or 0.0
                if svc.x_is_group:
                    svc.write({'x_price_pax': (price / pax_qty) if pax_qty else price})
                else:
                    svc.write({'x_price_pax': price})

        op_cost = sum(svc.x_price_pax or 0.0 for line in wizard.x_line_ids for svc in line.x_service_line_ids)
        fixed = wizard.x_fixed_cost or 0.0
        variable = wizard.x_variable_cost or 0.0
        total_cost = op_cost + fixed + variable

        profit_pct_raw = wizard.x_profit_pct if wizard.x_profit_pct is not None else 20.0
        profit_rate = (profit_pct_raw / 100.0) if profit_pct_raw > 1 else profit_pct_raw
        profit_amount = total_cost * profit_rate
        subtotal = total_cost + profit_amount

        igv_pct_raw = wizard.x_igv_pct if wizard.x_igv_pct is not None else 18.0
        renta_pct_raw = wizard.x_renta_pct if wizard.x_renta_pct is not None else 0.3
        igv_rate = (igv_pct_raw / 100.0) if igv_pct_raw > 1 else igv_pct_raw
        renta_rate = (renta_pct_raw / 100.0) if renta_pct_raw > 1 else renta_pct_raw
        tax_rate = igv_rate if wizard.x_apply_igv else (renta_rate if wizard.x_apply_renta else 0.0)
        tax_amount = subtotal * tax_rate
        subtotal_with_tax = subtotal + tax_amount

        card_pct_raw = wizard.x_card_commission_pct if wizard.x_card_commission_pct is not None else 5.0
        card_rate = (card_pct_raw / 100.0) if card_pct_raw > 1 else card_pct_raw
        card_commission = subtotal_with_tax * card_rate
        final_price = subtotal_with_tax + card_commission

        wizard.write({
            'x_operational_cost_pax': op_cost,
            'x_total_cost': total_cost,
            'x_profit_amount': profit_amount,
            'x_subtotal_amount': subtotal,
            'x_tax_amount': tax_amount,
            'x_subtotal_after_tax': subtotal_with_tax,
            'x_card_commission_amount': card_commission,
            'x_final_price': final_price,
            'x_final_price_total': final_price * (wizard.x_passenger_qty or 1),
        })

        # Sincronizar precio en la linea del presupuesto principal
        so = wizard.x_sale_order_id
        if so:
            product = env['product.product'].search([('name', '=', 'Custom Quotation')], limit=1)
            if product:
                line = env['sale.order.line'].search([
                    ('order_id', '=', so.id),
                    ('product_id', '=', product.id)
                ], limit=1)
                if line:
                    line.write({'price_unit': final_price})

            # Generar PDF Cliente y adjuntar a Chatter
            report_obj = env['ir.actions.report'].search([('name', '=', 'WTK - PDF Cotización cliente'), ('model', '=', 'x_wtk_custom_quote_wizard')], limit=1)
            if report_obj:
                pdf_content, dummy = env['ir.actions.report']._render_qweb_pdf(report_obj.id, [wizard.id])
                attachment = env['ir.attachment'].create({
                    'name': f"Cotizacion_Cliente_{so.name}.pdf",
                    'type': 'binary',
                    'raw': pdf_content,
                    'res_model': 'sale.order',
                    'res_id': so.id,
                })
                so.message_post(
                    body="Se ha generado y guardado la cotización personalizada (Cliente).",
                    attachment_ids=[attachment.id]
                )

    report = env['ir.actions.report'].search([('name', '=', 'WTK - PDF Cotización cliente'), ('model', '=', 'x_wtk_custom_quote_wizard')], limit=1)
    if report:
        action = report.report_action(records)
    else:
        action = {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {'title': 'Cotización cliente', 'message': 'No se encontró el reporte PDF cliente.', 'type': 'warning', 'sticky': False}
        }
"""
    client.write('ir.actions.server', [602], {'code': old_code})
    print("Server Action 602 REVERTIDA exitosamente!")

if __name__ == '__main__':
    revert_server_action()
