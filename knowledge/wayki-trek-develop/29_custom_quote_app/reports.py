from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from odoo_cli import OdooClient
from constants import *
from constants import _get_model

def _upsert_wizard_report_template(client: OdooClient) -> int:
    # Plantilla PDF custom Wayki Trek: cabecera de marca, tablas claras, resumen financiero.
    arch_db = """
<t t-name="wtk.report_custom_quote_document">
    <t t-call="web.html_container">
        <t t-foreach="docs" t-as="doc">
            <t t-set="wiz_cur" t-value="doc.x_sale_order_id.currency_id if (doc.x_sale_order_id and doc.x_sale_order_id.currency_id) else env['res.currency'].search([('name','=','USD')], limit=1)"/>
            <t t-call="web.external_layout">
                <div class="page" style="font-family: DejaVu Sans, Helvetica, Arial, sans-serif; color:#1a1a1a; font-size:11px; line-height:1.45;">
                    <table style="width:100%; border-collapse:collapse; margin-bottom:16px;">
                        <tr>
                            <td style="vertical-align:middle; padding:12px 14px; background:#20603D; color:#ffffff;">
                                <div style="font-size:18px; font-weight:bold; letter-spacing:0.3px;">Cotización personalizada</div>
                                <div style="font-size:10px; opacity:0.92; margin-top:4px;">Wayki Trek · Documento de referencia</div>
                            </td>
                        </tr>
                    </table>
                    <table style="width:100%; border-collapse:collapse; margin-bottom:18px; border:none;">
                        <tr>
                            <td style="width:50%; padding:10px 12px; vertical-align:top; border-right:none; background:#fafafa;">
                                <div style="font-size:9px; text-transform:uppercase; color:#6b7280; letter-spacing:0.5px;">Cotización</div>
                                <div style="font-size:13px; font-weight:bold; color:#20603D;">
                                    <span t-if="doc.x_sale_order_id" t-field="doc.x_sale_order_id.name"/>
                                    <span t-else="">—</span>
                                </div>
                                <div t-if="doc.x_sale_order_id and doc.x_sale_order_id.partner_id" style="margin-top:8px; font-size:10px; color:#374151;">
                                    <span t-field="doc.x_sale_order_id.partner_id.name"/>
                                </div>
                            </td>
                            <td style="width:50%; padding:10px 12px; vertical-align:top; background:#fafafa;">
                                <table style="width:100%; font-size:10px;">
                                    <tr>
                                        <td style="color:#6b7280; padding:2px 0;">Pasajeros (PAX)</td>
                                        <td style="text-align:right; font-weight:bold;"><span t-field="doc.x_passenger_qty"/></td>
                                    </tr>
                                    <tr t-if="doc.x_sale_order_id">
                                        <td style="color:#6b7280; padding:2px 0;">Moneda</td>
                                        <td style="text-align:right; font-weight:bold;"><span t-out="wiz_cur.display_name"/></td>
                                    </tr>
                                </table>
                            </td>
                        </tr>
                    </table>
                    <div style="margin-bottom:8px;">
                        <span style="display:inline-block; font-size:12px; font-weight:bold; color:#20603D; border-bottom:2px solid #20603D; padding-bottom:2px;">Productos y servicios incluidos</span>
                    </div>
                    <table style="width:100%; border-collapse:collapse; font-size:10px; border:1px solid #cbd5e1;">
                        <thead>
                            <tr style="background:#20603D; color:#ffffff;">
                                <th style="text-align:center; width:88px; padding:8px 6px; font-weight:bold;">Fecha</th>
                                <th style="text-align:left; width:200px; padding:8px 6px; font-weight:bold;">Producto</th>
                                <th style="text-align:left; padding:8px 6px; font-weight:bold;">Servicio incluido</th>
                                <th style="text-align:right; width:88px; padding:8px 6px; font-weight:bold;">Precio USD</th>
                                <th style="text-align:center; width:56px; padding:8px 6px; font-weight:bold;">Grupal</th>
                                <th style="text-align:right; width:88px; padding:8px 6px; font-weight:bold;">PAX USD</th>
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
                                                <td style="text-align:center; padding:7px 6px; border:1px solid #e5e7eb; vertical-align:top;">
                                                    <span t-if="svc_index == 0">
                                                        <span t-field="line.x_service_date"/>
                                                    </span>
                                                </td>
                                                <td style="padding:7px 6px; border:1px solid #e5e7eb; vertical-align:top;">
                                                    <span t-if="svc_index == 0">
                                                        <span t-if="line.x_product_id" t-field="line.x_product_id.display_name"/>
                                                        <span t-else="">—</span>
                                                    </span>
                                                </td>
                                                <td style="padding:7px 6px; border:1px solid #e5e7eb; vertical-align:top;">
                                                    <span t-field="svc.x_name"/>
                                                </td>
                                                <td style="text-align:right; padding:7px 6px; border:1px solid #e5e7eb; vertical-align:top;">
                                                    <span t-out="svc_price" t-options="{'widget': 'monetary', 'display_currency': wiz_cur}"/>
                                                </td>
                                                <td style="text-align:center; padding:7px 6px; border:1px solid #e5e7eb; vertical-align:top;">
                                                    <span t-if="svc.x_is_group">Sí</span>
                                                    <span t-else="">No</span>
                                                </td>
                                                <td style="text-align:right; padding:7px 6px; border:1px solid #e5e7eb; vertical-align:top;">
                                                    <span t-out="svc_price_pax" t-options="{'widget': 'monetary', 'display_currency': wiz_cur}"/>
                                                </td>
                                            </tr>
                                        </t>
                                    </t>
                                    <t t-else="">
                                        <tr>
                                            <td style="text-align:center; padding:7px 6px; border:1px solid #e5e7eb;">
                                                <span t-field="line.x_service_date"/>
                                            </td>
                                            <td style="padding:7px 6px; border:1px solid #e5e7eb;">
                                                <span t-if="line.x_product_id" t-field="line.x_product_id.display_name"/>
                                                <span t-else="">—</span>
                                            </td>
                                            <td style="padding:7px 6px; border:1px solid #e5e7eb; color:#9ca3af; font-style:italic;">
                                                Sin servicios incluidos
                                            </td>
                                            <td style="text-align:center; padding:7px 6px; border:1px solid #e5e7eb;">—</td>
                                            <td style="text-align:center; padding:7px 6px; border:1px solid #e5e7eb;">—</td>
                                            <td style="text-align:right; padding:7px 6px; border:1px solid #e5e7eb;">—</td>
                                        </tr>
                                    </t>
                                </t>
                            </t>
                            <t t-else="">
                                <tr>
                                    <td colspan="6" style="padding:14px; text-align:center; color:#6b7280; border:1px solid #e5e7eb;">
                                        Sin productos agregados en esta cotización personalizada.
                                    </td>
                                </tr>
                            </t>
                        </tbody>
                    </table>
                    <t t-if="doc.x_line_ids">
                        <table style="width:100%; margin-top:10px; margin-bottom:22px;">
                            <tr>
                                <td style="text-align:right; padding:8px 0;">
                                    <span style="font-size:11px; color:#374151;">Total servicios (suma precios):</span>
                                    <span style="font-size:13px; font-weight:bold; color:#20603D; margin-left:10px;" t-out="grand_total" t-options="{'widget': 'monetary', 'display_currency': wiz_cur}"/>
                                </td>
                            </tr>
                        </table>
                    </t>
                    <div style="margin-top:6px; margin-bottom:8px;">
                        <span style="display:inline-block; font-size:12px; font-weight:bold; color:#20603D; border-bottom:2px solid #20603D; padding-bottom:2px;">Resumen financiero</span>
                    </div>
                    <table style="width:100%; max-width:100%; border-collapse:collapse; font-size:10px; border:1px solid #cbd5e1;">
                        <tr style="background:#f3f4f6;">
                            <td colspan="2" style="padding:8px 10px; font-weight:bold; color:#20603D;">Costos y márgenes</td>
                        </tr>
                        <tr><td style="padding:7px 10px; border:1px solid #e5e7eb;">Costo operativo por PAX (suma precios PAX)</td>
                            <td style="padding:7px 10px; border:1px solid #e5e7eb; text-align:right; width:120px;"><span t-out="doc.x_operational_cost_pax" t-options="{'widget': 'monetary', 'display_currency': wiz_cur}"/></td></tr>
                        <tr><td style="padding:7px 10px; border:1px solid #e5e7eb;">Costo fijo / administrativos</td>
                            <td style="padding:7px 10px; border:1px solid #e5e7eb; text-align:right;"><span t-out="doc.x_fixed_cost" t-options="{'widget': 'monetary', 'display_currency': wiz_cur}"/></td></tr>
                        <tr><td style="padding:7px 10px; border:1px solid #e5e7eb;">Costo variable / otros</td>
                            <td style="padding:7px 10px; border:1px solid #e5e7eb; text-align:right;"><span t-out="doc.x_variable_cost" t-options="{'widget': 'monetary', 'display_currency': wiz_cur}"/></td></tr>
                        <tr style="background:#ecfdf5;">
                            <td style="padding:7px 10px; border:1px solid #e5e7eb;"><strong>Total costos</strong></td>
                            <td style="padding:7px 10px; border:1px solid #e5e7eb; text-align:right;"><strong><span t-out="doc.x_total_cost" t-options="{'widget': 'monetary', 'display_currency': wiz_cur}"/></strong></td></tr>
                        <tr><td style="padding:7px 10px; border:1px solid #e5e7eb;">Utilidad estimada</td>
                            <td style="padding:7px 10px; border:1px solid #e5e7eb; text-align:right;"><span t-out="doc.x_profit_amount" t-options="{'widget': 'monetary', 'display_currency': wiz_cur}"/></td></tr>
                        <tr><td style="padding:7px 10px; border:1px solid #e5e7eb;"><strong>Subtotal</strong></td>
                            <td style="padding:7px 10px; border:1px solid #e5e7eb; text-align:right;"><strong><span t-out="doc.x_subtotal_amount" t-options="{'widget': 'monetary', 'display_currency': wiz_cur}"/></strong></td></tr>
                        <tr><td style="padding:7px 10px; border:1px solid #e5e7eb;">Impuesto (IGV o renta)</td>
                            <td style="padding:7px 10px; border:1px solid #e5e7eb; text-align:right;"><span t-out="doc.x_tax_amount" t-options="{'widget': 'monetary', 'display_currency': wiz_cur}"/></td></tr>
                        <tr><td style="padding:7px 10px; border:1px solid #e5e7eb;"><strong>Subtotal acumulado</strong></td>
                            <td style="padding:7px 10px; border:1px solid #e5e7eb; text-align:right;"><strong><span t-out="doc.x_subtotal_after_tax" t-options="{'widget': 'monetary', 'display_currency': wiz_cur}"/></strong></td></tr>
                        <tr><td style="padding:7px 10px; border:1px solid #e5e7eb;">Comisión tarjetas</td>
                            <td style="padding:7px 10px; border:1px solid #e5e7eb; text-align:right;"><span t-out="doc.x_card_commission_amount" t-options="{'widget': 'monetary', 'display_currency': wiz_cur}"/></td></tr>
                        <tr style="background:#20603D; color:#ffffff;">
                            <td style="padding:10px 10px; border:none; font-size:11px;"><strong>PRECIO FINAL</strong></td>
                            <td style="padding:10px 10px; border:none; text-align:right; font-size:14px;"><strong><span t-out="doc.x_final_price" t-options="{'widget': 'monetary', 'display_currency': wiz_cur}"/></strong></td></tr>
                    </table>
                    <p style="margin-top:22px; padding-top:12px; border-top:1px solid #e5e7eb; color:#6b7280; font-size:9px; text-align:center;">
                        Documento informativo generado desde Cotización personalizada · Wayki Trek · No constituye comprobante fiscal.
                    </p>
                </div>
            </t>
        </t>
    </t>
</t>
""".strip()

    # Odoo resuelve la plantilla del PDF por ``key`` (debe coincidir con ir.actions.report.report_name).
    existing = client.search_read(
        "ir.ui.view",
        domain=[["key", "=", WIZ_REPORT_TEMPLATE_NAME], ["type", "=", "qweb"]],
        fields=["id"],
        limit=1,
    )
    if not existing:
        existing = client.search_read(
            "ir.ui.view",
            domain=[["name", "=", WIZ_REPORT_TEMPLATE_NAME], ["type", "=", "qweb"]],
            fields=["id"],
            limit=1,
        )
    vals = {
        "name": WIZ_REPORT_TEMPLATE_NAME,
        "key": WIZ_REPORT_TEMPLATE_NAME,
        "type": "qweb",
        "arch_db": arch_db,
        "active": True,
        "mode": "primary",
    }
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

        # 1. Recalcular x_price_pax por servicio
        for line in wizard.x_line_ids:
            for svc in line.x_service_line_ids:
                price = svc.x_price or 0.0
                if svc.x_is_group:
                    svc.write({{'x_price_pax': (price / pax_qty) if pax_qty else price}})
                else:
                    svc.write({{'x_price_pax': price}})

        # 2. Calcular resumen financiero completo (no depender del on_change del frontend)
        op_cost = sum(
            svc.x_price_pax or 0.0
            for line in wizard.x_line_ids
            for svc in line.x_service_line_ids
        )
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

        tax_rate = 0.0
        if wizard.x_apply_igv:
            tax_rate = igv_rate
        elif wizard.x_apply_renta:
            tax_rate = renta_rate

        tax_amount = subtotal * tax_rate
        subtotal_with_tax = subtotal + tax_amount

        card_pct_raw = wizard.x_card_commission_pct if wizard.x_card_commission_pct is not None else 5.0
        card_rate = (card_pct_raw / 100.0) if card_pct_raw > 1 else card_pct_raw
        card_commission = subtotal_with_tax * card_rate
        final_price = subtotal_with_tax + card_commission

        # 3. Persistir los valores calculados en la DB antes de renderizar el PDF
        wizard.write({{
            'x_operational_cost_pax': op_cost,
            'x_total_cost': total_cost,
            'x_profit_amount': profit_amount,
            'x_subtotal_amount': subtotal,
            'x_tax_amount': tax_amount,
            'x_subtotal_after_tax': subtotal_with_tax,
            'x_card_commission_amount': card_commission,
            'x_final_price': final_price,
        }})

    # 4. Ahora sí generar el PDF con los valores reales
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



