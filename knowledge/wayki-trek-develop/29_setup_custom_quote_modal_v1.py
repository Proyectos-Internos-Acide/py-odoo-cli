#!/usr/bin/env python3
"""
V3 - Cotización personalizada desde botón en sale.order.

Incluye:
- Botón "Cotización personalizada" en cotización (verde branding).
- Apertura de modal (wizard) con:
  - Cantidad de pasajeros
  - Múltiples productos (líneas)
  - Servicios incluidos por cada producto (líneas con precio)
- Botón "Generar PDF" en el modal.

Nota:
- Esta versión NO persiste servicios incluidos en productos.
- El PDF sale desde el wizard (documento custom).
"""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from odoo_cli import OdooClient


BTN_ACTION_NAME = "WTK - Abrir modal cotización personalizada"
BTN_VIEW_NAME = "wtk.sale.order.form.custom.quote.button"

WIZ_MODEL = "x_wtk_custom_quote_wizard"
WIZ_MODEL_NAME = "WTK Custom Quote Wizard"
WIZ_LINE_MODEL = "x_wtk_custom_quote_wizard_line"
WIZ_LINE_MODEL_NAME = "WTK Custom Quote Wizard Line"
WIZ_SERVICE_LINE_MODEL = "x_wtk_custom_quote_wizard_service_line"
WIZ_SERVICE_LINE_MODEL_NAME = "WTK Custom Quote Wizard Service Line"
WIZ_VIEW_NAME = "wtk.custom.quote.wizard.form"
WIZ_REPORT_TEMPLATE_NAME = "wtk.report_custom_quote_document"
WIZ_REPORT_ACTION_NAME = "WTK - PDF Cotización personalizada"
WIZ_PRINT_ACTION_NAME = "WTK - Generar PDF desde wizard"


def _get_model(client: OdooClient, model_name: str) -> dict:
    rec = client.search_read("ir.model", domain=[["model", "=", model_name]], fields=["id", "model", "name"], limit=1)
    return rec[0] if rec else {}


def _ensure_model(client: OdooClient) -> dict:
    rec = _get_model(client, WIZ_MODEL)
    if rec:
        return rec
    model_id = client.create(
        "ir.model",
        {
            "name": WIZ_MODEL_NAME,
            "model": WIZ_MODEL,
            "state": "manual",
        },
    )
    return {"id": model_id, "model": WIZ_MODEL, "name": WIZ_MODEL_NAME}


def _ensure_line_model(client: OdooClient) -> dict:
    rec = _get_model(client, WIZ_LINE_MODEL)
    if rec:
        return rec
    model_id = client.create(
        "ir.model",
        {
            "name": WIZ_LINE_MODEL_NAME,
            "model": WIZ_LINE_MODEL,
            "state": "manual",
        },
    )
    return {"id": model_id, "model": WIZ_LINE_MODEL, "name": WIZ_LINE_MODEL_NAME}


def _ensure_service_line_model(client: OdooClient) -> dict:
    rec = _get_model(client, WIZ_SERVICE_LINE_MODEL)
    if rec:
        return rec
    model_id = client.create(
        "ir.model",
        {
            "name": WIZ_SERVICE_LINE_MODEL_NAME,
            "model": WIZ_SERVICE_LINE_MODEL,
            "state": "manual",
        },
    )
    return {"id": model_id, "model": WIZ_SERVICE_LINE_MODEL, "name": WIZ_SERVICE_LINE_MODEL_NAME}


def _ensure_field(
    client: OdooClient,
    model: dict,
    name: str,
    desc: str,
    ttype: str,
    relation: str | None = None,
    relation_field: str | None = None,
) -> int:
    existing = client.search_read(
        "ir.model.fields",
        domain=[["model", "=", model["model"]], ["name", "=", name]],
        fields=["id"],
        limit=1,
    )
    if existing:
        return existing[0]["id"]

    vals = {
        "name": name,
        "field_description": desc,
        "model_id": model["id"],
        "model": model["model"],
        "ttype": ttype,
        "state": "manual",
        "store": True,
    }
    if relation:
        vals["relation"] = relation
    if relation_field:
        vals["relation_field"] = relation_field
    return client.create("ir.model.fields", vals)


