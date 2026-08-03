import sys
import os
sys.path.insert(0, os.path.abspath('.'))
from odoo_cli import OdooClient

def main():
    client = OdooClient()
    client.connect()

    # 1. Update Server Action 597 code
    code_597 = """target_records = records or record
if target_records:
    for wiz in target_records:
        pax_qty = wiz.x_passenger_qty or 1
        # Recalcular x_price_pax por servicio
        for line in wiz.x_line_ids:
            for svc in line.x_service_line_ids:
                price = svc.x_price or 0.0
                svc.write({
                    'x_price_pax': (price / pax_qty) if (svc.x_is_group and pax_qty) else price
                })

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

        so = wiz.x_sale_order_id
        if so:
            product = env['product.product'].search([('name', '=', 'Custom Quotation')], limit=1)
            if product:
                line = env['sale.order.line'].search([
                    ('order_id', '=', so.id),
                    ('product_id', '=', product.id)
                ], limit=1)
                if line:
                    line.write({'price_unit': final_price})
"""
    client.write('ir.actions.server', [597], {'code': code_597})
    print("Updated Server Action 597")

    # 2. Add field 15299 (x_passenger_qty) to Automation 13 on_change_field_ids
    f_ids = [15363, 15367, 15375, 15351, 15365, 15323, 15357, 15369, 15353, 15299]
    client.write('base.automation', [13], {
        'on_change_field_ids': [(6, 0, f_ids)]
    })
    print("Updated Automation 13 on_change_field_ids with x_passenger_qty")

    # 3. Create on_create_or_write automation for x_wtk_custom_quote_wizard (Model 761)
    existing_auto = client.search_read(
        'base.automation',
        domain=[('model_id', '=', 761), ('name', '=', 'WTK - Auto costos wizard en guardado')],
        fields=['id']
    )
    if not existing_auto:
        auto_id = client.create('base.automation', {
            'name': 'WTK - Auto costos wizard en guardado',
            'model_id': 761,
            'trigger': 'on_create_or_write',
            'action_server_ids': [(6, 0, [597])]
        })
        print(f"Created on_create_or_write automation {auto_id} for Wizard model")
    else:
        print("on_create_or_write automation for Wizard model already exists")

if __name__ == '__main__':
    main()