def _upsert_client_report_template(client: OdooClient) -> int:
    """Plantilla PDF cliente: mismo formato que el interno, sin columnas de precios ni resumen financiero."""
    arch_db = """
<t t-name="wtk.report_custom_quote_client">
    <t t-call="web.html_container">
        <t t-foreach="docs" t-as="doc">
            <t t-set="wiz_cur" t-value="doc.x_sale_order_id.currency_id if (doc.x_sale_order_id and doc.x_sale_order_id.currency_id) else env['res.currency'].search([('name','=','USD')], limit=1)"/>
            <t t-call="web.external_layout">
                <div class="page" style="font-family: DejaVu Sans, Helvetica, Arial, sans-serif; color:#1a1a1a; font-size:11px; line-height:1.45;">
                    <table style="width:100%; border-collapse:collapse; margin-bottom:16px;">
                        <tr>
                            <td style="vertical-align:middle; padding:12px 14px; background:#20603D; color:#ffffff;">
                                <div style="font-size:18px; font-weight:bold; letter-spacing:0.3px;">Cotización personalizada</div>
                                <div style="font-size:10px; opacity:0.92; margin-top:4px;">Wayki Trek · Documento de referencia</div>
                            </td>
                        </tr>
                    </table>
                    <table style="width:100%; border-collapse:collapse; margin-bottom:18px; border:1px solid #d1d5db;">
                        <tr>
                            <td style="width:50%; padding:10px 12px; vertical-align:top; border-right:1px solid #e5e7eb; background:#fafafa;">
                                <div style="font-size:9px; text-transform:uppercase; color:#6b7280; letter-spacing:0.5px;">Cotización</div>
                                <div style="font-size:13px; font-weight:bold; color:#20603D;">
                                    <span t-if="doc.x_sale_order_id" t-field="doc.x_sale_order_id.name"/>
                                    <span t-else="">—</span>
                                </div>
                                <div t-if="doc.x_sale_order_id and doc.x_sale_order_id.partner_id" style="margin-top:8px; font-size:10px; color:#374151;">
                                    <span t-field="doc.x_sale_order_id.partner_id.name"/>
                                </div>
                            </td>
                            <td style="width:50%; padding:10px 12px; vertical-align:top; background:#fafafa;">
                                <table style="width:100%; font-size:10px;">
                                    <tr>
                                        <td style="color:#6b7280; padding:2px 0;">Pasajeros (PAX)</td>
                                        <td style="text-align:right; font-weight:bold;"><span t-field="doc.x_passenger_qty"/></td>
                                    </tr>
                                    <tr t-if="doc.x_sale_order_id">
                                        <td style="color:#6b7280; padding:2px 0;">Moneda</td>
                                        <td style="text-align:right; font-weight:bold;"><span t-out="wiz_cur.display_name"/></td>
                                    </tr>
                                </table>
                            </td>
                        </tr>
                    </table>
                    <div style="margin-bottom:8px;">
                        <span style="display:inline-block; font-size:12px; font-weight:bold; color:#20603D; border-bottom:2px solid #20603D; padding-bottom:2px;">Productos y servicios incluidos</span>
                    </div>
                    <table style="width:100%; border-collapse:collapse; font-size:10px; border:1px solid #cbd5e1;">
                        <thead>
                            <tr style="background:#20603D; color:#ffffff;">
                                <th style="text-align:center; width:88px; padding:8px 6px; font-weight:bold;">Fecha</th>
                                <th style="text-align:left; width:220px; padding:8px 6px; font-weight:bold;">Producto</th>
                                <th style="text-align:left; padding:8px 6px; font-weight:bold;">Servicio incluido</th>
                            </tr>
                        </thead>
                        <tbody>
                            <t t-if="doc.x_line_ids">
                                <t t-foreach="doc.x_line_ids" t-as="line">
                                    <t t-if="line.x_service_line_ids">
                                        <t t-foreach="line.x_service_line_ids" t-as="svc">
                                            <tr>
                                                <td style="text-align:center; padding:7px 6px; border:1px solid #e5e7eb; vertical-align:top;">
                                                    <span t-if="svc_index == 0"><span t-field="line.x_service_date"/></span>
                                                </td>
                                                <td style="padding:7px 6px; border:1px solid #e5e7eb; vertical-align:top;">
                                                    <span t-if="svc_index == 0">
                                                        <span t-if="line.x_product_id" t-field="line.x_product_id.display_name"/>
                                                        <span t-else="">—</span>
                                                    </span>
                                                </td>
                                                <td style="padding:7px 6px; border:1px solid #e5e7eb; vertical-align:top;">
                                                    <span t-field="svc.x_name"/>
                                                </td>
                                            </tr>
                                        </t>
                                    </t>
                                    <t t-else="">
                                        <tr>
                                            <td style="text-align:center; padding:7px 6px; border:1px solid #e5e7eb;"><span t-field="line.x_service_date"/></td>
                                            <td style="padding:7px 6px; border:1px solid #e5e7eb;">
                                                <span t-if="line.x_product_id" t-field="line.x_product_id.display_name"/>
                                                <span t-else="">—</span>
                                            </td>
                                            <td style="padding:7px 6px; border:1px solid #e5e7eb; color:#9ca3af; font-style:italic;">Sin servicios incluidos</td>
                                        </tr>
                                    </t>
                                </t>
                            </t>
                            <t t-else="">
                                <tr>
                                    <td colspan="3" style="padding:14px; text-align:center; color:#6b7280; border:1px solid #e5e7eb;">
                                        Sin productos agregados en esta cotización personalizada.
                                    </td>
                                </tr>
                            </t>
                        </tbody>
                    </table>
                    <table style="width:100%; margin-top:10px; margin-bottom:8px;">
                        <tr>
                            <td style="text-align:right; padding:8px 0;">
                                <span style="font-size:11px; color:#374151;">Precio final:</span>
                                <span style="font-size:14px; font-weight:bold; color:#20603D; margin-left:10px;" t-out="doc.x_final_price" t-options="{'widget': 'monetary', 'display_currency': wiz_cur}"/>
                            </td>
                        </tr>
                    </table>
                    <p style="margin-top:22px; padding-top:12px; border-top:1px solid #e5e7eb; color:#6b7280; font-size:9px; text-align:center;">
                        Documento informativo generado desde Cotización personalizada · Wayki Trek · No constituye comprobante fiscal.
                    </p>
                </div>
            </t>
        </t>
    </t>
</t>
""".strip()

    existing = client.search_read(
        "ir.ui.view",
        domain=[["key", "=", WIZ_CLIENT_REPORT_TEMPLATE_NAME], ["type", "=", "qweb"]],
        fields=["id"], limit=1,
    )
    vals = {
        "name": WIZ_CLIENT_REPORT_TEMPLATE_NAME,
        "key": WIZ_CLIENT_REPORT_TEMPLATE_NAME,
        "type": "qweb",
        "arch_db": arch_db,
        "active": True,
        "mode": "primary",
    }
    if existing:
        client.write("ir.ui.view", [existing[0]["id"]], vals)
        return existing[0]["id"]
    return client.create("ir.ui.view", vals)

