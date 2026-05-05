#!/usr/bin/env python3
"""
Configura precio automático por cantidad para:
- Lares & Machu Picchu 4 días

Reglas (precio por persona):
- 1 persona  -> 760
- 2 personas -> 980
- 3-4        -> 860
- 5+         -> 790

Implementación:
- Quita el atributo "Modalidad / Grupo" de este producto para evitar selección manual.
- Mantiene "Tipo de pasajero".
- Crea/actualiza reglas de pricelist por cantidad mínima.
"""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from odoo_cli import OdooClient


PRODUCT_NAME = "Lares & Machu Picchu 4 días"
PRICELIST_NAME = "WTK - Lares automático por cantidad (USD)"
MODALIDAD_ATTR_NAME = "Modalidad / Grupo"

# min_quantity -> fixed_price
TIERS = [
    (1, 760.0),
    (2, 980.0),
    (3, 860.0),
    (5, 790.0),
]


def get_product_template(client: OdooClient) -> int:
    rec = client.search_read(
        "product.template",
        domain=[["name", "=", PRODUCT_NAME]],
        fields=["id"],
        limit=1,
    )
    if not rec:
        raise RuntimeError(f"No existe el producto '{PRODUCT_NAME}'.")
    return rec[0]["id"]


def remove_modalidad_attribute_line(client: OdooClient, tmpl_id: int) -> None:
    attr = client.search_read(
        "product.attribute",
        domain=[["name", "=", MODALIDAD_ATTR_NAME]],
        fields=["id"],
        limit=1,
    )
    if not attr:
        return
    attr_id = attr[0]["id"]
    lines = client.search_read(
        "product.template.attribute.line",
        domain=[["product_tmpl_id", "=", tmpl_id], ["attribute_id", "=", attr_id]],
        fields=["id"],
        limit=10,
    )
    if lines:
        client.unlink("product.template.attribute.line", [l["id"] for l in lines])


def get_or_create_pricelist(client: OdooClient) -> int:
    pl = client.search_read(
        "product.pricelist",
        domain=[["name", "=", PRICELIST_NAME]],
        fields=["id"],
        limit=1,
    )
    if pl:
        return pl[0]["id"]
    return client.create(
        "product.pricelist",
        {"name": PRICELIST_NAME, "currency_id": 1},  # USD
    )


def configure_tier_items(client: OdooClient, pricelist_id: int, tmpl_id: int) -> None:
    # Limpiar reglas previas de este producto en esta pricelist
    existing = client.search_read(
        "product.pricelist.item",
        domain=[["pricelist_id", "=", pricelist_id], ["product_tmpl_id", "=", tmpl_id]],
        fields=["id"],
        limit=200,
    )
    if existing:
        client.unlink("product.pricelist.item", [r["id"] for r in existing])

    for min_qty, price in TIERS:
        client.create(
            "product.pricelist.item",
            {
                "pricelist_id": pricelist_id,
                "applied_on": "1_product",
                "product_tmpl_id": tmpl_id,
                "compute_price": "fixed",
                "fixed_price": price,
                "min_quantity": float(min_qty),
            },
        )


def set_default_pricelist(client: OdooClient, pricelist_id: int) -> None:
    companies = client.search_read("res.company", domain=[], fields=["id"], limit=20)
    for comp in companies:
        client.execute(
            "ir.default",
            "set",
            "res.partner",
            "property_product_pricelist",
            pricelist_id,
            False,
            comp["id"],
            False,
        )


def show_summary(client: OdooClient, tmpl_id: int, pricelist_id: int) -> None:
    variants = client.search_read(
        "product.product",
        domain=[["product_tmpl_id", "=", tmpl_id]],
        fields=["id", "display_name", "lst_price"],
        limit=50,
        order="id asc",
    )
    rules = client.search_read(
        "product.pricelist.item",
        domain=[["pricelist_id", "=", pricelist_id], ["product_tmpl_id", "=", tmpl_id]],
        fields=["min_quantity", "fixed_price"],
        limit=50,
        order="min_quantity asc",
    )
    print(f"\n✅ Variantes actuales ({len(variants)}):")
    for v in variants:
        print(f"- {v['display_name']} | list_price={v['lst_price']}")

    print("\n✅ Reglas automáticas por cantidad:")
    for r in rules:
        print(f"- min_qty={r['min_quantity']} => USD {r['fixed_price']}")


def main() -> None:
    print("Configurando Lares con precio automático por cantidad...")
    client = OdooClient()
    uid = client.connect()
    print(f"✅ Conectado (uid={uid})")

    tmpl_id = get_product_template(client)
    remove_modalidad_attribute_line(client, tmpl_id)
    pricelist_id = get_or_create_pricelist(client)
    configure_tier_items(client, pricelist_id, tmpl_id)
    set_default_pricelist(client, pricelist_id)
    show_summary(client, tmpl_id, pricelist_id)
    print("\n🎉 Listo.")


if __name__ == "__main__":
    main()
