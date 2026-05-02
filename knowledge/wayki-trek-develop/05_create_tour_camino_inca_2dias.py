#!/usr/bin/env python3
"""
Crea o actualiza el tour:
- Camino Inca 2 días – Grupo Compartido

Configuración:
- Categoría: Camino Inca
- Tipo: Service
- Ventas: ON
- Compras: OFF
- Sin impuestos
- Tarifas configurables por variante:
  - Adulto: 670 USD
  - Estudiante: 620 USD
  - Niño: 590 USD
"""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from odoo_cli import OdooClient


PRODUCT_NAME = "Camino Inca 2 días – Grupo Compartido"
DESCRIPTION = (
    "Vive la esencia del legendario Camino Inca en una versión corta pero profundamente "
    "significativa. Esta aventura compartida te llevará por antiguos senderos entre selva "
    "andina, rodeado de orquídeas, aves y paisajes espectaculares. En el camino, descubrirás "
    "sitios arqueológicos como Chachabamba y Wiñay Wayna, donde el pasado cobra vida. "
    "El momento culminante llega al cruzar el Inti Punku, la Puerta del Sol, y ver por primera "
    "vez Machu Picchu como lo hicieron los antiguos peregrinos. Un recorrido ideal para quienes "
    "buscan historia, naturaleza y conexión, en compañía de otros aventureros."
)

PRICES = {
    "Adulto": 670.0,
    "Estudiante": 620.0,
    "Niño": 590.0,
}


def ensure_category(client: OdooClient) -> int:
    cat = client.search_read("product.category", domain=[["name", "=", "Camino Inca"]], fields=["id"], limit=1)
    if not cat:
        raise RuntimeError("No existe la categoría 'Camino Inca'.")
    return cat[0]["id"]


def ensure_attribute_and_values(client: OdooClient) -> tuple[int, dict[str, int]]:
    attr_name = "Tipo de pasajero"
    attr = client.search_read("product.attribute", domain=[["name", "=", attr_name]], fields=["id"], limit=1)
    if attr:
        attr_id = attr[0]["id"]
    else:
        attr_id = client.create(
            "product.attribute",
            {
                "name": attr_name,
                "display_type": "radio",
                "create_variant": "always",
            },
        )

    value_ids: dict[str, int] = {}
    for value_name in PRICES:
        val = client.search_read(
            "product.attribute.value",
            domain=[["name", "=", value_name], ["attribute_id", "=", attr_id]],
            fields=["id"],
            limit=1,
        )
        if val:
            value_ids[value_name] = val[0]["id"]
        else:
            value_ids[value_name] = client.create(
                "product.attribute.value",
                {
                    "name": value_name,
                    "attribute_id": attr_id,
                },
            )
    return attr_id, value_ids


def ensure_product(client: OdooClient, categ_id: int) -> int:
    product = client.search_read(
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
        # Base = precio más bajo; los demás por price_extra.
        "list_price": PRICES["Niño"],
    }
    if product:
        tmpl_id = product[0]["id"]
        client.write("product.template", [tmpl_id], vals)
        return tmpl_id
    return client.create("product.template", vals)


def ensure_attribute_line(client: OdooClient, tmpl_id: int, attr_id: int, value_ids: dict[str, int]) -> None:
    lines = client.search_read(
        "product.template.attribute.line",
        domain=[["product_tmpl_id", "=", tmpl_id], ["attribute_id", "=", attr_id]],
        fields=["id", "value_ids"],
        limit=1,
    )
    target_ids = [value_ids["Adulto"], value_ids["Estudiante"], value_ids["Niño"]]
    if lines:
        client.write("product.template.attribute.line", [lines[0]["id"]], {"value_ids": [(6, 0, target_ids)]})
    else:
        client.create(
            "product.template.attribute.line",
            {
                "product_tmpl_id": tmpl_id,
                "attribute_id": attr_id,
                "value_ids": [(6, 0, target_ids)],
            },
        )


def configure_variant_prices(client: OdooClient, tmpl_id: int, value_ids: dict[str, int]) -> None:
    # Ajuste por valor de variante:
    # Niño = base 590 => extra 0
    # Estudiante = 620 => +30
    # Adulto = 670 => +80
    extras = {
        value_ids["Niño"]: 0.0,
        value_ids["Estudiante"]: PRICES["Estudiante"] - PRICES["Niño"],
        value_ids["Adulto"]: PRICES["Adulto"] - PRICES["Niño"],
    }

    ptavs = client.search_read(
        "product.template.attribute.value",
        domain=[["product_tmpl_id", "=", tmpl_id]],
        fields=["id", "product_attribute_value_id", "price_extra"],
        limit=100,
    )
    for ptav in ptavs:
        pav = ptav.get("product_attribute_value_id")
        if not isinstance(pav, list) or not pav:
            continue
        pav_id = pav[0]
        if pav_id in extras:
            client.write("product.template.attribute.value", [ptav["id"]], {"price_extra": extras[pav_id]})


def show_result(client: OdooClient, tmpl_id: int) -> None:
    variants = client.search_read(
        "product.product",
        domain=[["product_tmpl_id", "=", tmpl_id]],
        fields=["id", "display_name", "lst_price"],
        limit=20,
        order="id asc",
    )
    print("\n✅ Tour listo. Variantes y precios finales:")
    for v in variants:
        print(f"- {v['display_name']} | USD {v['lst_price']}")


def main() -> None:
    print("Creando/actualizando tour Camino Inca 2 días...")
    client = OdooClient()
    uid = client.connect()
    print(f"✅ Conectado (uid={uid})")

    categ_id = ensure_category(client)
    attr_id, value_ids = ensure_attribute_and_values(client)
    tmpl_id = ensure_product(client, categ_id)
    ensure_attribute_line(client, tmpl_id, attr_id, value_ids)
    configure_variant_prices(client, tmpl_id, value_ids)
    show_result(client, tmpl_id)
    print("\n🎉 Proceso completado.")


if __name__ == "__main__":
    main()
