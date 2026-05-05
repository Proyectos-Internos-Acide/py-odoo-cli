#!/usr/bin/env python3
"""
Configura el producto:
- Lares & Machu Picchu 4 días

Objetivo:
- Precio base = 0
- Sin impuestos
- Ventas ON / Compras OFF
- Mantener atributo "Tipo de pasajero" (Adulto/Estudiante/Niño) con price_extra=0
- Agregar atributo "Modalidad / Grupo" con precios:
  - Compartido (Base por persona): 760
  - Privado 2 personas: 980
  - Privado 3-4 personas: 860
  - Privado 5+ personas: 790
"""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from odoo_cli import OdooClient


PRODUCT_NAME = "Lares & Machu Picchu 4 días"
CATEGORY_NAME = "Camino Inca"
PASSENGER_ATTR = "Tipo de pasajero"
PASSENGER_VALUES = ["Adulto", "Estudiante", "Niño"]
PRICE_ATTR = "Modalidad / Grupo"
PRICE_MAP = {
    "Compartido (Base por persona)": 760.0,
    "Privado 2 personas (por persona)": 980.0,
    "Privado 3-4 personas (por persona)": 860.0,
    "Privado 5+ personas (por persona)": 790.0,
}


def ensure_category(client: OdooClient) -> int:
    cat = client.search_read("product.category", domain=[["name", "=", CATEGORY_NAME]], fields=["id"], limit=1)
    if not cat:
        raise RuntimeError(f"No existe la categoría '{CATEGORY_NAME}'.")
    return cat[0]["id"]


def ensure_attribute(client: OdooClient, name: str) -> int:
    rec = client.search_read("product.attribute", domain=[["name", "=", name]], fields=["id"], limit=1)
    if rec:
        return rec[0]["id"]
    return client.create(
        "product.attribute",
        {"name": name, "display_type": "radio", "create_variant": "always"},
    )


def ensure_value_ids(client: OdooClient, attr_id: int, labels: list[str]) -> dict[str, int]:
    result: dict[str, int] = {}
    for label in labels:
        val = client.search_read(
            "product.attribute.value",
            domain=[["name", "=", label], ["attribute_id", "=", attr_id]],
            fields=["id"],
            limit=1,
        )
        result[label] = val[0]["id"] if val else client.create(
            "product.attribute.value",
            {"name": label, "attribute_id": attr_id},
        )
    return result


def ensure_product(client: OdooClient, categ_id: int) -> int:
    prod = client.search_read("product.template", domain=[["name", "=", PRODUCT_NAME]], fields=["id"], limit=1)
    if not prod:
        raise RuntimeError(f"No existe el producto '{PRODUCT_NAME}'.")
    tmpl_id = prod[0]["id"]
    client.write(
        "product.template",
        [tmpl_id],
        {
            "categ_id": categ_id,
            "type": "service",
            "sale_ok": True,
            "purchase_ok": False,
            "taxes_id": [(6, 0, [])],
            "supplier_taxes_id": [(6, 0, [])],
            "list_price": 0.0,
        },
    )
    return tmpl_id


def ensure_line(client: OdooClient, tmpl_id: int, attr_id: int, value_ids: list[int]) -> None:
    line = client.search_read(
        "product.template.attribute.line",
        domain=[["product_tmpl_id", "=", tmpl_id], ["attribute_id", "=", attr_id]],
        fields=["id"],
        limit=1,
    )
    if line:
        client.write("product.template.attribute.line", [line[0]["id"]], {"value_ids": [(6, 0, value_ids)]})
    else:
        client.create(
            "product.template.attribute.line",
            {"product_tmpl_id": tmpl_id, "attribute_id": attr_id, "value_ids": [(6, 0, value_ids)]},
        )


def configure_price_extras(
    client: OdooClient,
    tmpl_id: int,
    passenger_value_ids: dict[str, int],
    price_value_ids: dict[str, int],
) -> None:
    price_by_value_id = {vid: 0.0 for vid in passenger_value_ids.values()}
    for label, amount in PRICE_MAP.items():
        price_by_value_id[price_value_ids[label]] = amount

    ptavs = client.search_read(
        "product.template.attribute.value",
        domain=[["product_tmpl_id", "=", tmpl_id]],
        fields=["id", "product_attribute_value_id"],
        limit=500,
    )
    for row in ptavs:
        pav = row.get("product_attribute_value_id")
        if isinstance(pav, list) and pav:
            amount = price_by_value_id.get(pav[0])
            if amount is not None:
                client.write("product.template.attribute.value", [row["id"]], {"price_extra": amount})


def show_result(client: OdooClient, tmpl_id: int) -> None:
    variants = client.search_read(
        "product.product",
        domain=[["product_tmpl_id", "=", tmpl_id]],
        fields=["display_name", "lst_price"],
        limit=200,
        order="id asc",
    )
    print(f"\n✅ Variantes finales ({len(variants)}):")
    for v in variants:
        print(f"- {v['display_name']} | USD {v['lst_price']}")


def main() -> None:
    print("Configurando Lares & Machu Picchu 4 días...")
    client = OdooClient()
    uid = client.connect()
    print(f"✅ Conectado (uid={uid})")

    categ_id = ensure_category(client)
    tmpl_id = ensure_product(client, categ_id)

    passenger_attr_id = ensure_attribute(client, PASSENGER_ATTR)
    passenger_ids = ensure_value_ids(client, passenger_attr_id, PASSENGER_VALUES)

    price_attr_id = ensure_attribute(client, PRICE_ATTR)
    price_ids = ensure_value_ids(client, price_attr_id, list(PRICE_MAP.keys()))

    ensure_line(client, tmpl_id, passenger_attr_id, list(passenger_ids.values()))
    ensure_line(client, tmpl_id, price_attr_id, list(price_ids.values()))
    configure_price_extras(client, tmpl_id, passenger_ids, price_ids)
    show_result(client, tmpl_id)
    print("\n🎉 Listo.")


if __name__ == "__main__":
    main()
