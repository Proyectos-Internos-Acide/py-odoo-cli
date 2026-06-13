#!/usr/bin/env python3
"""
Find where product_uom_qty appears in the list context inside sale.order.form
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

    base = client.search_read("ir.ui.view", [["id", "=", 1583]], ["arch_db"])
    arch = base[0]["arch_db"]

    # Find where product_uom_qty appears INSIDE the list
    # search from the list tag
    list_idx = arch.find("<list")
    list_end_search = arch.find("</list>", list_idx)
    list_section = arch[list_idx:list_end_search+10]

    qty_idx = list_section.find("product_uom_qty")
    if qty_idx >= 0:
        print("=== product_uom_qty context in list ===")
        print(list_section[max(0, qty_idx-100):qty_idx+500])
    else:
        print("product_uom_qty NOT found inside the <list> tag!")
        print("List section (first 2000 chars):")
        print(list_section[:2000])

if __name__ == "__main__":
    main()
