#!/usr/bin/env python3
"""
Deja Odoo sin impuestos por defecto para Wayki Trek:
- Quita impuestos por defecto de venta/compra en la compañía.
- Limpia impuestos en productos existentes para evitar autocompletado.
"""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from odoo_cli import OdooClient


def remove_company_default_taxes(client: OdooClient) -> None:
    companies = client.search_read("res.company", domain=[], fields=["id", "name"], limit=50)
    for comp in companies:
        client.write(
            "res.company",
            [comp["id"]],
            {
                "account_sale_tax_id": False,
                "account_purchase_tax_id": False,
            },
        )
    print(f"✅ Impuestos por defecto removidos en {len(companies)} compañía(s).")


def clear_existing_product_taxes(client: OdooClient) -> None:
    products = client.execute(
        "product.template",
        "search_read",
        [],
        fields=["id", "name", "taxes_id", "supplier_taxes_id"],
        limit=10000,
        context={"active_test": False},
    )
    updated = 0
    for prod in products:
        if prod.get("taxes_id") or prod.get("supplier_taxes_id"):
            client.write(
                "product.template",
                [prod["id"]],
                {
                    "taxes_id": [(6, 0, [])],
                    "supplier_taxes_id": [(6, 0, [])],
                },
            )
            updated += 1
    print(f"✅ Productos limpiados (sin impuestos): {updated}")


def verify(client: OdooClient) -> None:
    companies = client.search_read(
        "res.company",
        domain=[],
        fields=["name", "account_sale_tax_id", "account_purchase_tax_id"],
        limit=50,
    )
    print("\nVerificación compañías:")
    for comp in companies:
        print(
            f"- {comp['name']} | sale_default={comp.get('account_sale_tax_id')} | "
            f"purchase_default={comp.get('account_purchase_tax_id')}"
        )


def main() -> None:
    print("Iniciando configuración sin impuestos por defecto...")
    client = OdooClient()
    uid = client.connect()
    print(f"✅ Conectado (uid={uid})")

    remove_company_default_taxes(client)
    clear_existing_product_taxes(client)
    verify(client)
    print("\n🎉 Configuración completada.")


if __name__ == "__main__":
    main()
