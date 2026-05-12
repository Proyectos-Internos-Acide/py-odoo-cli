from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from odoo_cli import OdooClient
from constants import *
from constants import _get_model

def _upsert_service_price_pax_onchange(client: OdooClient, service_line_model: dict) -> None:
    """Recalcula PRECIO PAX en onchange sin usar compute (safe_eval friendly)."""
    field_rec = client.search_read(
        "ir.model.fields",
        domain=[["model", "=", WIZ_SERVICE_LINE_MODEL], ["name", "=", "x_price_pax"]],
        fields=["id"],
        limit=1,
    )
    if field_rec:
        client.write(
            "ir.model.fields",
            [field_rec[0]["id"]],
            {
                "compute": False,
                "depends": False,
                "readonly": True,
            },
        )

    action_name = "WTK - Recalcular precio pax (onchange)"
    action_code = """
target_records = records or record
if target_records:
    for rec in target_records:
        wizard_line = rec.x_line_id
        wizard = wizard_line.x_wizard_id if wizard_line else False
        pax_qty = 1
        if wizard and wizard.x_passenger_qty:
            pax_qty = wizard.x_passenger_qty
        elif wizard_line and wizard_line.x_passenger_qty:
            pax_qty = wizard_line.x_passenger_qty
        price = rec.x_price or 0.0
        value = (price / pax_qty) if (rec.x_is_group and pax_qty) else price
        rec.write({'x_price_pax': value})
""".strip()

    action_existing = client.search_read(
        "ir.actions.server",
        domain=[["name", "=", action_name], ["model_id", "=", service_line_model["id"]]],
        fields=["id"],
        limit=1,
    )
    action_vals = {
        "name": action_name,
        "model_id": service_line_model["id"],
        "state": "code",
        "code": action_code,
    }
    if action_existing:
        action_id = action_existing[0]["id"]
        client.write("ir.actions.server", [action_id], action_vals)
    else:
        action_id = client.create("ir.actions.server", action_vals)

    field_recs = client.search_read(
        "ir.model.fields",
        domain=[["model", "=", WIZ_SERVICE_LINE_MODEL], ["name", "in", ["x_price", "x_is_group", "x_line_id"]]],
        fields=["id"],
        limit=20,
    )
    field_ids = [r["id"] for r in field_recs]

    automation_name = "WTK - Auto precio pax servicios"
    automation_existing = client.search_read(
        "base.automation",
        domain=[["name", "=", automation_name], ["model_id", "=", service_line_model["id"]]],
        fields=["id"],
        limit=1,
    )
    automation_vals = {
        "name": automation_name,
        "model_id": service_line_model["id"],
        "trigger": "on_change",
        "active": True,
        "on_change_field_ids": [(6, 0, field_ids)],
        "action_server_ids": [(6, 0, [action_id])],
    }
    if automation_existing:
        client.write("base.automation", [automation_existing[0]["id"]], automation_vals)
    else:
        client.create("base.automation", automation_vals)

def _upsert_wizard_passenger_qty_sync(client: OdooClient, wizard_model: dict) -> None:
    action_name = "WTK - Sync pax qty en lineas"
    action_code = """
target_records = records or record
if target_records:
    for wiz in target_records:
        pax_qty = wiz.x_passenger_qty or 1
        for line in wiz.x_line_ids:
            line.write({'x_passenger_qty': pax_qty})
""".strip()

    action_existing = client.search_read(
        "ir.actions.server",
        domain=[["name", "=", action_name], ["model_id", "=", wizard_model["id"]]],
        fields=["id"],
        limit=1,
    )
    action_vals = {"name": action_name, "model_id": wizard_model["id"], "state": "code", "code": action_code}
    if action_existing:
        action_id = action_existing[0]["id"]
        client.write("ir.actions.server", [action_id], action_vals)
    else:
        action_id = client.create("ir.actions.server", action_vals)

    field_recs = client.search_read(
        "ir.model.fields",
        domain=[["model", "=", WIZ_MODEL], ["name", "=", "x_passenger_qty"]],
        fields=["id"],
        limit=1,
    )
    field_ids = [r["id"] for r in field_recs]
    if not field_ids:
        return

    automation_name = "WTK - Auto sync pax qty lineas"
    automation_existing = client.search_read(
        "base.automation",
        domain=[["name", "=", automation_name], ["model_id", "=", wizard_model["id"]]],
        fields=["id"],
        limit=1,
    )
    automation_vals = {
        "name": automation_name,
        "model_id": wizard_model["id"],
        "trigger": "on_change",
        "active": True,
        "on_change_field_ids": [(6, 0, field_ids)],
        "action_server_ids": [(6, 0, [action_id])],
    }
    if automation_existing:
        client.write("base.automation", [automation_existing[0]["id"]], automation_vals)
    else:
        client.create("base.automation", automation_vals)

