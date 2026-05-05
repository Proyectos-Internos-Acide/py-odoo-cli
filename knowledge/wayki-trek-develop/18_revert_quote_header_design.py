#!/usr/bin/env python3
"""
Revierte la cabecera personalizada de cotización Wayki Trek.

Acción:
- Desactiva la vista QWeb custom si existe.
"""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from odoo_cli import OdooClient


VIEW_NAMES = [
    "wtk.sale.quote.header.custom",
    "wtk.external_layout.top_header.custom",
    "wtk.sale.quote.compact.spacing",
    "wtk.sale.quote.clean.table.unique.descriptions",
]


def main() -> None:
    print("Revirtiendo diseño de cabecera de cotización...")
    client = OdooClient()
    uid = client.connect()
    print(f"✅ Conectado (uid={uid})")

    existing = client.search_read(
        "ir.ui.view",
        domain=[["name", "in", VIEW_NAMES], ["type", "=", "qweb"]],
        fields=["id", "name", "active"],
        limit=20,
    )
    if not existing:
        print("ℹ️ No existen vistas personalizadas para revertir.")
        return

    client.write("ir.ui.view", [v["id"] for v in existing], {"active": False})
    print("✅ Vistas desactivadas:")
    for v in existing:
        print(f"- {v['name']} (id={v['id']})")
    print("Reversión completada.")


if __name__ == "__main__":
    main()
