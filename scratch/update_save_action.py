import sys
import os
sys.path.insert(0, os.path.abspath('.'))
from odoo_cli import OdooClient

def main():
    client = OdooClient()
    client.connect()

    new_code = """if records:
    for wizard in records:
        pax_qty = wizard.x_passenger_qty or 1

        # 1. Recalcular x_price_pax por servicio (grupal vs individual)
        for line in wizard.x_line_ids:
            line.write({'x_passenger_qty': pax_qty})
            for svc in line.x_service_line_ids:
                price = svc.x_price or 0.0
                svc.write({
                    'x_price_pax': (price / pax_qty) if (svc.x_is_group and pax_qty) else price
                })

        # 2. Calcular costos operativos (suma de PRECIO PAX)
        op_cost = sum(
            svc.x_price_pax or 0.0
            for line in wizard.x_line_ids
            for svc in line.x_service_line_ids
        )
        fixed = wizard.x_fixed_cost or 0.0
        variable = wizard.x_variable_cost or 0.0
        total_cost = op_cost + fixed + variable

        # 3. Utilidad
        profit_pct_raw = wizard.x_profit_pct if wizard.x_profit_pct is not None else 20.0
        profit_rate = (profit_pct_raw / 100.0) if profit_pct_raw > 1 else profit_pct_raw
        profit_amount = total_cost * profit_rate
        subtotal = total_cost + profit_amount

        # 4. Impuestos (IGV vs Renta)
        igv_pct_raw = wizard.x_igv_pct if wizard.x_igv_pct is not None else 18.0
        renta_pct_raw = wizard.x_renta_pct if wizard.x_renta_pct is not None else 0.3
        igv_rate = (igv_pct_raw / 100.0) if igv_pct_raw > 1 else igv_pct_raw
        renta_rate = (renta_pct_raw / 100.0) if renta_pct_raw > 1 else renta_pct_raw

        tax_rate = 0.0
        if wizard.x_apply_igv:
            tax_rate = igv_rate
        elif wizard.x_apply_renta:
            tax_rate = renta_rate

        tax_amount = subtotal * tax_rate
        subtotal_with_tax = subtotal + tax_amount

        # 5. Comisión por Tarjeta
        card_pct_raw = wizard.x_card_commission_pct if wizard.x_card_commission_pct is not None else 5.0
        card_rate = (card_pct_raw / 100.0) if card_pct_raw > 1 else card_pct_raw
        card_commission = subtotal_with_tax * card_rate
        final_price = subtotal_with_tax + card_commission

        # 6. Escribir resumen financiero actualizado en DB
        wizard.write({
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

        # 7. Sincronizar precio en la linea del presupuesto principal
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

    # 8. Reabrir modal con valores refrescados en pantalla
    action = {
        'type': 'ir.actions.act_window',
        'name': 'Cotización personalizada',
        'res_model': 'x_wtk_custom_quote_wizard',
        'view_mode': 'form',
        'res_id': records[0].id,
        'view_id': 1758,
        'target': 'new',
        'context': {'dialog_size': 'large'},
    }
"""

    res = client.write('ir.actions.server', [627], {'code': new_code})
    print(f"Action 627 update result: {res}")

if __name__ == '__main__':
    main()
