#!/usr/bin/env python3
"""
Inspect all form views for sale.order to find where the list columns are defined
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

    # Check all form views for sale.order and find which one has a list/tree with product_uom_qty
    all_views = client.search_read(
        "ir.ui.view",
        [["model", "=", "sale.order"], ["type", "=", "form"]],
        ["id", "name", "inherit_id", "arch_db"]
    )
    print(f"Found {len(all_views)} views\n")
    for v in all_views:
        arch = v.get("arch_db", "") or ""
        if "<list" in arch and "product_uom_qty" in arch:
            print(f"*** ID: {v['id']} | {v['name']} has <list> with product_uom_qty ***")
            # find it
            idx = arch.find("product_uom_qty")
            snippet = arch[max(0, idx-400):idx+400]
            print(snippet)
            print("---")
        elif "product_uom_qty" in arch:
            print(f"ID: {v['id']} | {v['name']} has product_uom_qty (but not in <list>)")
        else:
            print(f"ID: {v['id']} | {v['name']} - no product_uom_qty")

if __name__ == "__main__":
    main()
