#!/usr/bin/env python3
"""
Crea/actualiza el producto:
- Camino Inca 2 días – Para Parejas

Configuración:
- Categoría: Camino Inca
- Tipo: Service
- Ventas: ON
- Compras: OFF
- Sin impuestos
- Variantes: Adulto y Estudiante (sin Niño)
- Precios finales:
  - Adulto: 870 USD
  - Estudiante: 620 USD
"""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from odoo_cli import OdooClient


PRODUCT_NAME = "Camino Inca 2 días – Para Parejas"
DESCRIPTION = (
    "Perfecta para parejas que buscan una aventura íntima y transformadora, esta experiencia "
    "condensa lo mejor del legado inca en una travesía corta, pero profundamente significativa. "
    "Atraviesa la ceja de selva andina, rodeado de naturaleza viva, orquídeas silvestres y "
    "vestigios arqueológicos ocultos. Caminos ancestrales te llevarán a lugares sagrados como "
    "Chachabamba y Wiñay Wayna, culminando con una llegada inolvidable a Machu Picchu por la "
    "Puerta del Sol. Una experiencia que no solo une paisajes, sino también corazones. Caminar "
    "juntos, descubrir juntos, crecer juntos."
)
PRICES = {"Adulto": 870.0, "Estudiante": 620.0}


def ensure_category(client: OdooClient) -> int:
    cat = client.search_read("product.category", domain=[["name", "=", "Camino Inca"]], fields=["id"], limit=1)
    if not cat:
        raise RuntimeError("No existe la categoría 'Camino Inca'.")
    return cat[0]["id"]


def ensure_attribute_and_values(client: OdooClient) -> tuple[int, dict[str, int]]:
    attr = client.search_read("product.attribute", domain=[["name", "=", "Tipo de pasajero"]], fields=["id"], limit=1)
    if attr:
        attr_id = attr[0]["id"]
    else:
        attr_id = client.create(
            "product.attribute",
            {"name": "Tipo de pasajero", "display_type": "radio", "create_variant": "always"},
        )

    value_ids: dict[str, int] = {}
    for label in PRICES:
        val = client.search_read(
            "product.attribute.value",
            domain=[["name", "=", label], ["attribute_id", "=", attr_id]],
            fields=["id"],
            limit=1,
        )
        value_ids[label] = val[0]["id"] if val else client.create(
            "product.attribute.value",
            {"name": label, "attribute_id": attr_id},
        )
    return attr_id, value_ids


def create_or_update_product(client: OdooClient, categ_id: int) -> int:
    existing = client.search_read(
        "product.template",
        domain=[["name", "=", PRODUCT_NAME]],
        fields=["id"],
        limit=1,
    )
    vals = {
        "name": PRODUCT_NAME,
        "categ_id": categ_id,
        "type": "service",
        "sale_ok": True,
        "purchase_ok": False,
        "taxes_id": [(6, 0, [])],
        "supplier_taxes_id": [(6, 0, [])],
        "description_sale": DESCRIPTION,
        "list_price": 0.0,
    }
    if existing:
        tmpl_id = existing[0]["id"]
        client.write("product.template", [tmpl_id], vals)
        return tmpl_id
    return client.create("product.template", vals)


def ensure_attribute_line(client: OdooClient, tmpl_id: int, attr_id: int, value_ids: dict[str, int]) -> None:
    target_ids = [value_ids["Adulto"], value_ids["Estudiante"]]
    line = client.search_read(
        "product.template.attribute.line",
        domain=[["product_tmpl_id", "=", tmpl_id], ["attribute_id", "=", attr_id]],
        fields=["id"],
        limit=1,
    )
    if line:
        client.write("product.template.attribute.line", [line[0]["id"]], {"value_ids": [(6, 0, target_ids)]})
    else:
        client.create(
            "product.template.attribute.line",
            {"product_tmpl_id": tmpl_id, "attribute_id": attr_id, "value_ids": [(6, 0, target_ids)]},
        )


def configure_price_extras(client: OdooClient, tmpl_id: int, value_ids: dict[str, int]) -> None:
    extras = {
        value_ids["Estudiante"]: PRICES["Estudiante"],
        value_ids["Adulto"]: PRICES["Adulto"],
    }
    ptavs = client.search_read(
        "product.template.attribute.value",
        domain=[["product_tmpl_id", "=", tmpl_id]],
        fields=["id", "product_attribute_value_id"],
        limit=100,
    )
    for row in ptavs:
        pav = row.get("product_attribute_value_id")
        if isinstance(pav, list) and pav and pav[0] in extras:
            client.write("product.template.attribute.value", [row["id"]], {"price_extra": extras[pav[0]]})


def show_result(client: OdooClient, tmpl_id: int) -> None:
    variants = client.search_read(
        "product.product",
        domain=[["product_tmpl_id", "=", tmpl_id]],
        fields=["display_name", "lst_price"],
        limit=20,
        order="id asc",
    )
    print("\n✅ Producto creado/actualizado:")
    for v in variants:
        print(f"- {v['display_name']} | USD {v['lst_price']}")


def main() -> None:
    print("Creando/actualizando tour Camino Inca 2 días – Para Parejas...")
    client = OdooClient()
    uid = client.connect()
    print(f"✅ Conectado (uid={uid})")

    categ_id = ensure_category(client)
    attr_id, value_ids = ensure_attribute_and_values(client)
    tmpl_id = create_or_update_product(client, categ_id)
    ensure_attribute_line(client, tmpl_id, attr_id, value_ids)
    configure_price_extras(client, tmpl_id, value_ids)
    show_result(client, tmpl_id)
    print("\n🎉 Listo.")


if __name__ == "__main__":
    main()
