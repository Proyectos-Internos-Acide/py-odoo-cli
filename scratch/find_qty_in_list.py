#!/usr/bin/env python3
"""
Find which view actually defines the visible columns (price, qty) in sale.order order lines
"""
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

    # Look at ALL views (form + list) for sale.order AND sale.order.line that mention product_uom_qty in a list context
    all_views = client.search_read(
        "ir.ui.view",
        [["model", "in", ["sale.order", "sale.order.line"]], ["arch_db", "ilike", "product_uom_qty"]],
        ["id", "name", "model", "type", "arch_db", "inherit_id"]
    )
    print(f"Found {len(all_views)} views with product_uom_qty\n")
    for v in all_views:
        arch = v.get("arch_db", "") or ""
        # Look for it in a list context
        list_pos = arch.find("<list")
        qty_pos = arch.find("product_uom_qty")
        if list_pos >= 0 and qty_pos > list_pos:
            print(f"*** MODEL: {v['model']} | TYPE: {v['type']} | ID: {v['id']} | {v['name']} | Inherit: {v['inherit_id']}")
            snippet = arch[max(0, qty_pos-200):qty_pos+400]
            print(snippet)
            print("---")
        else:
            print(f"    MODEL: {v['model']} | TYPE: {v['type']} | ID: {v['id']} | {v['name']} (qty not in list)")

if __name__ == "__main__":
    main()
