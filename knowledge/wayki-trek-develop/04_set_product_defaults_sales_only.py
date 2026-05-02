#!/usr/bin/env python3
"""
Configura productos nuevos con:
- Ventas = True
- Compras = False
- Tipo de producto = Service
"""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from odoo_cli import OdooClient


def set_company_defaults(client: OdooClient) -> None:
    companies = client.search_read("res.company", domain=[], fields=["id", "name"], limit=50)
    for comp in companies:
        cid = comp["id"]
        client.execute("ir.default", "set", "product.template", "sale_ok", True, False, cid, False)
        client.execute("ir.default", "set", "product.template", "purchase_ok", False, False, cid, False)
        client.execute("ir.default", "set", "product.template", "type", "service", False, cid, False)
    print(f"✅ Defaults aplicados para {len(companies)} compañía(s).")


def verify_defaults(client: OdooClient) -> None:
    fields = client.search_read(
        "ir.model.fields",
        domain=[["model", "=", "product.template"], ["name", "in", ["sale_ok", "purchase_ok", "type"]]],
        fields=["id", "name"],
        limit=10,
    )
    field_ids = [f["id"] for f in fields]
    defaults = client.search_read(
        "ir.default",
        domain=[["field_id", "in", field_ids]],
        fields=["field_id", "json_value", "company_id", "user_id", "condition"],
        limit=50,
    )
    print("Verificación en ir.default:")
    for row in defaults:
        print(
            f"- field={row.get('field_id')} value={row.get('json_value')} "
            f"company={row.get('company_id')} user={row.get('user_id')}"
        )


def main() -> None:
    print("Configurando productos por defecto: solo ventas...")
    client = OdooClient()
    uid = client.connect()
    print(f"✅ Conectado (uid={uid})")

    set_company_defaults(client)
    verify_defaults(client)
    print("\n🎉 Listo: productos nuevos se crearán con Ventas=ON, Compras=OFF y Tipo=Service.")


if __name__ == "__main__":
    main()