def _upsert_client_report_action(client: OdooClient, model: dict) -> int:
    existing = client.search_read(
        "ir.actions.report",
        domain=[["name", "=", WIZ_CLIENT_REPORT_ACTION_NAME], ["model", "=", model["model"]]],
        fields=["id"], limit=1,
    )
    vals = {
        "name": WIZ_CLIENT_REPORT_ACTION_NAME,
        "model": model["model"],
        "report_type": "qweb-pdf",
        "report_name": WIZ_CLIENT_REPORT_TEMPLATE_NAME,
        "report_file": WIZ_CLIENT_REPORT_TEMPLATE_NAME,
    }
    if existing:
        client.write("ir.actions.report", [existing[0]["id"]], vals)
        return existing[0]["id"]
    return client.create("ir.actions.report", vals)


def _upsert_client_print_action(client: OdooClient, model: dict) -> int:
    """Calcula el resumen financiero y genera el PDF para el cliente."""
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

        wizard.write({{
            'x_operational_cost_pax': op_cost,
            'x_total_cost': total_cost,
            'x_profit_amount': profit_amount,
            'x_subtotal_amount': subtotal,
            'x_tax_amount': tax_amount,
            'x_subtotal_after_tax': subtotal_with_tax,
            'x_card_commission_amount': card_commission,
            'x_final_price': final_price,
        }})

    report = env['ir.actions.report'].search([('name', '=', '{WIZ_CLIENT_REPORT_ACTION_NAME}'), ('model', '=', '{model['model']}')], limit=1)
    if report:
        action = report.report_action(records)
    else:
        action = {{
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {{'title': 'Cotización cliente', 'message': 'No se encontró el reporte PDF cliente.', 'type': 'warning', 'sticky': False}}
        }}
""".strip()

    existing = client.search_read(
        "ir.actions.server",
        domain=[["name", "=", WIZ_CLIENT_PRINT_ACTION_NAME], ["model_id", "=", model["id"]]],
        fields=["id"], limit=1,
    )
    vals = {"name": WIZ_CLIENT_PRINT_ACTION_NAME, "model_id": model["id"], "state": "code", "code": code}
    if existing:
        aid = existing[0]["id"]
        client.write("ir.actions.server", [aid], vals)
        return aid
    return client.create("ir.actions.server", vals)


def run(client: OdooClient, wizard_model: dict):
    print("-> Configurando reportes (QWeb y Acciones PDF)...")
    _upsert_wizard_report_template(client)
    _upsert_report_action(client, wizard_model)
    print_action_id = _upsert_wizard_print_action(client, wizard_model, WIZ_REPORT_ACTION_NAME)

    _upsert_client_report_template(client)
    _upsert_client_report_action(client, wizard_model)
    client_print_action_id = _upsert_client_print_action(client, wizard_model)

    return print_action_id, client_print_action_id

if __name__ == "__main__":
    client = OdooClient()
    client.connect()
    wizard_model = _get_model(client, WIZ_MODEL)
    run(client, wizard_model)
