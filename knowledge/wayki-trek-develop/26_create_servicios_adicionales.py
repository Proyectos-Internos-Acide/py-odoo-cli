#!/usr/bin/env python3
"""
Crea/actualiza la categoría "Servicios adicionales" y sus productos.

Nota:
- Por una automatización global de productos, algunos precios de template pueden
  quedar en 0. Para evitarlo, este script también fija `lst_price` en variantes.
"""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from odoo_cli import OdooClient


CATEGORY_NAME = "Servicios adicionales"
PRODUCTS = [
    ("Alquiler de bolsa de dormir", 30.0),
    ("Ticket Huayna Picchu o Machu Picchu", 75.0),
    ("Alquiler bastones", 25.0),
    ("Carpa Privada en TT4D", 90.0),
    ("Upgrade Vistadome regular", 40.0),
    ("Upgrade Vistadome observatory", 60.0),
    ("Porter extra 8kg", 100.0),
    ("Porter extra 15kg", 180.0),
    ("Caballo de silla", 150.0),
    ("City tour", 15.0),
    ("Valle Sagrado", 28.0),
    ("Montaña de 7 colores", 55.0),
    ("Laguna de Humantay", 55.0),
    ("Habitación Simple", 100.0),
]


def ensure_category(client: OdooClient) -> int:
    category = client.search_read(
        "product.category",
        domain=[["name", "=", CATEGORY_NAME]],
        fields=["id"],
        limit=1,
    )
    if category:
        return category[0]["id"]
    return client.create("product.category", {"name": CATEGORY_NAME})


def create_or_update_products(client: OdooClient, category_id: int) -> tuple[int, int]:
    created = 0
    updated = 0

    for name, price in PRODUCTS:
        rec = client.search_read(
            "product.template",
            domain=[["name", "=", name]],
            fields=["id"],
            limit=1,
        )
        vals = {
            "name": name,
            "categ_id": category_id,
            "type": "service",
            "sale_ok": True,
            "purchase_ok": False,
            "taxes_id": [(6, 0, [])],
            "supplier_taxes_id": [(6, 0, [])],
            "list_price": float(price),
        }
        if rec:
            client.write("product.template", [rec[0]["id"]], vals)
            updated += 1
            tmpl_id = rec[0]["id"]
        else:
            tmpl_id = client.create("product.template", vals)
            created += 1

        # Asegura precio visible correcto en variantes
        variants = client.search_read(
            "product.product",
            domain=[["product_tmpl_id", "=", tmpl_id]],
            fields=["id"],
            limit=50,
        )
        if variants:
            client.write("product.product", [v["id"] for v in variants], {"lst_price": float(price)})

    return created, updated


def show_summary(client: OdooClient, category_id: int) -> None:
    products = client.search_read(
        "product.template",
        domain=[["categ_id", "=", category_id]],
        fields=["id", "name"],
        limit=500,
        order="name asc",
    )
    print(f"TOTAL_EN_CATEGORIA={len(products)}")
    for product in products:
        variant = client.search_read(
            "product.product",
            domain=[["product_tmpl_id", "=", product["id"]]],
            fields=["lst_price"],
            limit=1,
        )
        price = variant[0]["lst_price"] if variant else None
        print(f"- {product['name']} | USD {price}")


def main() -> None:
    print("Creando/actualizando Servicios adicionales...")
    client = OdooClient()
    uid = client.connect()
    print(f"✅ Conectado (uid={uid})")

    category_id = ensure_category(client)
    created, updated = create_or_update_products(client, category_id)
    print(f"✅ Categoría: {CATEGORY_NAME} (id={category_id})")
    print(f"✅ Productos creados: {created} | actualizados: {updated}")
    show_summary(client, category_id)
    print("\n🎉 Listo.")


if __name__ == "__main__":
    main()
