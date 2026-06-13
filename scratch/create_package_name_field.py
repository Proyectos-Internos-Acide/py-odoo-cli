#!/usr/bin/env python3
"""
create_package_name_field.py

Creates a custom field `x_package_name` (Nombre de Paquete) on sale.order.line.
The field is visible only when product_uom_qty > 1 on that line.
Includes i18n-friendly field label for future PDF integration.
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from odoo_cli import OdooClient

FIELD_NAME = "x_package_name"
MODEL_NAME = "sale.order.line"


def main():
    client = OdooClient()
    client.connect()
    print("✅ Connected to Odoo.")

    # ── 1. Get model ID ──────────────────────────────────────────────────────
    print(f"\n📦 Finding model '{MODEL_NAME}'...")
    model_recs = client.search_read(
        "ir.model",
        domain=[["model", "=", MODEL_NAME]],
        fields=["id", "name"],
    )
    if not model_recs:
        raise RuntimeError(f"Model '{MODEL_NAME}' not found.")
    model_id = model_recs[0]["id"]
    print(f"   Found: {model_recs[0]['name']} (ID: {model_id})")

    # ── 2. Create / ensure custom field ─────────────────────────────────────
    print(f"\n🔧 Checking field '{FIELD_NAME}'...")
    existing = client.search_read(
        "ir.model.fields",
        domain=[["model", "=", MODEL_NAME], ["name", "=", FIELD_NAME]],
        fields=["id", "name", "field_description"],
    )
    if not existing:
        print(f"   Creating field '{FIELD_NAME}'...")
        field_id = client.create(
            "ir.model.fields",
            {
                "model_id": model_id,
                "name": FIELD_NAME,
                "field_description": "Nombre de Paquete",   # shown as column header
                "ttype": "char",
                "state": "manual",
                "translate": True,   # i18n ready for future PDF translations
                "copied": True,
            },
        )
        print(f"   Field created with ID: {field_id}")
    else:
        field_id = existing[0]["id"]
        print(f"   Field already exists (ID: {field_id}).")

    # ── 3. Find sale order form view ─────────────────────────────────────────
    print("\n🔍 Looking for sale order form views...")
    sol_views = client.search_read(
        "ir.ui.view",
        domain=[["model", "=", "sale.order"], ["type", "=", "form"]],
        fields=["id", "name", "inherit_id"],
    )
    print(f"   Found {len(sol_views)} form views for sale.order:")
    for v in sol_views:
        print(f"   ID: {v['id']} | {v['name']} | Inherit: {v['inherit_id']}")

    # Target: the base sale order form (non-inherited)
    base_views = [v for v in sol_views if not v["inherit_id"]]
    if not base_views:
        base_views = sol_views  # fallback
    parent_view = base_views[0]
    parent_view_id = parent_view["id"]
    print(f"\n   Using parent view: '{parent_view['name']}' (ID: {parent_view_id})")

    # ── 4. Create / update inherited view ────────────────────────────────────
    # The inline list in sale.order.form has product_uom_qty followed by a widget.
    # We add x_package_name after product_uom_qty - NO optional so it always shows.
    view_name = "sale_order_line_package_name_field"
    arch_xml = f"""
<data>
    <xpath expr="//field[@name='order_line']//field[@name='product_uom_qty']" position="after">
        <field
            name="{FIELD_NAME}"
            column_invisible="True"
            placeholder="Paquete custom MP"
            string="Nombre de Paquete"
        />
    </xpath>
    <xpath expr="//field[@name='order_line']//field[@name='product_template_id']" position="after">
        <field
            name="{FIELD_NAME}"
            optional="show"
            placeholder="Paquete custom MP"
            invisible="product_uom_qty &lt;= 1"
            string="Nombre de Paquete"
        />
    </xpath>
</data>
"""
    existing_view = client.search_read(
        "ir.ui.view",
        domain=[["name", "=", view_name]],
        fields=["id"],
    )
    view_vals = {
        "name": view_name,
        "model": "sale.order",
        "inherit_id": parent_view_id,
        "type": "form",
        "arch": arch_xml,
        "priority": 99,
    }

    if not existing_view:
        print(f"\n🖼️  Creating inherited view '{view_name}'...")
        view_id = client.create("ir.ui.view", view_vals)
        print(f"   Inherited view created with ID: {view_id}")
    else:
        print(f"\n🖼️  Updating inherited view '{view_name}'...")
        client.write("ir.ui.view", [existing_view[0]["id"]], {"arch": arch_xml})
        print("   Updated.")

    print("\n🎉 Proceso completado exitosamente.")
    print(f"\nCampo creado: '{FIELD_NAME}' en '{MODEL_NAME}'")
    print("Comportamiento: visible cuando product_uom_qty > 1 en la línea de pedido.")


if __name__ == "__main__":
    main()
