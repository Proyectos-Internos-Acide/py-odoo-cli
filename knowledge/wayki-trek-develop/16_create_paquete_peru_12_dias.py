#!/usr/bin/env python3
"""
Crea/actualiza:
- Perú - Perú 12 días

Formato de precio:
- Sin cantidad de personas
- Variantes por:
  - Tipo de alojamiento: HOTEL 3 ESTRELLAS / BED & BREAKFAST
  - Tipo de habitación: SWD / DWB
- Precio fijo por combinación (por persona)
"""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from odoo_cli import OdooClient


PRODUCT_NAME = "Perú - Perú 12 días"
CATEGORY_NAME = "Paquetes"
LODGING_ATTR = "Tipo de alojamiento"
ROOM_ATTR = "Tipo de habitación"
PRICELIST_NAME = "WTK - Paquetes matriz precios (USD)"

DESCRIPTION = (
    "Descubre el Perú más auténtico en un viaje de 12 días que une cultura, aventura y naturaleza. "
    "Desde los templos de Cusco y el Valle Sagrado hasta la vivencia con los porteadores del Camino "
    "Inca, cada experiencia está pensada para transformar. Camina 4 días por senderos ancestrales "
    "rumbo a Machu Picchu, explorando ruinas ocultas y paisajes que elevan el alma. Luego, sumérgete "
    "en la selva de Puerto Maldonado, entre cochas, monos y guacamayos. Con logística premium, guías "
    "expertos y grupos reducidos, este viaje no es solo un recorrido: es una conexión profunda con la "
    "historia, la vida y lo esencial."
)

PRICE_MATRIX = {
    ("HOTEL 3 ESTRELLAS", "SWD"): 3186.0,
    ("HOTEL 3 ESTRELLAS", "DWB"): 2878.0,
    ("BED & BREAKFAST", "SWD"): 2877.0,
    ("BED & BREAKFAST", "DWB"): 2742.0,
}


def ensure_category(client: OdooClient) -> int:
    rec = client.search_read("product.category", domain=[["name", "=", CATEGORY_NAME]], fields=["id"], limit=1)
    if not rec:
        raise RuntimeError(f"No existe la categoría '{CATEGORY_NAME}'.")
    return rec[0]["id"]


def ensure_attribute(client: OdooClient, name: str) -> int:
    rec = client.search_read("product.attribute", domain=[["name", "=", name]], fields=["id"], limit=1)
    if rec:
        return rec[0]["id"]
    return client.create("product.attribute", {"name": name, "display_type": "radio", "create_variant": "always"})


def ensure_values(client: OdooClient, attr_id: int, labels: list[str]) -> dict[str, int]:
    out: dict[str, int] = {}
    for label in labels:
        rec = client.search_read(
            "product.attribute.value",
            domain=[["name", "=", label], ["attribute_id", "=", attr_id]],
            fields=["id"],
            limit=1,
        )
        out[label] = rec[0]["id"] if rec else client.create("product.attribute.value", {"name": label, "attribute_id": attr_id})
    return out


def create_or_update_template(client: OdooClient, categ_id: int) -> int:
    rec = client.search_read("product.template", domain=[["name", "=", PRODUCT_NAME]], fields=["id"], limit=1)
    vals = {
        "name": PRODUCT_NAME,
        "categ_id": categ_id,
        "type": "service",
        "sale_ok": True,
        "purchase_ok": False,
        "taxes_id": [(6, 0, [])],
        "supplier_taxes_id": [(6, 0, [])],
        "list_price": 0.0,
        "description_sale": DESCRIPTION,
    }
    if rec:
        tid = rec[0]["id"]
        client.write("product.template", [tid], vals)
        return tid
    return client.create("product.template", vals)


def ensure_attr_line(client: OdooClient, tmpl_id: int, attr_id: int, value_ids: list[int]) -> None:
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


def keep_only_required_attributes(client: OdooClient, tmpl_id: int, allowed_attr_ids: list[int]) -> None:
    lines = client.search_read(
        "product.template.attribute.line",
        domain=[["product_tmpl_id", "=", tmpl_id]],
        fields=["id", "attribute_id"],
        limit=100,
    )
    allowed = set(allowed_attr_ids)
    for line in lines:
        attr = line.get("attribute_id")
        if isinstance(attr, list) and attr and attr[0] not in allowed:
            client.unlink("product.template.attribute.line", [line["id"]])