def _upsert_wizard_report_template(client: OdooClient) -> int:
    arch_db = """
<t t-name="wtk.report_custom_quote_document">
    <t t-call="web.html_container">
        <t t-foreach="docs" t-as="doc">
            <t t-call="web.external_layout">
                <div class="page">
                    <h2 style="color:#20603D;">Cotización personalizada</h2>
                    <p><strong>Oportunidad/Cotización:</strong>
                        <span t-if="doc.x_sale_order_id" t-field="doc.x_sale_order_id.name"/>
                        <span t-else="">-</span>
                    </p>
                    <p><strong>Cantidad de pasajeros:</strong> <span t-field="doc.x_passenger_qty"/></p>
                    <p><strong>Productos y servicios incluidos:</strong></p>
                    <div style="border:1px solid #ddd; padding:10px; min-height:60px;">
                        <table style="width:100%; border-collapse: collapse; font-size: 12px;">
                            <thead>
                                <tr style="background:#f3f4f6;">
                                    <th style="text-align:center; width:95px; padding:6px; border:1px solid #e5e7eb;">Fecha</th>
                                    <th style="text-align:left; width:220px; padding:6px; border:1px solid #e5e7eb;">Producto</th>
                                    <th style="text-align:left; padding:6px; border:1px solid #e5e7eb;">Servicios incluidos</th>
                                    <th style="text-align:right; width:110px; padding:6px; border:1px solid #e5e7eb;">Precio (USD)</th>
                                    <th style="text-align:center; width:90px; padding:6px; border:1px solid #e5e7eb;">¿Grupal?</th>
                                    <th style="text-align:right; width:110px; padding:6px; border:1px solid #e5e7eb;">Precio PAX (USD)</th>
                                </tr>
                            </thead>
                            <tbody>
                                <t t-if="doc.x_line_ids">
                                    <t t-set="grand_total" t-value="0.0"/>
                                    <t t-foreach="doc.x_line_ids" t-as="line">
                                        <t t-if="line.x_service_line_ids">
                                            <t t-foreach="line.x_service_line_ids" t-as="svc">
                                                <t t-set="svc_price" t-value="svc.x_price or 0.0"/>
                                                <t t-set="svc_price_pax" t-value="svc.x_price_pax or svc_price"/>
                                                <t t-set="grand_total" t-value="grand_total + svc_price"/>
                                                <tr>
                                                    <td style="text-align:center; padding:6px; border:1px solid #e5e7eb;">
                                                        <span t-if="svc_index == 0">
                                                            <span t-field="line.x_service_date"/>
                                                        </span>
                                                    </td>
                                                    <td style="padding:6px; border:1px solid #e5e7eb;">
                                                        <span t-if="svc_index == 0">
                                                            <span t-if="line.x_product_id" t-field="line.x_product_id.display_name"/>
                                                            <span t-else="">-</span>
                                                        </span>
                                                    </td>
                                                    <td style="padding:6px; border:1px solid #e5e7eb;">
                                                        <span t-field="svc.x_name"/>
                                                    </td>
                                                    <td style="text-align:right; padding:6px; border:1px solid #e5e7eb;">
                                                        <span t-out="svc_price" t-options="{'widget': 'monetary', 'display_currency': (doc.x_sale_order_id.currency_id if (doc.x_sale_order_id and doc.x_sale_order_id.currency_id) else env['res.currency'].search([('name','=','USD')], limit=1))}"/>
                                                    </td>
                                                    <td style="text-align:center; padding:6px; border:1px solid #e5e7eb;">
                                                        <span t-if="svc.x_is_group">Si</span>
                                                        <span t-else="">No</span>
                                                    </td>
                                                    <td style="text-align:right; padding:6px; border:1px solid #e5e7eb;">
                                                        <span t-out="svc_price_pax" t-options="{'widget': 'monetary', 'display_currency': (doc.x_sale_order_id.currency_id if (doc.x_sale_order_id and doc.x_sale_order_id.currency_id) else env['res.currency'].search([('name','=','USD')], limit=1))}"/>
                                                    </td>
                                                </tr>
                                            </t>
                                        </t>
                                        <t t-else="">
                                            <tr>
                                                <td style="text-align:center; padding:6px; border:1px solid #e5e7eb;">
                                                    <span t-field="line.x_service_date"/>
                                                </td>
                                                <td style="padding:6px; border:1px solid #e5e7eb;">
                                                    <span t-if="line.x_product_id" t-field="line.x_product_id.display_name"/>
                                                    <span t-else="">-</span>
                                                </td>
                                                <td style="padding:6px; border:1px solid #e5e7eb; color:#6b7280;">
                                                    Sin servicios incluidos.
                                                </td>
                                                <td style="text-align:center; padding:6px; border:1px solid #e5e7eb;">
                                                    -
                                                </td>
                                                <td style="text-align:right; padding:6px; border:1px solid #e5e7eb;">
                                                    -
                                                </td>
                                                <td style="text-align:right; padding:6px; border:1px solid #e5e7eb;">
                                                    -
                                                </td>
                                            </tr>
                                        </t>
                                    </t>
                                </t>
                                <t t-else="">
                                    <tr>
                                        <td colspan="4" style="padding:6px; border:1px solid #e5e7eb; color:#6b7280;">
                                            Sin productos agregados.
                                        </td>
                                    </tr>
                                </t>
                            </tbody>
                        </table>
                    </div>
                    <t t-if="doc.x_line_ids">
                        <p style="margin-top:12px; text-align:right;">
                            <strong>Total estimado (USD): </strong>
                            <span t-out="grand_total" t-options="{'widget': 'monetary', 'display_currency': (doc.x_sale_order_id.currency_id if (doc.x_sale_order_id and doc.x_sale_order_id.currency_id) else env['res.currency'].search([('name','=','USD')], limit=1))}"/>
                        </p>
                    </t>
                    <p style="margin-top:20px; color:#6b7280; font-size:11px;">
                        Documento preliminar - Wayki Trek
                    </p>
                </div>
            </t>
        </t>
    </t>
</t>
""".strip()

    existing = client.search_read(
        "ir.ui.view",
        domain=[["name", "=", WIZ_REPORT_TEMPLATE_NAME], ["type", "=", "qweb"]],
        fields=["id"],
        limit=1,
        # active_test not needed
    )
    vals = {"name": WIZ_REPORT_TEMPLATE_NAME, "type": "qweb", "arch_db": arch_db, "active": True}
    if existing:
        vid = existing[0]["id"]
        client.write("ir.ui.view", [vid], vals)
        return vid
    return client.create("ir.ui.view", vals)


