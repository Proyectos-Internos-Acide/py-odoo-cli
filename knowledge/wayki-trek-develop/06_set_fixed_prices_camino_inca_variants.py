#!/usr/bin/env python3
"""
Configura precios FIJOS por variante para:
Camino Inca 2 días – Grupo Compartido

Objetivo:
- No depender del precio base + extras para calcular precios finales.
- Usar lista de precios con reglas fijas por variante.
"""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from odoo_cli import OdooClient


PRODUCT_NAME = "Camino Inca 2 días – Grupo Compartido"
PRICELIST_NAME = "Wayki Trek - Tarifas Fijas Tours (USD)"
TARGET_PRICES = {
    "Adulto": 670.0,
    "Estudiante": 620.0,
    "Niño": 590.0,
}


def get_template(client: OdooClient) -> int:
    tmpl = client.search_read(
        "product.template",
        domain=[["name", "=", PRODUCT_NAME]],
        fields=["id"],
        limit=1,
    )
    if not tmpl:
        raise RuntimeError(f"No existe el producto: {PRODUCT_NAME}")
    return tmpl[0]["id"]


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
        {
            "name": PRICELIST_NAME,
            "currency_id": 1,  # USD
        },
    )


def map_variants(client: OdooClient, tmpl_id: int) -> dict[str, int]:
    variants = client.search_read(
        "product.product",
        domain=[["product_tmpl_id", "=", tmpl_id]],
        fields=["id", "display_name"],
        limit=50,
    )
    mapping: dict[str, int] = {}
    for v in variants:
        name = v.get("display_name", "")
        for key in TARGET_PRICES:
            if f"({key})" in name:
                mapping[key] = v["id"]
    missing = [k for k in TARGET_PRICES if k not in mapping]
    if missing:
        raise RuntimeError(f"Faltan variantes en Odoo: {missing}")
    return mapping


def upsert_pricelist_items(client: OdooClient, pricelist_id: int, variant_ids: dict[str, int]) -> None:
    existing = client.search_read(
        "product.pricelist.item",
        domain=[["pricelist_id", "=", pricelist_id]],
        fields=["id", "product_id"],
        limit=500,
    )
    existing_by_variant = {}
    for item in existing:
        product_id = item.get("product_id")
        if isinstance(product_id, list) and product_id:
            existing_by_variant[product_id[0]] = item["id"]

    for passenger_type, price in TARGET_PRICES.items():
        variant_id = variant_ids[passenger_type]
        vals = {
            "pricelist_id": pricelist_id,
            "applied_on": "0_product_variant",
            "product_id": variant_id,
            "compute_price": "fixed",
            "fixed_price": price,
        }
        if variant_id in existing_by_variant:
            client.write("product.pricelist.item", [existing_by_variant[variant_id]], vals)
        else:
            client.create("product.pricelist.item", vals)


def set_default_pricelist(client: OdooClient, pricelist_id: int) -> None:
    companies = client.search_read("res.company", domain=[], fields=["id", "name"], limit=20)
    for comp in companies:
        cid = comp["id"]
        # Default para nuevos partners de la compañía
        client.execute("ir.default", "set", "res.partner", "property_product_pricelist", pricelist_id, False, cid, False)

    # Aplicar a contactos existentes para que nuevas cotizaciones tomen esta lista
    partners = client.search_read("res.partner", domain=[], fields=["id"], limit=10000)
    if partners:
        client.write("res.partner", [p["id"] for p in partners], {"property_product_pricelist": pricelist_id})


def main() -> None:
    print("Configurando precios fijos por variante...")
    client = OdooClient()
    uid = client.connect()
    print(f"✅ Conectado (uid={uid})")

    tmpl_id = get_template(client)
    pricelist_id = get_or_create_pricelist(client)
    variant_ids = map_variants(client, tmpl_id)
    upsert_pricelist_items(client, pricelist_id, variant_ids)
    set_default_pricelist(client, pricelist_id)

    print("\n✅ Configuración completada:")
    print(f"- Producto: {PRODUCT_NAME}")
    print(f"- Pricelist: {PRICELIST_NAME} (id={pricelist_id})")
    for k, v in TARGET_PRICES.items():
        print(f"  - {k}: USD {v}")


if __name__ == "__main__":
    main()
