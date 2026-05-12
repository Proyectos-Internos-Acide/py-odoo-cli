from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from odoo_cli import OdooClient
from constants import *
from constants import _get_model

def _upsert_wizard_view(client: OdooClient, model: dict, print_action_id: int) -> int:
    arch_db = f"""
<form string="Cotización personalizada" create="true" edit="true">
    <sheet>
        <group col="2">
            <field name="x_sale_order_id" readonly="1"/>
            <field name="x_passenger_qty"/>
        </group>
        <separator string="Productos para cotización custom"/>
        <group col="1">
            <field name="x_line_ids" nolabel="1" colspan="4" mode="list,form" context="{{'default_x_passenger_qty': x_passenger_qty}}">
                <list>
                    <field name="x_service_date" string="Fecha"/>
                    <field name="x_product_id" string="Producto"/>
                </list>
                <form>
                    <group col="1">
                        <field name="x_passenger_qty" invisible="1"/>
                        <field name="x_service_date"/>
                        <field name="x_product_id"/>
                        <separator string="Servicios incluidos"/>
                        <field name="x_service_line_ids" nolabel="1" mode="list,form">
                            <list editable="bottom">
                                <field name="x_name" string="Servicio"/>
                                <field name="x_price" string="Precio (USD)"/>
                                <field name="x_is_group" string="¿Grupal?"/>
                                <field name="x_price_pax" string="PRECIO PAX" readonly="1"/>
                            </list>
                            <form>
                                <group col="1">
                                    <field name="x_name"/>
                                    <field name="x_price"/>
                                    <field name="x_is_group"/>
                                    <field name="x_price_pax" readonly="1"/>
                                </group>
                            </form>
                        </field>
                    </group>
                </form>
            </field>
        </group>
        <separator string="Resumen de costos"/>
        <group col="2">
            <group col="1">
                <group col="2">
                    <label for="x_operational_cost_pax" string="Costo operativo por PAX (USD)"/>
                    <field name="x_operational_cost_pax" nolabel="1" readonly="1"/>
                    <label for="x_fixed_cost" string="Costo fijo / gastos administrativos (USD)"/>
                    <field name="x_fixed_cost" nolabel="1"/>
                    <label for="x_variable_cost" string="Costo variable / otros gastos (USD)"/>
                    <field name="x_variable_cost" nolabel="1"/>
                    <label for="x_total_cost" string="Total costos (USD)"/>
                    <field name="x_total_cost" nolabel="1" readonly="1"/>
                </group>
            </group>
            <group col="1">
                <group col="2">
                    <label for="x_profit_pct" string="Utilidad (%)"/>
                    <field name="x_profit_pct" nolabel="1"/>
                    <label for="x_profit_amount" string="Utilidad (USD)"/>
                    <field name="x_profit_amount" nolabel="1" readonly="1"/>
                    <label for="x_subtotal_amount" string="Subtotal (USD)"/>
                    <field name="x_subtotal_amount" nolabel="1" readonly="1"/>
                </group>
                <separator string="Impuesto (seleccionar uno)"/>
                <group col="2">
                    <label for="x_apply_igv" string="Aplicar IGV"/>
                    <field name="x_apply_igv" nolabel="1"/>
                    <label for="x_igv_pct" string="IGV (%)"/>
                    <field name="x_igv_pct" nolabel="1"/>
                    <label for="x_apply_renta" string="Aplicar Renta a la utilidad"/>
                    <field name="x_apply_renta" nolabel="1"/>
                    <label for="x_renta_pct" string="Renta (%)"/>
                    <field name="x_renta_pct" nolabel="1"/>
                </group>
                <group col="2">
                    <label for="x_tax_amount" string="Monto impuesto (USD)"/>
                    <field name="x_tax_amount" nolabel="1" readonly="1"/>
                    <label for="x_subtotal_after_tax" string="Subtotal acumulado (USD)"/>
                    <field name="x_subtotal_after_tax" nolabel="1" readonly="1"/>
                    <label for="x_card_commission_pct" string="Comisión por tarjetas (%)"/>
                    <field name="x_card_commission_pct" nolabel="1"/>
                    <label for="x_card_commission_amount" string="Comisión tarjetas (USD)"/>
                    <field name="x_card_commission_amount" nolabel="1" readonly="1"/>
                    <label for="x_final_price" string="Precio final (USD)"/>
                    <field name="x_final_price" nolabel="1" readonly="1"/>
                </group>
            </group>
        </group>
    </sheet>
    <footer>
        <button string="Generar PDF" type="action" name="{print_action_id}" class="btn-primary"/>
        <button string="Cerrar" special="cancel"/>
    </footer>
</form>
""".strip()

    existing = client.search_read(
        "ir.ui.view",
        domain=[["name", "=", WIZ_VIEW_NAME], ["type", "=", "form"], ["model", "=", model["model"]]],
        fields=["id"],
        limit=1,
    )
    vals = {
        "name": WIZ_VIEW_NAME,
        "model": model["model"],
        "type": "form",
        "arch_db": arch_db,
        "active": True,
    }
    if existing:
        vid = existing[0]["id"]
        client.write("ir.ui.view", [vid], vals)
        return vid
    return client.create("ir.ui.view", vals)