def _upsert_report_action(client: OdooClient, model: dict) -> int:
    existing = client.search_read(
        "ir.actions.report",
        domain=[["name", "=", WIZ_REPORT_ACTION_NAME], ["model", "=", model["model"]]],
        fields=["id"],
        limit=1,
    )
    vals = {
        "name": WIZ_REPORT_ACTION_NAME,
        "model": model["model"],
        "report_type": "qweb-pdf",
        "report_name": WIZ_REPORT_TEMPLATE_NAME,
        "report_file": WIZ_REPORT_TEMPLATE_NAME,
    }
    if existing:
        rid = existing[0]["id"]
        client.write("ir.actions.report", [rid], vals)
        return rid
    return client.create("ir.actions.report", vals)


def _upsert_wizard_print_action(client: OdooClient, model: dict, report_name: str) -> int:
    code = f"""
if records:
    for wizard in records:
        pax_qty = wizard.x_passenger_qty or 1
        for line in wizard.x_line_ids:
            for svc in line.x_service_line_ids:
                price = svc.x_price or 0.0
                if svc.x_is_group:
                    svc.write({{'x_price_pax': (price / pax_qty) if pax_qty else price}})
                else:
                    svc.write({{'x_price_pax': price}})
    report = env['ir.actions.report'].search([('name', '=', '{report_name}'), ('model', '=', '{model['model']}')], limit=1)
    if report:
        action = report.report_action(records)
    else:
        action = {{
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {{
                'title': 'Cotización personalizada',
                'message': 'No se encontró el reporte PDF.',
                'type': 'warning',
                'sticky': False,
            }}
        }}
""".strip()

    existing = client.search_read(
        "ir.actions.server",
        domain=[["name", "=", WIZ_PRINT_ACTION_NAME], ["model_id", "=", model["id"]]],
        fields=["id"],
        limit=1,
    )
    vals = {"name": WIZ_PRINT_ACTION_NAME, "model_id": model["id"], "state": "code", "code": code}
    if existing:
        aid = existing[0]["id"]
        client.write("ir.actions.server", [aid], vals)
        return aid
    return client.create("ir.actions.server", vals)


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


