#!/usr/bin/env python3
"""
Configura en cotizaciones (sale.order.line):
- Checkbox: ¿Cotización? (x_wtk_cotizacion)
- Campo: Precio custom (x_wtk_precio_custom)
- Checkbox tipo botón: Confirmar precio (x_wtk_confirmar_precio)

Comportamiento:
- Al marcar confirmar y tener cotización + precio custom, se aplica ese precio
  al price_unit de la línea.
- Vive solo en cotizaciones (backend), no en productos.
"""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from odoo_cli import OdooClient


VIEW_NAME = "wtk.sale.order.form.custom.quote.price"
AUTOMATION_NAME = "WTK - Aplicar precio custom en cotización"
ACTION_NAME = "WTK - Confirmar precio custom línea"


def _get_model(client: OdooClient, model_name: str) -> dict:
    rec = client.search_read("ir.model", domain=[["model", "=", model_name]], fields=["id", "name", "model"], limit=1)
    if not rec:
        raise RuntimeError(f"No se encontró modelo: {model_name}")
    return rec[0]


def ensure_custom_field(
    client: OdooClient,
    model: dict,
    name: str,
    field_description: str,
    ttype: str,
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
        "field_description": field_description,
        "model_id": model["id"],
        "model": model["model"],
        "ttype": ttype,
        "state": "manual",
        "store": True,
    }
    return client.create("ir.model.fields", vals)


def upsert_order_form_view(client: OdooClient) -> int:
    base_view_xml = client.search_read(
        "ir.model.data",
        domain=[["module", "=", "sale"], ["name", "=", "view_order_form"], ["model", "=", "ir.ui.view"]],
        fields=["res_id"],
        limit=1,
    )
    if not base_view_xml:
        raise RuntimeError("No se encontró sale.view_order_form")
    base_view_id = base_view_xml[0]["res_id"]

    arch_db = """
<data inherit_id="sale.view_order_form">
    <!-- Lista de líneas (backend cotización) -->
    <xpath expr="//field[@name='order_line']/list/field[@name='price_unit']" position="after">
        <field name="x_wtk_cotizacion" string="¿Cotización?"/>
        <field name="x_wtk_precio_custom" string="Precio custom" optional="show" invisible="not x_wtk_cotizacion"/>
        <field name="x_wtk_confirmar_precio" string="Confirmar" widget="boolean_toggle" optional="show" invisible="not x_wtk_cotizacion"/>
    </xpath>

    <!-- Form de línea dentro de cotización -->
    <xpath expr="//field[@name='order_line']/form//field[@name='price_unit']" position="after">
        <field name="x_wtk_cotizacion" string="¿Cotización?"/>
        <field name="x_wtk_precio_custom" string="Precio custom" invisible="not x_wtk_cotizacion"/>
        <field name="x_wtk_confirmar_precio" string="Confirmar precio" widget="boolean_toggle" invisible="not x_wtk_cotizacion"/>
    </xpath>
</data>
""".strip()

    existing = client.search_read(
        "ir.ui.view",
        domain=[["name", "=", VIEW_NAME], ["type", "=", "form"]],
        fields=["id"],
        limit=1,
    )
    vals = {
        "name": VIEW_NAME,
        "type": "form",
        "model": "sale.order",
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


def upsert_automation(client: OdooClient, model: dict) -> int:
    trigger_fields = client.search_read(
        "ir.model.fields",
        domain=[
            ["model", "=", "sale.order.line"],
            ["name", "in", ["x_wtk_cotizacion", "x_wtk_precio_custom", "x_wtk_confirmar_precio"]],
        ],
        fields=["id"],
        limit=10,
    )
    trigger_field_ids = [f["id"] for f in trigger_fields]

    code = """
if record.display_type in (False, None):
    if record.x_wtk_cotizacion and record.x_wtk_confirmar_precio and record.x_wtk_precio_custom not in (False, None):
        vals = {
            'price_unit': record.x_wtk_precio_custom,
            'x_wtk_confirmar_precio': False,
        }
        if record.product_id:
            vals['name'] = record.product_id.display_name
        record.write(vals)
""".strip()

    existing = client.search_read(
        "base.automation",
        domain=[["name", "=", AUTOMATION_NAME], ["model_name", "=", "sale.order.line"]],
        fields=["id", "action_server_ids"],
        limit=1,
    )

    if existing:
        auto_id = existing[0]["id"]
        action_ids = existing[0].get("action_server_ids") or []
        if action_ids:
            client.write(
                "ir.actions.server",
                action_ids,
                {"name": ACTION_NAME, "model_id": model["id"], "state": "code", "code": code},
            )
        else:
            action_id = client.create(
                "ir.actions.server",
                {
                    "name": ACTION_NAME,
                    "model_id": model["id"],
                    "state": "code",
                    "code": code,
                    "base_automation_id": auto_id,
                },
            )
            client.write("base.automation", [auto_id], {"action_server_ids": [(4, action_id)]})

        client.write(
            "base.automation",
            [auto_id],
            {
                "active": True,
                "trigger": "on_change",
                "model_id": model["id"],
                "trigger_field_ids": [(6, 0, trigger_field_ids)],
            },
        )
        return auto_id

    auto_id = client.create(
        "base.automation",
        {
            "name": AUTOMATION_NAME,
            "model_id": model["id"],
            "trigger": "on_change",
            "active": True,
            "trigger_field_ids": [(6, 0, trigger_field_ids)],
        },
    )
    action_id = client.create(
        "ir.actions.server",
        {
            "name": ACTION_NAME,
            "model_id": model["id"],
            "state": "code",
            "code": code,
            "base_automation_id": auto_id,
        },
    )
    client.write("base.automation", [auto_id], {"action_server_ids": [(4, action_id)]})
    return auto_id


def main() -> None:
    print("Configurando precio custom en cotizaciones...")
    client = OdooClient()
    uid = client.connect()
    print(f"✅ Conectado (uid={uid})")

    model = _get_model(client, "sale.order.line")

    ensure_custom_field(client, model, "x_wtk_cotizacion", "¿Cotización?", "boolean")
    ensure_custom_field(client, model, "x_wtk_precio_custom", "Precio custom", "float")
    ensure_custom_field(client, model, "x_wtk_confirmar_precio", "Confirmar precio", "boolean")

    view_id = upsert_order_form_view(client)
    auto_id = upsert_automation(client, model)

    print(f"✅ Vista aplicada (id={view_id})")
    print(f"✅ Automatización activa (id={auto_id})")
    print("Listo: marca ¿Cotización?, llena Precio custom y activa Confirmar.")


if __name__ == "__main__":
    main()
