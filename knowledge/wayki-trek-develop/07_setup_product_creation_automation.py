#!/usr/bin/env python3
"""
Automatiza la creación de productos en Odoo para Wayki Trek.

Al crear un producto nuevo (product.template), aplica:
- Ventas = ON
- Compras = OFF
- Precio base = 0
- Sin impuestos por defecto
- Atributo "Tipo de pasajero" preconfigurado con:
  - Adulto
  - Estudiante
  - Niño
- price_extra = 0 para todas esas variantes
"""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from odoo_cli import OdooClient


AUTOMATION_NAME = "WTK - Defaults al crear producto"
SERVER_ACTION_NAME = "WTK - Aplicar defaults producto nuevo"
PASSENGER_ATTRIBUTE = "Tipo de pasajero"
PASSENGER_VALUES = ["Adulto", "Estudiante", "Niño"]


def _get_model_id(client: OdooClient, model_name: str) -> int:
    model = client.search_read("ir.model", domain=[["model", "=", model_name]], fields=["id"], limit=1)
    if not model:
        raise RuntimeError(f"No se encontró ir.model para: {model_name}")
    return model[0]["id"]


def ensure_attribute_and_values(client: OdooClient) -> tuple[int, list[int]]:
    attr = client.search_read(
        "product.attribute",
        domain=[["name", "=", PASSENGER_ATTRIBUTE]],
        fields=["id"],
        limit=1,
    )
    if attr:
        attr_id = attr[0]["id"]
    else:
        attr_id = client.create(
            "product.attribute",
            {"name": PASSENGER_ATTRIBUTE, "display_type": "radio", "create_variant": "always"},
        )

    value_ids: list[int] = []
    for label in PASSENGER_VALUES:
        val = client.search_read(
            "product.attribute.value",
            domain=[["name", "=", label], ["attribute_id", "=", attr_id]],
            fields=["id"],
            limit=1,
        )
        value_ids.append(val[0]["id"] if val else client.create("product.attribute.value", {"name": label, "attribute_id": attr_id}))

    return attr_id, value_ids


def set_ir_defaults(client: OdooClient) -> None:
    companies = client.search_read("res.company", domain=[], fields=["id"], limit=50)
    for comp in companies:
        cid = comp["id"]
        client.execute("ir.default", "set", "product.template", "sale_ok", True, False, cid, False)
        client.execute("ir.default", "set", "product.template", "purchase_ok", False, False, cid, False)
        client.execute("ir.default", "set", "product.template", "list_price", 0.0, False, cid, False)
        client.execute("ir.default", "set", "product.template", "type", "service", False, cid, False)


def upsert_automation(client: OdooClient, attr_id: int, value_ids: list[int]) -> None:
    product_template_model_id = _get_model_id(client, "product.template")

    code = f"""
attr_id = {attr_id}
value_ids = {value_ids}

record.write({{
    'sale_ok': True,
    'purchase_ok': False,
    'list_price': 0.0,
    'taxes_id': [(6, 0, [])],
    'supplier_taxes_id': [(6, 0, [])],
}})

line = record.attribute_line_ids.filtered(lambda l: l.attribute_id.id == attr_id)[:1]
if line:
    line.write({{'value_ids': [(6, 0, value_ids)]}})
else:
    env['product.template.attribute.line'].create({{
        'product_tmpl_id': record.id,
        'attribute_id': attr_id,
        'value_ids': [(6, 0, value_ids)],
    }})

ptavs = env['product.template.attribute.value'].search([
    ('product_tmpl_id', '=', record.id),
    ('product_attribute_value_id', 'in', value_ids),
])
if ptavs:
    ptavs.write({{'price_extra': 0.0}})
"""

    existing_automation = client.search_read(
        "base.automation",
        domain=[["name", "=", AUTOMATION_NAME], ["model_name", "=", "product.template"]],
        fields=["id", "action_server_ids"],
        limit=1,
    )

    if existing_automation:
        automation_id = existing_automation[0]["id"]
        action_server_ids = existing_automation[0].get("action_server_ids") or []
        if action_server_ids:
            client.write(
                "ir.actions.server",
                action_server_ids,
                {
                    "name": SERVER_ACTION_NAME,
                    "model_id": product_template_model_id,
                    "state": "code",
                    "code": code,
                },
            )
        else:
            new_action_id = client.create(
                "ir.actions.server",
                {
                    "name": SERVER_ACTION_NAME,
                    "model_id": product_template_model_id,
                    "state": "code",
                    "code": code,
                    "base_automation_id": automation_id,
                },
            )
            client.write("base.automation", [automation_id], {"action_server_ids": [(4, new_action_id)]})
        client.write(
            "base.automation",
            [automation_id],
            {"active": True, "trigger": "on_create", "model_id": product_template_model_id},
        )
    else:
        automation_id = client.create(
            "base.automation",
            {
                "name": AUTOMATION_NAME,
                "model_id": product_template_model_id,
                "trigger": "on_create",
                "active": True,
            },
        )
        action_id = client.create(
            "ir.actions.server",
            {
                "name": SERVER_ACTION_NAME,
                "model_id": product_template_model_id,
                "state": "code",
                "code": code,
                "base_automation_id": automation_id,
            },
        )
        client.write("base.automation", [automation_id], {"action_server_ids": [(4, action_id)]})


def main() -> None:
    print("Configurando automatización de creación de productos...")
    client = OdooClient()
    uid = client.connect()
    print(f"✅ Conectado (uid={uid})")

    attr_id, value_ids = ensure_attribute_and_values(client)
    set_ir_defaults(client)
    upsert_automation(client, attr_id, value_ids)

    print("✅ Automatización configurada.")
    print("- Ventas=ON, Compras=OFF, precio=0, impuestos=[]")
    print("- Tipo de pasajero: Adulto, Estudiante, Niño (price_extra=0)")


if __name__ == "__main__":
    main()