def _upsert_wizard_cost_totals_automation(client: OdooClient, wizard_model: dict, service_line_model: dict) -> None:
    # Recalcula costos en wizard al cambiar costos fijos/variables o líneas
    wiz_action_name = "WTK - Recalcular costos wizard"
    wiz_action_code = """
target_records = records or record
if target_records:
    for wiz in target_records:
        op_cost = sum((wiz.x_line_ids.mapped('x_service_line_ids').mapped('x_price_pax')))
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
        })
""".strip()

    wiz_action_existing = client.search_read(
        "ir.actions.server",
        domain=[["name", "=", wiz_action_name], ["model_id", "=", wizard_model["id"]]],
        fields=["id"],
        limit=1,
    )
    wiz_action_vals = {
        "name": wiz_action_name,
        "model_id": wizard_model["id"],
        "state": "code",
        "code": wiz_action_code,
    }
    if wiz_action_existing:
        wiz_action_id = wiz_action_existing[0]["id"]
        client.write("ir.actions.server", [wiz_action_id], wiz_action_vals)
    else:
        wiz_action_id = client.create("ir.actions.server", wiz_action_vals)

    wiz_fields = client.search_read(
        "ir.model.fields",
        domain=[["model", "=", WIZ_MODEL], ["name", "in", [
            "x_fixed_cost",
            "x_variable_cost",
            "x_line_ids",
            "x_profit_pct",
            "x_apply_igv",
            "x_igv_pct",
            "x_apply_renta",
            "x_renta_pct",
            "x_card_commission_pct",
        ]]],
        fields=["id"],
        limit=100,
    )
    wiz_field_ids = [r["id"] for r in wiz_fields]

    wiz_auto_name = "WTK - Auto recalcular costos wizard"
    wiz_auto_existing = client.search_read(
        "base.automation",
        domain=[["name", "=", wiz_auto_name], ["model_id", "=", wizard_model["id"]]],
        fields=["id"],
        limit=1,
    )
    wiz_auto_vals = {
        "name": wiz_auto_name,
        "model_id": wizard_model["id"],
        "trigger": "on_change",
        "active": True,
        "on_change_field_ids": [(6, 0, wiz_field_ids)],
        "action_server_ids": [(6, 0, [wiz_action_id])],
    }
    if wiz_auto_existing:
        client.write("base.automation", [wiz_auto_existing[0]["id"]], wiz_auto_vals)
    else:
        client.create("base.automation", wiz_auto_vals)

    # Recalcula wizard cuando cambia una línea de servicio (precio pax)
    svc_action_name = "WTK - Recalcular costos wizard desde servicio"
    svc_action_code = """
target_records = records or record
if target_records:
    for svc in target_records:
        line = svc.x_line_id
        wiz = line.x_wizard_id if line else False
        if wiz:
            op_cost = sum((wiz.x_line_ids.mapped('x_service_line_ids').mapped('x_price_pax')))
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
            })
""".strip()

    svc_action_existing = client.search_read(
        "ir.actions.server",
        domain=[["name", "=", svc_action_name], ["model_id", "=", service_line_model["id"]]],
        fields=["id"],
        limit=1,
    )
    svc_action_vals = {
        "name": svc_action_name,
        "model_id": service_line_model["id"],
        "state": "code",
        "code": svc_action_code,
    }
    if svc_action_existing:
        svc_action_id = svc_action_existing[0]["id"]
        client.write("ir.actions.server", [svc_action_id], svc_action_vals)
    else:
        svc_action_id = client.create("ir.actions.server", svc_action_vals)

    svc_fields = client.search_read(
        "ir.model.fields",
        domain=[["model", "=", WIZ_SERVICE_LINE_MODEL], ["name", "in", ["x_price_pax", "x_line_id"]]],
        fields=["id"],
        limit=20,
    )
    svc_field_ids = [r["id"] for r in svc_fields]

    svc_auto_name = "WTK - Auto costos wizard desde servicio"
    svc_auto_existing = client.search_read(
        "base.automation",
        domain=[["name", "=", svc_auto_name], ["model_id", "=", service_line_model["id"]]],
        fields=["id"],
        limit=1,
    )
    svc_auto_vals = {
        "name": svc_auto_name,
        "model_id": service_line_model["id"],
        "trigger": "on_change",
        "active": True,
        "on_change_field_ids": [(6, 0, svc_field_ids)],
        "action_server_ids": [(6, 0, [svc_action_id])],
    }
    if svc_auto_existing:
        client.write("base.automation", [svc_auto_existing[0]["id"]], svc_auto_vals)
    else:
        client.create("base.automation", svc_auto_vals)

