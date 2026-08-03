import sys
import os
sys.path.insert(0, os.path.abspath('.'))
from odoo_cli import OdooClient

def main():
    client = OdooClient()
    client.connect()

    code_line = """target_records = records or record
if target_records:
    for line in target_records:
        wiz = line.x_wizard_id
        if wiz:
            pax_qty = wiz.x_passenger_qty or 1
            for l in wiz.x_line_ids:
                for svc in l.x_service_line_ids:
                    price = svc.x_price or 0.0
                    svc.write({
                        'x_price_pax': (price / pax_qty) if (svc.x_is_group and pax_qty) else price
                    })
            op_cost = sum(
                svc.x_price_pax or 0.0
                for l in wiz.x_line_ids
                for svc in l.x_service_line_ids
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
                    soline = env['sale.order.line'].search([
                        ('order_id', '=', so.id),
                        ('product_id', '=', product.id)
                    ], limit=1)
                    if soline:
                        soline.write({'price_unit': final_price})
"""

    # 1. Check or create Server Action for Model 763 (WTK Custom Quote Wizard Line)
    existing_action = client.search_read(
        'ir.actions.server',
        domain=[('model_id', '=', 763), ('name', '=', 'WTK - Recalcular costos wizard desde linea custom')],
        fields=['id']
    )
    if existing_action:
        sa_line_id = existing_action[0]['id']
        client.write('ir.actions.server', [sa_line_id], {'code': code_line})
        print(f"Updated Server Action {sa_line_id}")
    else:
        sa_line_id = client.create('ir.actions.server', {
            'name': 'WTK - Recalcular costos wizard desde linea custom',
            'model_id': 763,
            'state': 'code',
            'code': code_line
        })
        print(f"Created Server Action {sa_line_id} for Model 763")

    # 2. Check or create Automation Rule for Model 763 (WTK Custom Quote Wizard Line)
    existing_auto = client.search_read(
        'base.automation',
        domain=[('model_id', '=', 763), ('name', '=', 'WTK - Auto costos wizard desde linea custom')],
        fields=['id']
    )
    if existing_auto:
        client.write('base.automation', [existing_auto[0]['id']], {
            'trigger': 'on_create_or_write',
            'action_server_ids': [(6, 0, [sa_line_id])]
        })
        print(f"Updated Automation {existing_auto[0]['id']} for Model 763")
    else:
        auto_id = client.create('base.automation', {
            'name': 'WTK - Auto costos wizard desde linea custom',
            'model_id': 763,
            'trigger': 'on_create_or_write',
            'action_server_ids': [(6, 0, [sa_line_id])]
        })
        print(f"Created Automation Rule {auto_id} for Model 763")

    # 3. Add on_unlink triggers for deletion recalculation
    # Service Line deletion automation
    existing_unlink_svc = client.search_read(
        'base.automation',
        domain=[('model_id', '=', 765), ('name', '=', 'WTK - Recalcular al eliminar servicio')],
        fields=['id']
    )
    if not existing_unlink_svc:
        client.create('base.automation', {
            'name': 'WTK - Recalcular al eliminar servicio',
            'model_id': 765,
            'trigger': 'on_unlink',
            'action_server_ids': [(6, 0, [598])]
        })
        print("Created on_unlink automation for service line (Model 765)")

    # Line deletion automation
    existing_unlink_line = client.search_read(
        'base.automation',
        domain=[('model_id', '=', 763), ('name', '=', 'WTK - Recalcular al eliminar linea custom')],
        fields=['id']
    )
    if not existing_unlink_line:
        client.create('base.automation', {
            'name': 'WTK - Recalcular al eliminar linea custom',
            'model_id': 763,
            'trigger': 'on_unlink',
            'action_server_ids': [(6, 0, [sa_line_id])]
        })
        print("Created on_unlink automation for custom line (Model 763)")

if __name__ == '__main__':
    main()
