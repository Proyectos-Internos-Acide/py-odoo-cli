#!/usr/bin/env python3
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from odoo_cli import OdooClient

def main():
    client = OdooClient()
    client.connect()
    print("Conectado a Odoo.\n")

    # 1. Show arch of our custom view (ID 1841)
    view = client.search_read("ir.ui.view", [["id", "=", 1841]], ["name", "arch_db", "inherit_id"])
    if view:
        print(f"=== Vista ID 1841: {view[0]['name']} ===")
        print(f"Inherit ID: {view[0]['inherit_id']}")
        print("Arch:")
        print(view[0]["arch_db"])
    else:
        print("Vista 1841 no encontrada.")

    # 2. Show the structure of the base sale.order.form view around order_line
    print("\n=== Buscando XPath en la vista base (sale.order.form ID 1583) ===")
    base = client.search_read("ir.ui.view", [["id", "=", 1583]], ["name", "arch_db"])
    if base:
        arch = base[0]["arch_db"]
        # Find product_uom_qty inside the list context
        idx = arch.find("product_uom_qty")
        if idx >= 0:
            snippet = arch[max(0, idx-300):idx+600]
            print(snippet)
        else:
            print("'product_uom_qty' not found in base view arch!")
            print(arch[:3000])

if __name__ == "__main__":
    main()