def set_all_ptav_zero(client: OdooClient, tmpl_id: int) -> None:
    ptavs = client.search_read(
        "product.template.attribute.value",
        domain=[["product_tmpl_id", "=", tmpl_id]],
        fields=["id", "price_extra"],
        limit=500,
    )
    for row in ptavs:
        if row.get("price_extra") != 0.0:
            client.write("product.template.attribute.value", [row["id"]], {"price_extra": 0.0})


def get_or_create_pricelist(client: OdooClient) -> int:
    rec = client.search_read("product.pricelist", domain=[["name", "=", PRICELIST_NAME]], fields=["id"], limit=1)
    if rec:
        return rec[0]["id"]
    return client.create("product.pricelist", {"name": PRICELIST_NAME, "currency_id": 1})


def upsert_variant_prices(client: OdooClient, tmpl_id: int, pricelist_id: int) -> None:
    variants = client.search_read(
        "product.product",
        domain=[["product_tmpl_id", "=", tmpl_id]],
        fields=["id", "display_name"],
        limit=200,
    )
    variant_price: dict[int, float] = {}
    for variant in variants:
        name = variant.get("display_name", "")
        for (lodging, room), price in PRICE_MATRIX.items():
            if lodging in name and room in name:
                variant_price[variant["id"]] = price
                break

    if len(variant_price) < len(PRICE_MATRIX):
        raise RuntimeError("No se pudo mapear todas las variantes para Perú 12 días.")

    existing = client.search_read(
        "product.pricelist.item",
        domain=[["pricelist_id", "=", pricelist_id], ["product_id", "in", list(variant_price.keys())]],
        fields=["id", "product_id"],
        limit=500,
    )
    existing_by_variant: dict[int, int] = {}
    for row in existing:
        pid = row.get("product_id")
        if isinstance(pid, list) and pid:
            existing_by_variant[pid[0]] = row["id"]

    for variant_id, price in variant_price.items():
        client.write("product.product", [variant_id], {"lst_price": price})
        vals = {
            "pricelist_id": pricelist_id,
            "applied_on": "0_product_variant",
            "product_id": variant_id,
            "compute_price": "fixed",
            "fixed_price": price,
            "min_quantity": 0.0,
        }
        if variant_id in existing_by_variant:
            client.write("product.pricelist.item", [existing_by_variant[variant_id]], vals)
        else:
            client.create("product.pricelist.item", vals)


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


def show_result(client: OdooClient, tmpl_id: int, pricelist_id: int) -> None:
    variants = client.search_read(
        "product.product",
        domain=[["product_tmpl_id", "=", tmpl_id], ["active", "=", True]],
        fields=["id", "display_name", "lst_price"],
        limit=100,
        order="id asc",
    )
    rules = client.search_read(
        "product.pricelist.item",
        domain=[["pricelist_id", "=", pricelist_id]],
        fields=["product_id", "fixed_price"],
        limit=3000,
    )
    fixed_by_variant: dict[int, float] = {}
    for row in rules:
        pid = row.get("product_id")
        if isinstance(pid, list) and pid:
            fixed_by_variant[pid[0]] = row.get("fixed_price", 0.0)

    print("\n✅ Variantes y precios:")
    for v in variants:
        print(f"- {v['display_name']} | lst_price={v['lst_price']} | fixed={fixed_by_variant.get(v['id'])}")


def main() -> None:
    print("Configurando Perú - Perú 12 días...")
    client = OdooClient()
    uid = client.connect()
    print(f"✅ Conectado (uid={uid})")

    categ_id = ensure_category(client)
    lodging_attr_id = ensure_attribute(client, LODGING_ATTR)
    room_attr_id = ensure_attribute(client, ROOM_ATTR)

    lodging_labels = sorted({k[0] for k in PRICE_MATRIX.keys()})
    room_labels = sorted({k[1] for k in PRICE_MATRIX.keys()})
    lodging_values = ensure_values(client, lodging_attr_id, lodging_labels)
    room_values = ensure_values(client, room_attr_id, room_labels)

    tmpl_id = create_or_update_template(client, categ_id)
    ensure_attr_line(client, tmpl_id, lodging_attr_id, [lodging_values[x] for x in lodging_labels])
    ensure_attr_line(client, tmpl_id, room_attr_id, [room_values[x] for x in room_labels])
    keep_only_required_attributes(client, tmpl_id, [lodging_attr_id, room_attr_id])
    set_all_ptav_zero(client, tmpl_id)

    pricelist_id = get_or_create_pricelist(client)
    upsert_variant_prices(client, tmpl_id, pricelist_id)
    set_default_pricelist(client, pricelist_id)
    show_result(client, tmpl_id, pricelist_id)
    print("\n🎉 Listo.")


if __name__ == "__main__":
    main()
