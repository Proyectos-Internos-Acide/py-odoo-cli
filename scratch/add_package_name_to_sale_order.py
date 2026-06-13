#!/usr/bin/env python3
"""
add_package_name_to_sale_order.py

Creates x_package_name on sale.order (header level) and places it
right below the partner_id (Cliente) field in the sale order form.
Always visible, with placeholder "Paquete custom MP".
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from odoo_cli import OdooClient

FIELD_NAME = "x_package_name"
MODEL_NAME = "sale.order"


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

    # ── 2. Create / ensure custom field on sale.order ────────────────────────
    print(f"\n🔧 Checking field '{FIELD_NAME}' on '{MODEL_NAME}'...")
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
                "field_description": "Nombre de Paquete",
                "ttype": "char",
                "state": "manual",
                "translate": True,   # i18n ready for future PDF
                "copied": True,
            },
        )
        print(f"   Field created with ID: {field_id}")
    else:
        field_id = existing[0]["id"]
        print(f"   Field already exists (ID: {field_id}).")

    # ── 3. Find base sale order form view ────────────────────────────────────
    print("\n🔍 Looking for base sale.order form view...")
    base_view = client.search_read(
        "ir.ui.view",
        domain=[["model", "=", "sale.order"], ["type", "=", "form"], ["inherit_id", "=", False]],
        fields=["id", "name"],
    )
    if not base_view:
        raise RuntimeError("Base sale.order form view not found.")
    parent_view_id = base_view[0]["id"]
    print(f"   Using: '{base_view[0]['name']}' (ID: {parent_view_id})")

    # ── 4. Create / update inherited view ────────────────────────────────────
    # Place the field inside group[@name='partner_details'], after partner_id
    # Always visible, with placeholder
    view_name = "sale_order_package_name_header_field"
    arch_xml = f"""
<xpath expr="//group[@name='partner_details']/field[@name='partner_id']" position="after">
    <field
        name="{FIELD_NAME}"
        placeholder="Paquete custom MP"
        string="Nombre de Paquete"
    />
</xpath>
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

    # ── 5. Clean up the old sale.order.line view (remove x_package_name from lines) ─
    print("\n🧹 Removing old sale.order.line view customization...")
    old_view = client.search_read(
        "ir.ui.view",
        domain=[["name", "=", "sale_order_line_package_name_field"]],
        fields=["id"],
    )
    if old_view:
        client.unlink("ir.ui.view", [old_view[0]["id"]])
        print("   Old view deleted.")
    else:
        print("   Old view not found (already clean).")

    # ── 6. Also clean up the field on sale.order.line if it exists ───────────
    print(f"\n🧹 Checking if '{FIELD_NAME}' exists on 'sale.order.line'...")
    old_field = client.search_read(
        "ir.model.fields",
        domain=[["model", "=", "sale.order.line"], ["name", "=", FIELD_NAME]],
        fields=["id"],
    )
    if old_field:
        print("   Found field on sale.order.line. Deleting...")
        client.unlink("ir.model.fields", [old_field[0]["id"]])
        print("   Deleted.")
    else:
        print("   Not found on sale.order.line (already clean).")

    print("\n🎉 Proceso completado exitosamente.")
    print(f"\nCampo '{FIELD_NAME}' en '{MODEL_NAME}':")
    print("  → Siempre visible en la cabecera de cotizaciones")
    print("  → Debajo del campo Cliente (partner_id)")
    print("  → Placeholder: 'Paquete custom MP'")


if __name__ == "__main__":
    main()