def main() -> None:
    print("Configurando modal de cotización personalizada (V3)...")
    client = OdooClient()
    uid = client.connect()
    print(f"✅ Conectado (uid={uid})")

    wizard_model = _ensure_model(client)
    wizard_line_model = _ensure_line_model(client)
    wizard_service_line_model = _ensure_service_line_model(client)
    _ensure_field(client, wizard_model, "x_sale_order_id", "Cotización origen", "many2one", relation="sale.order")
    _ensure_field(client, wizard_model, "x_passenger_qty", "Cantidad de pasajeros", "integer")

    # Primero crear many2one del modelo línea, luego one2many del wizard.
    _ensure_field(client, wizard_line_model, "x_wizard_id", "Wizard", "many2one", relation=WIZ_MODEL)
    _ensure_field(client, wizard_line_model, "x_passenger_qty", "Cantidad pasajeros (snapshot)", "integer")
    _ensure_field(client, wizard_line_model, "x_service_date", "Fecha", "date")
    _ensure_field(client, wizard_line_model, "x_product_id", "Producto", "many2one", relation="product.product")
    _ensure_field(client, wizard_line_model, "x_qty", "Cantidad", "integer")
    _ensure_field(client, wizard_line_model, "x_unit_price", "Precio unitario", "float")
    _ensure_field(client, wizard_service_line_model, "x_line_id", "Línea de cotización", "many2one", relation=WIZ_LINE_MODEL)
    _ensure_field(client, wizard_service_line_model, "x_name", "Servicio incluido", "char")
    _ensure_field(client, wizard_service_line_model, "x_is_group", "¿Grupal?", "boolean")
    _ensure_field(client, wizard_service_line_model, "x_price", "Precio", "float")
    _ensure_field(client, wizard_service_line_model, "x_price_pax", "PRECIO PAX", "float")
    _ensure_field(
        client,
        wizard_line_model,
        "x_service_line_ids",
        "Servicios incluidos",
        "one2many",
        relation=WIZ_SERVICE_LINE_MODEL,
        relation_field="x_line_id",
    )
    _ensure_field(
        client,
        wizard_model,
        "x_line_ids",
        "Líneas custom",
        "one2many",
        relation=WIZ_LINE_MODEL,
        relation_field="x_wizard_id",
    )

    # ACL global para evitar error de acceso en modal
    for model_name in [WIZ_MODEL, WIZ_LINE_MODEL, WIZ_SERVICE_LINE_MODEL]:
        m = _get_model(client, model_name)
        existing_acl = client.execute(
            "ir.model.access",
            "search_read",
            [["model_id", "=", m["id"]], ["group_id", "=", False]],
            fields=["id"],
            limit=1,
            context={"active_test": False},
        )
        vals_acl = {
            "name": f"access_{model_name}_all",
            "model_id": m["id"],
            "perm_read": True,
            "perm_write": True,
            "perm_create": True,
            "perm_unlink": True,
        }
        if existing_acl:
            client.write("ir.model.access", [existing_acl[0]["id"]], vals_acl)
        else:
            client.create("ir.model.access", vals_acl)

    _upsert_wizard_report_template(client)
    _upsert_report_action(client, wizard_model)
    _upsert_wizard_passenger_qty_sync(client, wizard_model)
    _upsert_service_price_pax_onchange(client, wizard_service_line_model)
    print_action_id = _upsert_wizard_print_action(client, wizard_model, WIZ_REPORT_ACTION_NAME)
    wizard_view_id = _upsert_wizard_view(client, wizard_model, print_action_id)

    sale_order_model = _get_model(client, "sale.order")
    sale_action_id = _upsert_sale_button_action(client, sale_order_model, wizard_model, wizard_view_id)
    sale_view_id = _upsert_sale_form_button_view(client, sale_action_id)

    print(f"✅ Modelo wizard listo: {wizard_model['model']}")
    print(f"✅ Vista modal: {wizard_view_id}")
    print(f"✅ Acción abrir modal: {sale_action_id}")
    print(f"✅ Vista botón en cotización: {sale_view_id}")
    print("🎉 V3 lista.")


if __name__ == "__main__":
    main()