def _upsert_sale_button_action(client: OdooClient, sale_order_model: dict, wizard_model: dict, wizard_view_id: int) -> int:
    code = f"""
ctx = dict(env.context or {{}})
if records:
    ctx.update({{
        'default_x_sale_order_id': records[0].id,
        'default_x_passenger_qty': 1,
        'default_x_profit_pct': 20.0,
        'default_x_apply_igv': True,
        'default_x_igv_pct': 18.0,
        'default_x_apply_renta': False,
        'default_x_renta_pct': 0.3,
        'default_x_card_commission_pct': 5.0,
    }})

action = {{
    'type': 'ir.actions.act_window',
    'name': 'Cotización personalizada',
    'res_model': '{wizard_model['model']}',
    'view_mode': 'form',
    'view_id': {wizard_view_id},
    'target': 'new',
    'context': dict(ctx, dialog_size='large'),
}}
""".strip()

    existing = client.search_read(
        "ir.actions.server",
        domain=[["name", "=", BTN_ACTION_NAME], ["model_id", "=", sale_order_model["id"]]],
        fields=["id"],
        limit=1,
    )
    vals = {"name": BTN_ACTION_NAME, "model_id": sale_order_model["id"], "state": "code", "code": code}
    if existing:
        aid = existing[0]["id"]
        client.write("ir.actions.server", [aid], vals)
        return aid
    return client.create("ir.actions.server", vals)

def _upsert_sale_form_button_view(client: OdooClient, action_id: int) -> int:
    base_xml = client.search_read(
        "ir.model.data",
        domain=[["module", "=", "sale"], ["name", "=", "view_order_form"], ["model", "=", "ir.ui.view"]],
        fields=["res_id"],
        limit=1,
    )
    if not base_xml:
        raise RuntimeError("No se encontró sale.view_order_form")
    base_view_id = base_xml[0]["res_id"]

    arch_db = f"""
<data inherit_id="sale.view_order_form">
    <xpath expr="//form/header/button[@name='action_quotation_send']" position="after">
        <button string="Cotización personalizada"
                type="action"
                name="{action_id}"
                class="btn-primary"
                style="background-color:#20603D !important;border-color:#20603D !important;color:#FFFFFF !important;"
                invisible="state not in ('draft','sent')"/>
    </xpath>
</data>
""".strip()

    existing = client.search_read(
        "ir.ui.view",
        domain=[["name", "=", BTN_VIEW_NAME], ["type", "=", "form"]],
        fields=["id"],
        limit=1,
    )
    vals = {
        "name": BTN_VIEW_NAME,
        "model": "sale.order",
        "type": "form",
        "mode": "extension",
        "active": True,
        "priority": 99,
        "inherit_id": base_view_id,
        "arch_db": arch_db,
    }
    if existing:
        vid = existing[0]["id"]
        client.write("ir.ui.view", [vid], vals)
        return vid
    return client.create("ir.ui.view", vals)

def run(client: OdooClient, wizard_model: dict, print_action_id: int):
    print("-> Configurando vistas y botones...")
    wizard_view_id = _upsert_wizard_view(client, wizard_model, print_action_id)
    sale_order_model = _get_model(client, "sale.order")
    sale_action_id = _upsert_sale_button_action(client, sale_order_model, wizard_model, wizard_view_id)
    sale_view_id = _upsert_sale_form_button_view(client, sale_action_id)
    return wizard_view_id, sale_action_id, sale_view_id

if __name__ == "__main__":
    client = OdooClient()
    client.connect()
    wizard_model = _get_model(client, WIZ_MODEL)
    print_action_id = client.search_read("ir.actions.server", [["name", "=", WIZ_PRINT_ACTION_NAME], ["model_id", "=", wizard_model["id"]]], fields=["id"], limit=1)[0]["id"]
    run(client, wizard_model, print_action_id)
