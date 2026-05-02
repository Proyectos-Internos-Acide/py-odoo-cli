#!/usr/bin/env python3
"""
Script único para crear el tour Camino Inca 2 días con precios FIJOS por variante.

Acciones:
- Elimina el tour previo (si existe).
- Lo vuelve a crear desde cero.
- Crea variantes: Adulto, Estudiante, Niño.
- Aplica precios fijos por variante mediante pricelist (no depende del precio base).
"""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from odoo_cli import OdooClient
from odoo_cli.exceptions import OdooFaultError


PRODUCT_NAME = "Camino Inca 2 días – Grupo Compartido"
PRICELIST_NAME = "Wayki Trek - Tarifas Fijas Tours (USD)"
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
                {"name": value_name, "attribute_id": attr_id},
            )
    return attr_id, value_ids


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
        {"name": PRICELIST_NAME, "currency_id": 1},
    )


def delete_previous_tour(client: OdooClient, pricelist_id: int) -> None:
    previous = client.search_read(
        "product.template",
        domain=[["name", "=", PRODUCT_NAME]],
        fields=["id"],
        limit=20,
    )
    if not previous:
        print("ℹ️ No había tour previo para eliminar.")
        return

    previous_tmpl_ids = [p["id"] for p in previous]
    previous_variants = client.search_read(
        "product.product",
        domain=[["product_tmpl_id", "in", previous_tmpl_ids]],
        fields=["id"],
        limit=200,
    )
    previous_variant_ids = [v["id"] for v in previous_variants]

    if previous_variant_ids:
        pl_items = client.search_read(
            "product.pricelist.item",
            domain=[["pricelist_id", "=", pricelist_id], ["product_id", "in", previous_variant_ids]],
            fields=["id"],
            limit=500,
        )
        if pl_items:
            client.unlink("product.pricelist.item", [x["id"] for x in pl_items])

    try:
        client.unlink("product.template", previous_tmpl_ids)
        print(f"✅ Tour previo eliminado: {len(previous_tmpl_ids)} plantilla(s).")
    except OdooFaultError:
        # Si hay referencias (ej. sale.order.line), Odoo no permite borrar.
        # Fallback: archivar y renombrar para dejar libre el nombre del tour nuevo.
        for tmpl_id in previous_tmpl_ids:
            client.write(
                "product.template",
                [tmpl_id],
                {
                    "active": False,
                    "name": f"{PRODUCT_NAME} [ARCHIVADO]",
                },
            )
        print(
            "⚠️ No se pudo eliminar por referencias históricas. "
            "Se archivó/renombró el tour previo y se continuará con recreación."
        )


def create_new_tour(client: OdooClient, categ_id: int, attr_id: int, value_ids: dict[str, int]) -> int:
    tmpl_id = client.create(
        "product.template",
        {
            "name": PRODUCT_NAME,
            "categ_id": categ_id,
            "type": "service",
            "sale_ok": True,
            "purchase_ok": False,
            "taxes_id": [(6, 0, [])],
            "supplier_taxes_id": [(6, 0, [])],
            "description_sale": DESCRIPTION,
            "list_price": PRICES["Adulto"],
        },
    )
    client.create(
        "product.template.attribute.line",
        {
            "product_tmpl_id": tmpl_id,
            "attribute_id": attr_id,
            "value_ids": [(6, 0, [value_ids["Adulto"], value_ids["Estudiante"], value_ids["Niño"]])],
        },
    )
    return tmpl_id


def apply_fixed_prices(client: OdooClient, tmpl_id: int, pricelist_id: int) -> None:
    variants = client.search_read(
        "product.product",
        domain=[["product_tmpl_id", "=", tmpl_id]],
        fields=["id", "display_name"],
        limit=20,
    )
    variant_map: dict[str, int] = {}
    for v in variants:
        dname = v.get("display_name", "")
        for label in PRICES:
            if f"({label})" in dname:
                variant_map[label] = v["id"]

    missing = [x for x in PRICES if x not in variant_map]
    if missing:
        raise RuntimeError(f"No se encontraron variantes esperadas: {missing}")

    for label, price in PRICES.items():
        client.create(
            "product.pricelist.item",
            {
                "pricelist_id": pricelist_id,
                "applied_on": "0_product_variant",
                "product_id": variant_map[label],
                "compute_price": "fixed",
                "fixed_price": price,
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


def show_result(client: OdooClient, tmpl_id: int, pricelist_id: int) -> None:
    variants = client.search_read(
        "product.product",
        domain=[["product_tmpl_id", "=", tmpl_id]],
        fields=["id", "display_name", "lst_price"],
        limit=20,
        order="id asc",
    )
    rules = client.search_read(
        "product.pricelist.item",
        domain=[["pricelist_id", "=", pricelist_id]],
        fields=["id", "product_id", "fixed_price"],
        limit=500,
    )
    print("\n✅ Tour recreado con precios fijos:")
    for v in variants:
        fixed = next(
            (
                r["fixed_price"]
                for r in rules
                if isinstance(r.get("product_id"), list) and r["product_id"][0] == v["id"]
            ),
            None,
        )
        print(f"- {v['display_name']} | lista={v['lst_price']} | fijo={fixed}")


def main() -> None:
    print("Recreando tour Camino Inca 2 días con precios fijos...")
    client = OdooClient()
    uid = client.connect()
    print(f"✅ Conectado (uid={uid})")

    categ_id = ensure_category(client)
    attr_id, value_ids = ensure_attribute_and_values(client)
    pricelist_id = get_or_create_pricelist(client)
    delete_previous_tour(client, pricelist_id)
    tmpl_id = create_new_tour(client, categ_id, attr_id, value_ids)
    apply_fixed_prices(client, tmpl_id, pricelist_id)
    set_default_pricelist(client, pricelist_id)
    show_result(client, tmpl_id, pricelist_id)
    print("\n🎉 Proceso completado.")


if __name__ == "__main__":
    main()