def _upsert_tax_exclusive_automations(client: OdooClient, wizard_model: dict) -> None:
    igv_action_name = "WTK - Exclusivo IGV"
    igv_code = """
target_records = records or record
if target_records:
    for wiz in target_records:
        if wiz.x_apply_igv and wiz.x_apply_renta:
            wiz.write({'x_apply_renta': False})
""".strip()
    igv_action = client.search_read(
        "ir.actions.server",
        domain=[["name", "=", igv_action_name], ["model_id", "=", wizard_model["id"]]],
        fields=["id"],
        limit=1,
    )
    igv_vals = {"name": igv_action_name, "model_id": wizard_model["id"], "state": "code", "code": igv_code}
    if igv_action:
        igv_action_id = igv_action[0]["id"]
        client.write("ir.actions.server", [igv_action_id], igv_vals)
    else:
        igv_action_id = client.create("ir.actions.server", igv_vals)

    igv_field = client.search_read(
        "ir.model.fields",
        domain=[["model", "=", WIZ_MODEL], ["name", "=", "x_apply_igv"]],
        fields=["id"],
        limit=1,
    )
    if igv_field:
        igv_auto_name = "WTK - Auto exclusivo IGV"
        igv_auto = client.search_read(
            "base.automation",
            domain=[["name", "=", igv_auto_name], ["model_id", "=", wizard_model["id"]]],
            fields=["id"],
            limit=1,
        )
        igv_auto_vals = {
            "name": igv_auto_name,
            "model_id": wizard_model["id"],
            "trigger": "on_change",
            "active": True,
            "on_change_field_ids": [(6, 0, [igv_field[0]["id"]])],
            "action_server_ids": [(6, 0, [igv_action_id])],
        }
        if igv_auto:
            client.write("base.automation", [igv_auto[0]["id"]], igv_auto_vals)
        else:
            client.create("base.automation", igv_auto_vals)

    renta_action_name = "WTK - Exclusivo Renta"
    renta_code = """
target_records = records or record
if target_records:
    for wiz in target_records:
        if wiz.x_apply_renta and wiz.x_apply_igv:
            wiz.write({'x_apply_igv': False})
""".strip()
    renta_action = client.search_read(
        "ir.actions.server",
        domain=[["name", "=", renta_action_name], ["model_id", "=", wizard_model["id"]]],
        fields=["id"],
        limit=1,
    )
    renta_vals = {"name": renta_action_name, "model_id": wizard_model["id"], "state": "code", "code": renta_code}
    if renta_action:
        renta_action_id = renta_action[0]["id"]
        client.write("ir.actions.server", [renta_action_id], renta_vals)
    else:
        renta_action_id = client.create("ir.actions.server", renta_vals)

    renta_field = client.search_read(
        "ir.model.fields",
        domain=[["model", "=", WIZ_MODEL], ["name", "=", "x_apply_renta"]],
        fields=["id"],
        limit=1,
    )
    if renta_field:
        renta_auto_name = "WTK - Auto exclusivo Renta"
        renta_auto = client.search_read(
            "base.automation",
            domain=[["name", "=", renta_auto_name], ["model_id", "=", wizard_model["id"]]],
            fields=["id"],
            limit=1,
        )
        renta_auto_vals = {
            "name": renta_auto_name,
            "model_id": wizard_model["id"],
            "trigger": "on_change",
            "active": True,
            "on_change_field_ids": [(6, 0, [renta_field[0]["id"]])],
            "action_server_ids": [(6, 0, [renta_action_id])],
        }
        if renta_auto:
            client.write("base.automation", [renta_auto[0]["id"]], renta_auto_vals)
        else:
            client.create("base.automation", renta_auto_vals)

def run(client: OdooClient, wizard_model: dict, wizard_service_line_model: dict):
    print("-> Configurando lógica y automatizaciones...")
    _upsert_wizard_passenger_qty_sync(client, wizard_model)
    _upsert_service_price_pax_onchange(client, wizard_service_line_model)
    _upsert_wizard_cost_totals_automation(client, wizard_model, wizard_service_line_model)
    _upsert_tax_exclusive_automations(client, wizard_model)

if __name__ == "__main__":
    client = OdooClient()
    client.connect()
    wizard_model = _get_model(client, WIZ_MODEL)
    wizard_service_line_model = _get_model(client, WIZ_SERVICE_LINE_MODEL)
    run(client, wizard_model, wizard_service_line_model)
