#!/usr/bin/env python3
"""
Find the embedded list view inside sale.order.form for order_line
The list widget uses sol_o2m - need to find which view that references
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

    # The order_line widget is sol_o2m - it probably uses a dedicated view ref
    # Let's look at the actual base view arch_db around "sol_o2m"
    base = client.search_read("ir.ui.view", [["id", "=", 1583]], ["arch_db"])
    arch = base[0]["arch_db"]
    
    idx = arch.find("sol_o2m")
    if idx >= 0:
        print("=== sol_o2m widget context ===")
        print(arch[max(0, idx-200):idx+600])
    
    # Also look for view_ref in the order_line field
    idx2 = arch.find("order_line")
    if idx2 >= 0:
        print("\n=== order_line field definition ===")
        print(arch[idx2:idx2+500])

    # Let's also check if there's a dedicated list view model=sale.order.line type=list that is the embedded one
    # Look for all list views for sale.order.line
    list_views = client.search_read(
        "ir.ui.view",
        [["model", "=", "sale.order.line"], ["type", "=", "list"]],
        ["id", "name", "inherit_id", "arch_db"]
    )
    print(f"\n\nFound {len(list_views)} list views for sale.order.line:")
    for v in list_views:
        print(f"\n--- ID: {v['id']} | {v['name']} | Inherit: {v['inherit_id']}")
        arch_v = v.get("arch_db", "") or ""
        # Show first 600 chars
        print(arch_v[:600])

if __name__ == "__main__":
    main()
