import sys
import os
sys.path.insert(0, os.path.abspath('.'))
from odoo_cli import OdooClient

def main():
    print("==================================================================")
    print(" Applying Custom Quote Wizard Updates to PRODUCTION (wayki-trek) ")
    print("==================================================================")
    
    client = OdooClient()
    client.connect()

    # -------------------------------------------------------------------------
    # Python code for full financial recalculation
    # -------------------------------------------------------------------------
    code_wizard_recalc = """target_records = records or record
if target_records:
    for wiz in target_records:
        pax_qty = wiz.x_passenger_qty or 1

        # 1. Recalculate x_price_pax per service (group vs individual)
        for line in wiz.x_line_ids:
            line.write({'x_passenger_qty': pax_qty})
            for svc in line.x_service_line_ids:
                price = svc.x_price or 0.0
                svc.write({
                    'x_price_pax': (price / pax_qty) if (svc.x_is_group and pax_qty) else price
                })

        # 2. Calculate operational cost (sum of x_price_pax)
        op_cost = sum(
            svc.x_price_pax or 0.0
            for line in wiz.x_line_ids
            for svc in line.x_service_line_ids
        )
        fixed = wiz.x_fixed_cost or 0.0
        variable = wiz.x_variable_cost or 0.0
        total_cost = op_cost + fixed + variable

        # 3. Profit
        profit_pct_raw = wiz.x_profit_pct if wiz.x_profit_pct is not None else 20.0
        profit_rate = (profit_pct_raw / 100.0) if profit_pct_raw > 1 else profit_pct_raw
        profit_amount = total_cost * profit_rate
        subtotal = total_cost + profit_amount

        # 4. Taxes (IGV vs Renta)
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

        # 5. Card commission
        card_pct_raw = wiz.x_card_commission_pct if wiz.x_card_commission_pct is not None else 5.0
        card_rate = (card_pct_raw / 100.0) if card_pct_raw > 1 else card_pct_raw
        card_commission = subtotal_with_tax * card_rate
        final_price = subtotal_with_tax + card_commission

        # 6. Write financial summary back to wizard
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

        # 7. Synchronize price on sale.order.line
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

    code_action_627 = code_wizard_recalc + """
    # 8. Reopen modal with refreshed values
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

    code_action_598 = """target_records = records or record
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
                    soline = env['sale.order.line'].search([
                        ('order_id', '=', so.id),
                        ('product_id', '=', product.id)
                    ], limit=1)
                    if soline:
                        soline.write({'price_unit': final_price})
"""

    code_action_line = """target_records = records or record
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

    # 1. Update Server Action 627 (Guardar wizard)
    print("1. Updating Server Action 627 (WTK - Guardar wizard)...")
    res627 = client.write('ir.actions.server', [627], {'code': code_action_627})
    print(f"   --> Success: {res627}")

    # 2. Update Server Action 597 (Recalcular costos wizard)
    print("2. Updating Server Action 597 (WTK - Recalcular costos wizard)...")
    res597 = client.write('ir.actions.server', [597], {'code': code_wizard_recalc})
    print(f"   --> Success: {res597}")

    # 3. Update Server Action 598 (Recalcular costos wizard desde servicio)
    print("3. Updating Server Action 598 (WTK - Recalcular costos wizard desde servicio)...")
    res598 = client.write('ir.actions.server', [598], {'code': code_action_598})
    print(f"   --> Success: {res598}")

    # 4. Update Automation 13 (WTK - Auto recalcular costos wizard) to include x_passenger_qty
    print("4. Updating Automation 13 on_change_field_ids...")
    f_ids = [15363, 15367, 15375, 15351, 15365, 15323, 15357, 15369, 15353, 15299]
    res13 = client.write('base.automation', [13], {'on_change_field_ids': [(6, 0, f_ids)]})
    print(f"   --> Success: {res13}")

    # 5. Update Automation 14 (WTK - Auto costos wizard desde servicio) trigger to on_create_or_write
    print("5. Updating Automation 14 trigger to on_create_or_write...")
    res14 = client.write('base.automation', [14], {'trigger': 'on_create_or_write'})
    print(f"   --> Success: {res14}")

    # 6. Check / Create Server Action & Automations for Model 763 (WTK Custom Quote Wizard Line)
    print("6. Configuring Server Action and Automations for Model 763 (Wizard Line)...")
    existing_sa_line = client.search_read(
        'ir.actions.server',
        domain=[('model_id', '=', 763), ('name', '=', 'WTK - Recalcular costos wizard desde linea custom')],
        fields=['id']
    )
    if existing_sa_line:
        sa_line_id = existing_sa_line[0]['id']
        client.write('ir.actions.server', [sa_line_id], {'code': code_action_line})
        print(f"   --> Updated Server Action {sa_line_id}")
    else:
        sa_line_id = client.create('ir.actions.server', {
            'name': 'WTK - Recalcular costos wizard desde linea custom',
            'model_id': 763,
            'state': 'code',
            'code': code_action_line
        })
        print(f"   --> Created Server Action {sa_line_id}")

    existing_auto_line = client.search_read(
        'base.automation',
        domain=[('model_id', '=', 763), ('name', '=', 'WTK - Auto costos wizard desde linea custom')],
        fields=['id']
    )
    if existing_auto_line:
        client.write('base.automation', [existing_auto_line[0]['id']], {
            'trigger': 'on_create_or_write',
            'action_server_ids': [(6, 0, [sa_line_id])]
        })
        print(f"   --> Updated Automation {existing_auto_line[0]['id']}")
    else:
        auto_line_id = client.create('base.automation', {
            'name': 'WTK - Auto costos wizard desde linea custom',
            'model_id': 763,
            'trigger': 'on_create_or_write',
            'action_server_ids': [(6, 0, [sa_line_id])]
        })
        print(f"   --> Created Automation {auto_line_id}")

    # 7. Deletion automations (on_unlink)
    print("7. Configuring on_unlink deletion automations...")
    # Service Line deletion (Model 765)
    existing_unlink_svc = client.search_read(
        'base.automation',
        domain=[('model_id', '=', 765), ('name', '=', 'WTK - Recalcular al eliminar servicio')],
        fields=['id']
    )
    if not existing_unlink_svc:
        auto_unlink_svc_id = client.create('base.automation', {
            'name': 'WTK - Recalcular al eliminar servicio',
            'model_id': 765,
            'trigger': 'on_unlink',
            'action_server_ids': [(6, 0, [598])]
        })
        print(f"   --> Created on_unlink automation {auto_unlink_svc_id} for Model 765")
    else:
        print(f"   --> Deletion automation for Model 765 already exists ({existing_unlink_svc[0]['id']})")

    # Custom Line deletion (Model 763)
    existing_unlink_line = client.search_read(
        'base.automation',
        domain=[('model_id', '=', 763), ('name', '=', 'WTK - Recalcular al eliminar linea custom')],
        fields=['id']
    )
    if not existing_unlink_line:
        auto_unlink_line_id = client.create('base.automation', {
            'name': 'WTK - Recalcular al eliminar linea custom',
            'model_id': 763,
            'trigger': 'on_unlink',
            'action_server_ids': [(6, 0, [sa_line_id])]
        })
        print(f"   --> Created on_unlink automation {auto_unlink_line_id} for Model 763")
    else:
        print(f"   --> Deletion automation for Model 763 already exists ({existing_unlink_line[0]['id']})")

    # 8. Main Wizard Save Automation (Model 761)
    print("8. Configuring on_create_or_write automation for main Wizard (Model 761)...")
    existing_auto_wiz = client.search_read(
        'base.automation',
        domain=[('model_id', '=', 761), ('name', '=', 'WTK - Auto costos wizard en guardado')],
        fields=['id']
    )
    if not existing_auto_wiz:
        auto_wiz_id = client.create('base.automation', {
            'name': 'WTK - Auto costos wizard en guardado',
            'model_id': 761,
            'trigger': 'on_create_or_write',
            'action_server_ids': [(6, 0, [597])]
        })
        print(f"   --> Created on_create_or_write automation {auto_wiz_id} for Wizard")
    else:
        print(f"   --> Automation for Model 761 already exists ({existing_auto_wiz[0]['id']})")

    print("\n==================================================================")
    print(" ALL CUSTOM QUOTE WIZARD UPDATES APPLIED TO PRODUCTION SUCCESSFULLY ")
    print("==================================================================")

if __name__ == '__main__':
    main()
