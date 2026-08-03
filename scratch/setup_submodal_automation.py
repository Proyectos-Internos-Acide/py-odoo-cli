import sys
import os
sys.path.insert(0, os.path.abspath('.'))
from odoo_cli import OdooClient

def main():
    client = OdooClient()
    client.connect()

    # 1. Update Server Action 598 code
    action_598_code = """target_records = records or record
if target_records:
    for item in target_records:
        if hasattr(item, 'x_line_id'):
            wiz = item.x_line_id.x_wizard_id if item.x_line_id else False
        elif hasattr(item, 'x_wizard_id'):
            wiz = item.x_wizard_id
        else:
            wiz = False

        if wiz:
            pax_qty = wiz.x_passenger_qty or 1
            # 1. Recalcular x_price_pax en todas las lineas de servicio del wizard
            for line in wiz.x_line_ids:
                for svc in line.x_service_line_ids:
                    price = svc.x_price or 0.0
                    svc.write({
                        'x_price_pax': (price / pax_qty) if (svc.x_is_group and pax_qty) else price
                    })

            # 2. Recalcular resumen financiero completo
            op_cost = sum(
                svc.x_price_pax or 0.0
                for line in wiz.x_line_ids
                for svc in line.x_service_line_ids
            )
            fixed = wiz.x_fixed_cost or 0.0
            variable = wiz.x_variable_cost or 0.0
            total_cost = op_cost + fixed + variable

            profit_pct_raw = wiz.x_profit_pct if wiz.x_profit_pct is not None else 20.0
            profit_rate = (profit_pct_raw / 100.0) if profit_pct_raw > 1 else profit_pct_raw
            profit_amount = total_cost * profit_rate
            subtotal = total_cost + profit_amount

            igv_pct_raw = wiz.x_igv_pct if wiz.x_igv_pct is not None else 18.0
            renta_pct_raw = wiz.x_renta_pct if wiz.x_renta_pct is not None else 0.3
            igv_rate = (igv_pct_raw / 100.0) if igv_pct_raw > 1 else igv_pct_raw
            renta_rate = (renta_pct_raw / 100.0) if renta_pct_raw > 1 else renta_pct_raw

            tax_rate = 0.0
            if wiz.x_apply_igv:
                tax_rate = igv_rate
            elif wiz.x_apply_renta:
                tax_rate = renta_rate

            tax_amount = subtotal * tax_rate
            subtotal_with_tax = subtotal + tax_amount

            card_pct_raw = wiz.x_card_commission_pct if wiz.x_card_commission_pct is not None else 5.0
            card_rate = (card_pct_raw / 100.0) if card_pct_raw > 1 else card_pct_raw
            card_commission = subtotal_with_tax * card_rate
            final_price = subtotal_with_tax + card_commission

            wiz.write({
                'x_operational_cost_pax': op_cost,
                'x_total_cost': total_cost,
                'x_profit_amount': profit_amount,
                'x_subtotal_amount': subtotal,
                'x_tax_amount': tax_amount,
                'x_subtotal_after_tax': subtotal_with_tax,
                'x_card_commission_amount': card_commission,
                'x_final_price': final_price,
                'x_final_price_total': final_price * pax_qty,
            })

            # Sincronizar sale.order.line
            so = wiz.x_sale_order_id
            if so:
                product = env['product.product'].search([('name', '=', 'Custom Quotation')], limit=1)
                if product:
                    soline = env['sale.order.line'].search([
                        ('order_id', '=', so.id),
                        ('product_id', '=', product.id)
                    ], limit=1)
                    if soline:
                        soline.write({'price_unit': final_price})
"""

    res_sa = client.write('ir.actions.server', [598], {'code': action_598_code})
    print(f"Updated Server Action 598: {res_sa}")

    # 2. Update Automation ID 14 (on x_wtk_custom_quote_wizard_service_line) to trigger on_create_or_write
    res_auto14 = client.write('base.automation', [14], {'trigger': 'on_create_or_write'})
    print(f"Updated Automation 14 trigger to on_create_or_write: {res_auto14}")

    # 3. Check if automation exists for x_wtk_custom_quote_wizard_line (Model ID 763)
    existing_line_auto = client.search_read(
        'base.automation',
        domain=[('model_id', '=', 763)],
        fields=['id', 'name']
    )
    if not existing_line_auto:
        new_auto_id = client.create('base.automation', {
            'name': 'WTK - Auto costos wizard desde linea custom',
            'model_id': 763,
            'trigger': 'on_create_or_write',
            'action_server_ids': [(6, 0, [598])]
        })
        print(f"Created new automation for wizard line (ID {new_auto_id})")
    else:
        print(f"Existing automation for wizard line: {existing_line_auto}")
        client.write('base.automation', [existing_line_auto[0]['id']], {
            'trigger': 'on_create_or_write',
            'action_server_ids': [(6, 0, [598])]
        })
        print("Updated existing line automation")

if __name__ == '__main__':
    main()
