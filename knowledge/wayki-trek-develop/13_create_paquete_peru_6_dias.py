#!/usr/bin/env python3
"""
Crea/actualiza:
- Paquetes - Perú 6 días

Categoría: Paquetes
Variantes:
- Número de personas: 1 persona, 2 personas, 3 personas
- Alojamiento: Hotel 3★ – SWD, Hotel 3★ – DWB

Precio:
- Se fija por variante exacta (matriz), porque no es aditivo simple.
"""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from odoo_cli import OdooClient


PRODUCT_NAME = "Paquetes - Perú 6 días"
CATEGORY_NAME = "Paquetes"
PERSON_ATTR = "Número de personas"
ROOM_ATTR = "Alojamiento"
PRICELIST_NAME = "WTK - Paquetes matriz precios (USD)"

DESCRIPTION = (
    "Explora la esencia del antiguo imperio inca en un viaje de 6 días que combina cultura viva, "
    "caminatas legendarias y momentos transformadores. Desde las calles de Cusco hasta Machu Picchu, "
    "conecta con la historia, la naturaleza y contigo mismo. Incluye visitas guiadas, traslados privados, "
    "alojamiento en hoteles seleccionados y el icónico Camino Inca de 2 días. En grupos pequeños de 4 a 8 "
    "personas o en servicio privado, vive una experiencia auténtica, flexible y cercana con Wayki Trek. "
    "Cada paso es un recuerdo; cada mirada, una emoción.\n\n"
    "SWD: Alojamiento en habitación individual.\n"
    "DWB: Alojamiento en habitación doble o twin."
)

# (person_label, room_label) -> price_per_person
PRICE_MATRIX = {
    ("1 persona", "Hotel 3★ – SWD"): 1471.0,
    ("1 persona", "Hotel 3★ – DWB"): 0.0,
    ("2 personas", "Hotel 3★ – SWD"): 1379.0,
    ("2 personas", "Hotel 3★ – DWB"): 1079.0,
    ("3 personas", "Hotel 3★ – SWD"): 1349.0,
    ("3 personas", "Hotel 3★ – DWB"): 1049.0,
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
    return client.create(
        "product.attribute",
        {"name": name, "display_type": "radio", "create_variant": "always"},
    )


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
        tmpl_id = rec[0]["id"]
        client.write("product.template", [tmpl_id], vals)
        return tmpl_id
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
        for (person, room), price in PRICE_MATRIX.items():
            if person in name and room in name:
                variant_price[variant["id"]] = price
                break

    if len(variant_price) < len(PRICE_MATRIX):
        raise RuntimeError("No se pudo mapear todas las variantes de la matriz de precios.")

    existing = client.search_read(
        "product.pricelist.item",
        domain=[["pricelist_id", "=", pricelist_id], ["product_id", "in", list(variant_price.keys())]],
        fields=["id", "product_id"],
        limit=500,
    )
    existing_by_variant: dict[int, int] = {}
    for row in existing:
        product_id = row.get("product_id")
        if isinstance(product_id, list) and product_id:
            existing_by_variant[product_id[0]] = row["id"]

    for variant_id, price in variant_price.items():
        # También grabamos precio en la variante para que el configurador muestre
        # montos directos y no aparezcan todos en 0.
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
        fields=["id", "display_name"],
        limit=100,
        order="id asc",
    )
    rules = client.search_read(
        "product.pricelist.item",
        domain=[["pricelist_id", "=", pricelist_id]],
        fields=["id", "product_id", "fixed_price"],
        limit=2000,
    )
    rule_by_variant: dict[int, float] = {}
    for row in rules:
        pid = row.get("product_id")
        if isinstance(pid, list) and pid:
            rule_by_variant[pid[0]] = row.get("fixed_price", 0.0)

    print("\n✅ Variantes y precio fijo por persona:")
    for v in variants:
        print(f"- {v['display_name']} | USD {rule_by_variant.get(v['id'])}")


def main() -> None:
    print("Configurando Paquetes - Perú 6 días...")
    client = OdooClient()
    uid = client.connect()
    print(f"✅ Conectado (uid={uid})")

    categ_id = ensure_category(client)
    person_attr_id = ensure_attribute(client, PERSON_ATTR)
    room_attr_id = ensure_attribute(client, ROOM_ATTR)

    person_labels = sorted({k[0] for k in PRICE_MATRIX.keys()})
    room_labels = sorted({k[1] for k in PRICE_MATRIX.keys()})
    person_values = ensure_values(client, person_attr_id, person_labels)
    room_values = ensure_values(client, room_attr_id, room_labels)

    tmpl_id = create_or_update_template(client, categ_id)
    ensure_attr_line(client, tmpl_id, person_attr_id, [person_values[x] for x in person_labels])
    ensure_attr_line(client, tmpl_id, room_attr_id, [room_values[x] for x in room_labels])
    keep_only_required_attributes(client, tmpl_id, [person_attr_id, room_attr_id])
    set_all_ptav_zero(client, tmpl_id)

    pricelist_id = get_or_create_pricelist(client)
    upsert_variant_prices(client, tmpl_id, pricelist_id)
    set_default_pricelist(client, pricelist_id)
    show_result(client, tmpl_id, pricelist_id)
    print("\n🎉 Listo.")


if __name__ == "__main__":
    main()
